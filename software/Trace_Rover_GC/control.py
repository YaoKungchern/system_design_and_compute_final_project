# -*- coding: utf-8 -*-
import pygame
import threading
import time
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt, Signal, QTimer
from control_widget import Ui_Form as ControlUiForm
from config import *
from utils import joystick_value_map

class NewControlWidget(QWidget):
    close_signal = Signal()

    def __init__(self, rover, parent=None):
        super().__init__(parent)
        self.ui = ControlUiForm()
        self.ui.setupUi(self)
        self.setWindowTitle("Motion Control")
        self.setWindowModality(Qt.NonModal)

        # 小车通信实例
        self.rover = rover
        # 手柄相关
        self.joystick = None
        self.joystick_thread = None
        self.joystick_running = False
        # 控制模式映射（界面文本→指令码）
        self.control_mode_map = {
            "openloop control": 0x00,
            "speed closedloop control under robot base": 0x01,
            "speed closedloop control under world base": 0x02,
            "position closedloop control under robot base": 0x03,
            "position closedloop control under world base": 0x04
        }

        # 初始化
        self._init_widgets()

    def _init_widgets(self):
        """初始化控件"""
        # 模式切换
        self.ui.mode_box.currentTextChanged.connect(self._on_mode_change)
        # 写入按钮
        self.ui.control_set_button.clicked.connect(self._on_manual_write)

        # 初始禁用手柄模式（默认手动）
        self._on_mode_change(self.ui.mode_box.currentText())

    def _on_mode_change(self, mode_text):
        """模式切换：手动/手柄"""
        if mode_text == "manul mode":
            # 手动模式：启用输入框和按钮，停止手柄线程
            self._stop_joystick()
            self.ui.x_box.setEnabled(True)
            self.ui.y_box.setEnabled(True)
            self.ui.yaw_box.setEnabled(True)
            self.ui.control_set_button.setEnabled(True)
        elif mode_text == "controller mode":
            # 手柄模式：禁用输入框和按钮，启动手柄线程
            self._start_joystick()
            self.ui.x_box.setEnabled(False)
            self.ui.y_box.setEnabled(False)
            self.ui.yaw_box.setEnabled(False)
            self.ui.control_set_button.setEnabled(False)

    def _start_joystick(self):
        """启动手柄监听线程"""
        if self.joystick_running:
            return
        try:
            pygame.init()
            pygame.joystick.init()
            if pygame.joystick.get_count() == 0:
                QMessageBox.warning(self, "Warning", "No joystick detected!")
                self.ui.mode_box.setCurrentText("manul mode")
                return
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_running = True
            self.joystick_thread = threading.Thread(target=self._joystick_loop, daemon=True)
            self.joystick_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Joystick initialization failed: {str(e)}")
            self.ui.mode_box.setCurrentText("manul mode")

    def _stop_joystick(self):
        """停止手柄线程"""
        self.joystick_running = False
        if self.joystick_thread:
            self.joystick_thread.join(timeout=1)
        if self.joystick:
            self.joystick.quit()
            self.joystick = None
        pygame.joystick.quit()

    def _joystick_loop(self):
        """手柄数据读取循环"""
        interval = 1.0 / JOYSTICK_SEND_FREQ
        while self.joystick_running:
            try:
                pygame.event.pump()
                # 读取手柄轴值并映射
                x_val = joystick_value_map(self.joystick.get_axis(JOYSTICK_AXIS_MAP["x"]), min_out=-0.6, max_out=0.6)
                y_val = joystick_value_map(self.joystick.get_axis(JOYSTICK_AXIS_MAP["y"]), min_out=1.0, max_out=-1.0)
                yaw_val = joystick_value_map(self.joystick.get_axis(JOYSTICK_AXIS_MAP["yaw"]), min_out=6.0, max_out=-6.0)

                # 更新UI（线程安全）
                self.ui.x_box.setValue(x_val)
                self.ui.y_box.setValue(y_val)
                self.ui.yaw_box.setValue(yaw_val)

                # 发送控制指令
                control_mode = self.control_mode_map[self.ui.control_mode_box.currentText()]
                self.rover.write_control(control_mode, [x_val, y_val, yaw_val])

                time.sleep(interval)
            except Exception as e:
                print(f"Joystick thread error: {e}")
                break

    def _on_manual_write(self):
        """手动模式写入控制指令"""
        try:
            # 获取输入值
            x_val = self.ui.x_box.value()
            y_val = self.ui.y_box.value()
            yaw_val = self.ui.yaw_box.value()
            # 获取控制模式
            control_mode_text = self.ui.control_mode_box.currentText()
            control_mode = self.control_mode_map.get(control_mode_text, 0)
            # 发送指令
            self.rover.write_control(control_mode, [x_val, y_val, yaw_val])
            QMessageBox.information(self, "Success", "Control command sent successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Send failed: {str(e)}")

    def closeEvent(self, event):
        """关闭窗口清理资源"""
        self._stop_joystick()
        self.close_signal.emit()
        event.accept()