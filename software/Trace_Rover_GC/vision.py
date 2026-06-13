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
    aruco_signal = Signal(int, tuple, tuple, tuple)  # (id, position, rotation, rover_world_pos)
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
        # 创建ArUco检测器（兼容OpenCV 4.x新API）
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        self.aruco_config = read_json(ARUCO_CONFIG_PATH)
        self.aruco_last_send = 0

        # yaw角滤波参数
        self.yaw_filter_alpha = 0.2  # EMA平滑系数，0-1之间，越小越平滑
        self.smoothed_yaw = None     # 平滑后的yaw角
        self.yaw_change_threshold = 0.3  # yaw角突变阈值（弧度），超过此值认为是异常跳变

    def _load_camera_calib(self):
        """Load camera calibration parameters"""
        calib_file = os.path.join(BASE_DIR, CALIBRATION_PATH)
        if os.path.exists(calib_file):
            try:
                with np.load(calib_file) as data:
                    data = np.load(calib_file)
                    self.camera_matrix = data['mtx']
                    self.dist_coeffs = data['dist']
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
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
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
                # 检查相机标定参数是否有效
                if self.camera_matrix is None or self.dist_coeffs is None:
                    print("Camera calibration parameters not available, skipping ArUco pose estimation")
                else:
                    # 使用新API进行检测
                    corners, ids, rejected = self.aruco_detector.detectMarkers(frame)
                    if ids is not None:
                        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                        
                        # ArUco标记的3D角点坐标（相对于标记中心）
                        marker_points = np.array([
                            [-MARKER_SIZE/2, -MARKER_SIZE/2, 0],
                            [MARKER_SIZE/2, -MARKER_SIZE/2, 0],
                            [MARKER_SIZE/2, MARKER_SIZE/2, 0],
                            [-MARKER_SIZE/2, MARKER_SIZE/2, 0]
                        ], dtype=np.float32)
                        
                        for i, aruco_id in enumerate(ids.flatten()):
                            # 使用solvePnP估计位姿
                            ret, rvec, tvec = cv2.solvePnP(
                                marker_points, corners[i],
                                self.camera_matrix, self.dist_coeffs
                            )
                            
                            if ret:
                                # 绘制坐标轴
                                cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs,
                                                  rvec, tvec, MARKER_SIZE)
                                
                                # 获取平移向量（单位：米）- 相机相对于ArUco码的位置
                                cam_tvec = tvec.flatten()  # [x, y, z]
                                
                                # 从旋转向量计算旋转矩阵 - 相机相对ArUco的旋转
                                cam_rot_mat, _ = cv2.Rodrigues(rvec)
                                
                                # 构建相机相对ArUco的齐次变换矩阵 T_aruco_cam
                                # 表示从相机坐标系到ArUco坐标系的变换
                                T_aruco_cam = np.eye(4)
                                T_aruco_cam[:3, :3] = cam_rot_mat
                                T_aruco_cam[:3, 3] = cam_tvec
                                
                                # 从旋转矩阵计算欧拉角（yaw, pitch, roll）
                                # 使用Z-Y-X顺序（航空航天惯例）
                                yaw = np.arctan2(cam_rot_mat[1, 0], cam_rot_mat[0, 0])
                                pitch = np.arctan2(-cam_rot_mat[2, 0], np.sqrt(cam_rot_mat[2, 1]**2 + cam_rot_mat[2, 2]**2))
                                roll = np.arctan2(cam_rot_mat[2, 1], cam_rot_mat[2, 2])
                                
                                # 转换为角度
                                yaw_deg = np.degrees(yaw)
                                pitch_deg = np.degrees(pitch)
                                roll_deg = np.degrees(roll)
                                
                                # 构建相机相对小车的变换矩阵 T_rover_cam
                                # CAMERA_POS = (x, y, yaw) 表示相机相对于小车中心的位置和偏航角
                                # pitch角 = 舵机角度 - 90度（舵机90度时水平向前）
                                servo_angle = self.rover.state.servo_angle if hasattr(self.rover.state, 'servo_angle') else 90.0
                                cam_yaw_rel = np.radians(CAMERA_POS[2])  # 相机相对小车的yaw角
                                cam_pitch_rel = np.radians(servo_angle - 90.0)  # 相机相对小车的pitch角
                                cam_roll_rel = 0.0  # roll角与小车相同
                                
                                # 构建相机相对小车的旋转矩阵（Z-Y-X顺序）
                                cos_yaw, sin_yaw = np.cos(cam_yaw_rel), np.sin(cam_yaw_rel)
                                cos_pitch, sin_pitch = np.cos(cam_pitch_rel), np.sin(cam_pitch_rel)
                                cos_roll, sin_roll = np.cos(cam_roll_rel), np.sin(cam_roll_rel)
                                
                                R_rover_cam = np.array([
                                    [cos_yaw*cos_pitch, cos_yaw*sin_pitch*sin_roll - sin_yaw*cos_roll, cos_yaw*sin_pitch*cos_roll + sin_yaw*sin_roll],
                                    [sin_yaw*cos_pitch, sin_yaw*sin_pitch*sin_roll + cos_yaw*cos_roll, sin_yaw*sin_pitch*cos_roll - cos_yaw*sin_roll],
                                    [-sin_pitch, cos_pitch*sin_roll, cos_pitch*cos_roll]
                                ])
                                
                                # 相机相对小车的位置偏移
                                t_rover_cam = np.array([-CAMERA_POS[0], CAMERA_POS[1], -CAMERA_POS[2]])
                                
                                # 构建齐次变换矩阵
                                T_rover_cam = np.eye(4)
                                T_rover_cam[:3, :3] = R_rover_cam
                                T_rover_cam[:3, 3] = t_rover_cam
                                
                                # ArUco码立起来时的坐标变换（使用增广矩阵）
                                # 关键理解：
                                # - ArUco的pitch角 = 小车视角下的yaw角
                                # - 舵机角度控制摄像头在小车坐标系的pitch角，影响roll角对坐标的影响
                                
                                # 获取相机相对ArUco的位置（单位：米）
                                cam_x = float(tvec[0].item()) if hasattr(tvec[0], 'item') else float(tvec[0])
                                cam_y = float(tvec[1].item()) if hasattr(tvec[1], 'item') else float(tvec[1])
                                cam_z = float(tvec[2].item()) if hasattr(tvec[2], 'item') else float(tvec[2])
                                
                                # 从旋转向量计算旋转矩阵
                                cam_rot_mat, _ = cv2.Rodrigues(rvec)
                                
                                # 从旋转矩阵计算相机的欧拉角（Z-Y-X顺序）
                                # - yaw: 绕Z轴旋转
                                # - pitch: 绕Y轴旋转（对于立起来的ArUco，这对应小车的yaw角）
                                # - roll: 绕X轴旋转
                                cam_yaw = np.arctan2(cam_rot_mat[1, 0], cam_rot_mat[0, 0])
                                cam_pitch = np.arctan2(-cam_rot_mat[2, 0], np.sqrt(cam_rot_mat[2, 1]**2 + cam_rot_mat[2, 2]**2))
                                cam_roll = np.arctan2(cam_rot_mat[2, 1], cam_rot_mat[2, 2])
                                
                                # 获取舵机角度（控制摄像头俯仰角）
                                servo_angle = self.rover.state.servo_angle if hasattr(self.rover.state, 'servo_angle') else 90.0
                                servo_pitch = np.radians(servo_angle - 90.0)  # 舵机引起的俯仰角
                                
                                # 小车相对ArUco的yaw角 = ArUco的pitch角
                                # 这是关键：立起来的ArUco码，pitch角对应水平面内的旋转
                                rover_rel_yaw = cam_pitch
                                
                                # 相机相对小车的位置偏移
                                offset_x = -CAMERA_POS[0]
                                offset_y = -CAMERA_POS[1]
                                cam_yaw_offset = np.radians(CAMERA_POS[2])  # 相机相对小车的yaw角偏移
                                
                                # 构建二维坐标变换矩阵
                                # 考虑舵机俯仰角对roll的影响：当摄像头俯仰时，需要补偿roll角带来的坐标偏移
                                # 当舵机角度不为90度时，相机看到的roll角会影响x-z平面的坐标
                                
                                # 补偿舵机角度引起的投影效应
                                # 小车y轴向前，当摄像头俯仰时，相机z轴（深度）会投影到小车y轴
                                # 使用旋转矩阵将相机坐标转换到小车坐标系
                                # 绕X轴旋转servo_pitch角（俯仰）
                                cos_pitch = np.cos(servo_pitch)
                                sin_pitch = np.sin(servo_pitch)
                                
                                # 相机坐标 -> 小车坐标的投影变换
                                # 小车y轴向前，相机z轴投影到小车y轴
                                rover_x_from_cam = cam_x
                                rover_y_from_cam = cam_z * cos_pitch + cam_y * sin_pitch
                                
                                # 考虑相机相对小车的位置偏移和yaw角偏移
                                cos_yaw_off = np.cos(cam_yaw_offset)
                                sin_yaw_off = np.sin(cam_yaw_offset)
                                
                                # 最终小车相对ArUco的位置（经过yaw偏移修正）
                                rover_rel_x = (rover_x_from_cam - offset_x) * cos_yaw_off - (rover_y_from_cam - offset_y) * sin_yaw_off
                                rover_rel_y = (rover_x_from_cam - offset_x) * sin_yaw_off + (rover_y_from_cam - offset_y) * cos_yaw_off
                                
                                rover_rel_yaw = rover_rel_yaw * MARKER_SIZE
                                
                                rover_rel_x = rover_rel_x * MARKER_SIZE
                                
                                # print(f"rover_rel: ({rover_rel_x}, {rover_rel_y}, {rover_rel_yaw})")
                                
                                
                                # 计算小车的世界坐标 (x, y, yaw)
                                rover_world_pos = None
                                if str(aruco_id) in self.aruco_config:
                                    aruco_world = self.aruco_config[str(aruco_id)]
                                    aruco_world_x = aruco_world[0]
                                    aruco_world_y = aruco_world[1]
                                    aruco_world_yaw = np.radians(aruco_world[2]) if len(aruco_world) > 2 else 0.0
                                    
                                    rover_world_x = float(aruco_world_x +  rover_rel_x * np.cos(aruco_world_yaw) - rover_rel_y * np.sin(aruco_world_yaw))
                                    rover_world_y = float(aruco_world_y + rover_rel_y * np.cos(aruco_world_yaw) + rover_rel_x * np.sin(aruco_world_yaw))
                                    
                                    raw_yaw = float(aruco_world_yaw + rover_rel_yaw)
                                    
                                    # rover_world_x = rover_world_x*np.cos(-raw_yaw) - rover_world_y*np.sin(-raw_yaw)
                                    # rover_world_y = rover_world_x*np.sin(-raw_yaw) + rover_world_y*np.cos(-raw_yaw)
                                    
                                    # EMA滤波处理yaw角
                                    if self.smoothed_yaw is None:
                                        self.smoothed_yaw = raw_yaw
                                    else:
                                        # 检查是否发生异常跳变
                                        yaw_diff = abs(raw_yaw - self.smoothed_yaw)
                                        # 处理角度环绕问题（-π到π）
                                        if yaw_diff > np.pi:
                                            yaw_diff = 2 * np.pi - yaw_diff
                                        
                                        if yaw_diff < self.yaw_change_threshold:
                                            # 使用EMA滤波
                                            self.smoothed_yaw = self.yaw_filter_alpha * raw_yaw + (1 - self.yaw_filter_alpha) * self.smoothed_yaw
                                        else:
                                            # 发生跳变，缓慢跟随
                                            self.smoothed_yaw = 0.1 * raw_yaw + 0.9 * self.smoothed_yaw
                                            # print(f"Yaw jump detected: {np.degrees(raw_yaw):.1f} -> {np.degrees(self.smoothed_yaw):.1f}")
                                    
                                    rover_world_pos = (-rover_world_x, -rover_world_y, self.smoothed_yaw)
                                    
                                    # 定时发送小车世界坐标给导航系统
                                    now = time.time()
                                    if now - self.aruco_last_send > 1.0 / ARUCO_SEND_FREQ:
                                        if abs(rover_world_pos[2])>0.05:
                                            self.rover.write_nav(4, rover_world_pos)
                                        else:
                                            self.rover.write_nav(7, rover_world_pos)
                                        self.aruco_last_send = now
                                
                                # 发送ArUco检测信号（包含位置和角度信息，以及小车世界坐标）
                                self.aruco_signal.emit(aruco_id, (float(cam_tvec[0]), float(cam_tvec[1]), float(cam_tvec[2])), 
                                                       (float(yaw_deg), float(pitch_deg), float(roll_deg)),
                                                       rover_world_pos)

            # 发送帧数据
            self.frame_signal.emit(frame)
            time.sleep(0.02)

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
        # 连接ArUco信号（支持新的角度参数）
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

    @Slot(int, tuple, tuple, tuple)
    def _on_aruco_detected(self, aruco_id, pos, rot, rover_world_pos):
        """ArUco detection callback"""
        # Update ArUco information display
        world_pos_text = "N/A" if rover_world_pos is None else f"({rover_world_pos[0]:.3f}, {rover_world_pos[1]:.3f}, {rover_world_pos[2]:.3f})"
        self.aruco_info.setText(
            f"Detected ArUco ID: {aruco_id}\n"
            f"Camera Position: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})\n"
            f"Rotation: Yaw={rot[0]:.1f}, Pitch={rot[1]:.1f}, Roll={rot[2]:.1f}\n"
            f"Rover World Pos: {world_pos_text}"
        )
        
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

'''__||_____||__
   __||_____||__
   ___\\___//___
   _===========_
   _____|||_____
   _____|||_____
   ______|______
   ___防伪专用___'''