# -*- coding: utf-8 -*-
import os

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARUCO_CONFIG_PATH = os.path.join(BASE_DIR, "config_aruco.json")
PID_CONFIG_PATH = os.path.join(BASE_DIR, "config_pid.json")

# 手柄配置（根据实际手柄映射调整）
JOYSTICK_AXIS_MAP = {
    "x": 0,    # X轴对应手柄轴0
    "y": 1,    # Y轴对应手柄轴1
    "yaw": 2   # Yaw轴对应手柄轴2
}
JOYSTICK_DEAD_ZONE = 0.1  # 手柄死区
JOYSTICK_SEND_FREQ = 50    # 手柄指令发送频率(Hz)

# 状态监控配置
NAV_READ_FREQ = 10         # 导航信息读取频率(Hz)
ULTRASONIC_MAX_CACHE = 50  # 超声波最大缓存数
ULTRASONIC_POLAR_MAX = 5   # 极坐标超声波显示数
VELOCITY_PLOT_POINTS = 100 # 速度曲线显示点数

# 视觉识别配置
CAMERA_INDEX = 0           # USB摄像头索引
ARUCO_SEND_FREQ = 5        # ArUco位置重置频率(Hz)
YOLO_MODEL = "vision/best.pt"  # YOLO模型路径
ARUCO_DICT = "DICT_6X6_250"# ArUco字典类型
CALIBRATION_PATH = "vision\\camera_calib_params.npz"  # 摄像头标定文件路径

MAC_ADDRESS = "48:87:2D:82:0C:48"  # 小车MAC地址
