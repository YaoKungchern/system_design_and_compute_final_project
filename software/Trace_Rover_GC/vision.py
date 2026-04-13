# -*- coding: utf-8 -*-
import cv2
import threading
import time
import numpy as np
from ultralytics import YOLO
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
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

    def __init__(self, rover):
        super().__init__()
        self.rover = rover
        self.camera = None
        self.running = False
        self.yolo_enabled = False
        self.aruco_enabled = False

        # YOLO模型（CUDA加速）
        self.yolo_model = YOLO(YOLO_MODEL)
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            self.yolo_model.to("cuda")
            print("YOLO enabled with CUDA acceleration.")
        else:
            print("CUDA not available, using CPU for YOLO.")

        # ArUco配置
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_MAP[ARUCO_DICT])
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_config = read_json(ARUCO_CONFIG_PATH)
        self.aruco_last_send = 0

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

            # YOLO识别
            if self.yolo_enabled:
                results = self.yolo_model(frame, verbose=False)
                frame = results[0].plot()

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
        self.setMinimumSize(800, 600)

        # 小车通信实例
        self.rover = rover

        # 初始化UI
        self._init_ui()

        # 视觉处理线程
        self.vision_worker = VisionWorker(rover)
        self.vision_worker.frame_signal.connect(self._update_frame)
        self.vision_worker.aruco_signal.connect(self._on_aruco_detected)
        self.vision_worker.start()

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)

        # 视频显示标签
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.video_label)

        # 控制按钮
        btn_layout = QHBoxLayout()
        self.yolo_btn = QPushButton("YOLO Recognition")
        self.aruco_btn = QPushButton("ArUco Recognition")
        self.yolo_btn.clicked.connect(self._toggle_yolo)
        self.aruco_btn.clicked.connect(self._toggle_aruco)
        btn_layout.addWidget(self.yolo_btn)
        btn_layout.addWidget(self.aruco_btn)
        main_layout.addLayout(btn_layout)

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

    @Slot(int, tuple)
    def _on_aruco_detected(self, aruco_id, pos):
        """ArUco识别回调"""
        print(f"Detected ArUco ID: {aruco_id}, Position: {pos}")

    def _toggle_yolo(self):
        """切换YOLO识别"""
        self.vision_worker.yolo_enabled = not self.vision_worker.yolo_enabled
        self.yolo_btn.setText("YOLO Recognition" if self.vision_worker.yolo_enabled else "YOLO Recognition")

    def _toggle_aruco(self):
        """切换ArUco识别"""
        self.vision_worker.aruco_enabled = not self.vision_worker.aruco_enabled
        self.aruco_btn.setText("ArUco Recognition" if self.vision_worker.aruco_enabled else "ArUco Recognition")

    def closeEvent(self, event):
        """关闭窗口"""
        self.vision_worker.stop()
        self.close_signal.emit()
        event.accept()