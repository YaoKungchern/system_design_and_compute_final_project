# -*- coding: utf-8 -*-
import cv2
import threading
import time
import numpy as np
from ultralytics import YOLO
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDoubleSpinBox
from PySide6.QtCore import Qt, Signal, QTimer, QThread, Slot
from PySide6.QtGui import QImage, QPixmap
from config import *
from utils import read_json

# ArUco字典映射
ARUCO_DICT_MAP = {
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250
}

class VisionWorker(QThread):
    frame_signal = Signal(np.ndarray)
    aruco_signal = Signal(int, tuple)
    yolo_signal = Signal(int, int, int)

    def __init__(self, rover):
        super().__init__()
        self.rover = rover
        self.camera = None
        self.running = False
        self.yolo_enabled = False
        self.aruco_enabled = False

        # 相机标定参数
        self.camera_matrix = None
        self.dist_coeffs = None
        self._load_camera_calib()

        # YOLO模型（CUDA加速）
        self.yolo_model = YOLO(YOLO_MODEL)
        import torch
        if torch.cuda.is_available():
            self.yolo_model.to("cuda")
            print(f"YOLO enabled with CUDA acceleration on GPU {torch.cuda.get_device_name(0)}.")
        else:
            print("CUDA not available, using CPU for YOLO.")

        # ArUco配置
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_MAP[ARUCO_DICT])
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_config = read_json(ARUCO_CONFIG_PATH)
        self.aruco_last_send = 0

    def _load_camera_calib(self):
        """Load camera calibration parameters"""
        calib_file = os.path.join(BASE_DIR, "camera_calib_params.npz")
        if os.path.exists(calib_file):
            try:
                with np.load(calib_file) as data:
                    self.camera_matrix = data['camera_matrix']
                    self.dist_coeffs = data['dist_coeffs']
                print("Camera calibration parameters loaded successfully")
            except Exception as e:
                print(f"Failed to load camera calibration parameters: {e}")
                self.camera_matrix = None
                self.dist_coeffs = None
        else:
            print("Camera calibration parameters file not found, using default parameters")
            # Use default parameters
            self.camera_matrix = np.array([[640, 0, 320], [0, 640, 240], [0, 0, 1]], dtype=np.float32)
            self.dist_coeffs = np.zeros((5, 1), dtype=np.float32)

    def run(self):
        """摄像头采集线程"""
        self.camera = cv2.VideoCapture(CAMERA_INDEX)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True

        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                continue

            # 去畸变处理
            if self.camera_matrix is not None and self.dist_coeffs is not None:
                frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs)

            # YOLO识别
            if self.yolo_enabled:
                results = self.yolo_model(frame, verbose=False)
                frame = results[0].plot()
                # 统计YOLO结果
                total = 0
                with_helmet = 0
                no_helmet = 0
                for result in results:
                    for box in result.boxes:
                        if box.conf > 0.6:
                            total += 1
                            # 打印类别信息以便调试
                            print(f"Detected class: {box.cls}, confidence: {box.conf}")
                            # 假设0是with_helmet，1是no_helmet
                            if int(box.cls) == 0:
                                with_helmet += 1
                            elif int(box.cls) == 1:
                                no_helmet += 1
                print(f"YOLO stats: total={total}, with_helmet={with_helmet}, no_helmet={no_helmet}")
                self.yolo_signal.emit(total, with_helmet, no_helmet)

            # ArUco识别
            if self.aruco_enabled:
                corners, ids, rejected = cv2.aruco.detectMarkers(frame, self.aruco_dict, parameters=self.aruco_params)
                if ids is not None:
                    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                    for i, aruco_id in enumerate(ids.flatten()):
                        if str(aruco_id) in self.aruco_config:
                            pos = self.aruco_config[str(aruco_id)]
                            self.aruco_signal.emit(aruco_id, pos)
                            # 定时发送位置重置指令
                            now = time.time()
                            if now - self.aruco_last_send > 1.0 / ARUCO_SEND_FREQ:
                                self.rover.write_nav(pos)
                                self.aruco_last_send = now

            # 发送帧数据
            self.frame_signal.emit(frame)
            time.sleep(0.01)

    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()
        if self.camera:
            self.camera.release()

