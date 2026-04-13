# -*- coding: utf-8 -*-
import json
import numpy as np
from config import *

def read_json(file_path: str) -> dict:
    """读取JSON文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"读取JSON失败: {e}")
        return {}

def write_json(file_path: str, data: dict) -> bool:
    """写入JSON文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"写入JSON失败: {e}")
        return False

def joystick_value_map(raw_val: float, min_out: float = -999.99, max_out: float = 999.99) -> float:
    """手柄原始值(-1~1)映射到控制值范围"""
    if abs(raw_val) < JOYSTICK_DEAD_ZONE:
        return 0.0
    return np.interp(raw_val, [-1, 1], [min_out, max_out])

def polar_to_cartesian(r: float, theta: float) -> tuple:
    """极坐标转笛卡尔坐标"""
    theta_rad = np.radians(theta)
    x = r * np.cos(theta_rad)
    y = r * np.sin(theta_rad)
    return x, y