class VisionWidget(QWidget):
    close_signal = Signal()

    def __init__(self, rover, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vision Widget")
        self.setMinimumSize(1000, 600)

        # 小车通信实例
        self.rover = rover

        # 初始化UI
        self._init_ui()

        # 视觉处理线程
        self.vision_worker = VisionWorker(rover)
        self.vision_worker.frame_signal.connect(self._update_frame)
        self.vision_worker.aruco_signal.connect(self._on_aruco_detected)
        self.vision_worker.yolo_signal.connect(self._on_yolo_detected)
        self.vision_worker.start()

    def _init_ui(self):
        """Initialize UI"""
        main_layout = QHBoxLayout(self)

        # Left side: Video display
        left_layout = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.video_label)

        # Control buttons
        btn_layout = QHBoxLayout()
        self.yolo_btn = QPushButton("YOLO Recognition")
        self.aruco_btn = QPushButton("ArUco Recognition")
        self.yolo_btn.clicked.connect(self._toggle_yolo)
        self.aruco_btn.clicked.connect(self._toggle_aruco)
        btn_layout.addWidget(self.yolo_btn)
        btn_layout.addWidget(self.aruco_btn)
        left_layout.addLayout(btn_layout)
        main_layout.addLayout(left_layout, 2)

        # Right side: Control and information display
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        # 1. Servo control unit
        servo_group = QWidget()
        servo_group.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px;")
        servo_layout = QVBoxLayout(servo_group)
        servo_layout.setSpacing(10)
        servo_layout.addWidget(QLabel("Servo Control"))
        self.servo_input = QDoubleSpinBox()
        self.servo_input.setRange(0, 180)
        self.servo_input.setSingleStep(1)
        self.servo_input.setValue(90)
        servo_layout.addWidget(self.servo_input)
        self.servo_btn = QPushButton("Write")
        self.servo_btn.clicked.connect(self._write_servo)
        servo_layout.addWidget(self.servo_btn)
        right_layout.addWidget(servo_group)

        # 2. YOLO information display unit
        yolo_group = QWidget()
        yolo_group.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px;")
        yolo_layout = QVBoxLayout(yolo_group)
        yolo_layout.setSpacing(10)
        yolo_layout.addWidget(QLabel("YOLO Information"))
        self.yolo_info = QLabel("Total 0 people in view, \n0 wearing helmet, \n0 not wearing helmet")
        self.yolo_info.setWordWrap(True)
        yolo_layout.addWidget(self.yolo_info)
        right_layout.addWidget(yolo_group)

        # 3. ArUco code feedback unit
        aruco_group = QWidget()
        aruco_group.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px;")
        aruco_layout = QVBoxLayout(aruco_group)
        aruco_layout.setSpacing(10)
        aruco_layout.addWidget(QLabel("ArUco Feedback"))
        self.aruco_info = QLabel("No ArUco code detected")
        self.aruco_info.setWordWrap(True)
        aruco_layout.addWidget(self.aruco_info)
        right_layout.addWidget(aruco_group)

        main_layout.addLayout(right_layout, 1)

    @Slot(np.ndarray)
    def _update_frame(self, frame):
        """更新视频帧"""
        # BGR转RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def _write_servo(self):
        """Write servo angle"""
        angle = self.servo_input.value()
        self.rover.write_servo(angle)
        print(f"Sent servo angle: {angle}")

    @Slot(int, tuple)
    def _on_aruco_detected(self, aruco_id, pos):
        """ArUco detection callback"""
        print(f"Detected ArUco ID: {aruco_id}, Position: {pos}")
        # Update ArUco information display
        self.aruco_info.setText(f"Detected ArUco ID: {aruco_id}\nRover position: ({pos[0]}, {pos[1]}, {pos[2]})")

    @Slot(int, int, int)
    def _on_yolo_detected(self, total, with_helmet, no_helmet):
        """YOLO detection callback"""
        # Update YOLO information display
        self.yolo_info.setText(f"Total {total} people in view,\n{with_helmet} wearing helmet, \n{no_helmet} not wearing helmet")
        
    def _toggle_yolo(self):
        """Toggle YOLO recognition"""
        self.vision_worker.yolo_enabled = not self.vision_worker.yolo_enabled
        if self.vision_worker.yolo_enabled:
            self.yolo_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.yolo_btn.setStyleSheet("")

    def _toggle_aruco(self):
        """Toggle ArUco recognition"""
        self.vision_worker.aruco_enabled = not self.vision_worker.aruco_enabled
        if self.vision_worker.aruco_enabled:
            self.aruco_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.aruco_btn.setStyleSheet("")

    def closeEvent(self, event):
        """关闭窗口"""
        self.vision_worker.stop()
        self.close_signal.emit()
        event.accept()