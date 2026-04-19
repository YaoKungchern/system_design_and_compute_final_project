# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt, Signal
from pid_widget import Ui_Form as PidUiForm
from config import *
from utils import read_json, write_json

class NewPidWidget(QWidget):
    close_signal = Signal()

    def __init__(self, rover, parent=None):
        super().__init__(parent)
        self.ui = PidUiForm()
        self.ui.setupUi(self)
        self.setWindowTitle("PID Parameter Tuning")
        self.setWindowModality(Qt.NonModal)

        # 小车通信实例
        self.rover = rover
        # PID控制器ID映射（界面文本→ID）
        self.controller_map = {
            "speed loop controller": 0,
            "position loop controller": 1
        }

        # 初始化控件
        self._init_widgets()

    def _init_widgets(self):
        """初始化控件"""
        # 绑定按钮事件
        self.ui.pid_info_read.clicked.connect(self._on_read_pid)
        self.ui.pid_info_write.clicked.connect(self._on_write_pid)
        self.ui.pid_info_save.clicked.connect(self._on_save_pid)
        self.ui.pid_info_load.clicked.connect(self._on_load_pid)

    def _get_pid_params(self):
        """获取界面输入的PID参数"""
        try:
            kp = self.ui.kp_Box.value()
            ki = self.ui.ki_box.value()
            kd = self.ui.kd_box.value()
            i_limit = self.ui.i_limit_val_box.value()
            o_limit = self.ui.o_limit_val_box.value()
            controller_id = self.controller_map[self.ui.comboBox.currentText()]
            return controller_id, kp, ki, kd, i_limit, o_limit
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Parameter get failed: {str(e)}")
            return None

    def _on_read_pid(self):
        """读取PID参数"""
        try:
            controller_id = self.controller_map[self.ui.comboBox.currentText()]
            self.rover.read_pid(controller_id)
            # 读取后更新界面（需等待下位机返回，这里简化，实际需结合状态监听）
            state = self.rover.get_state()
            self.ui.kp_Box.setValue(state.kp)
            self.ui.ki_box.setValue(state.ki)
            self.ui.kd_box.setValue(state.kd)
            self.ui.i_limit_val_box.setValue(state.i_limit)
            self.ui.o_limit_val_box.setValue(state.o_limit)
            QMessageBox.information(self, "Success", "PID parameter read successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Read failed: {str(e)}")

    def _on_write_pid(self):
        """写入PID参数"""
        params = self._get_pid_params()
        if not params:
            return
        try:
            self.rover.write_pid(*params)
            QMessageBox.information(self, "Success", "PID parameter written successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Write failed: {str(e)}")

    def _on_save_pid(self):
        """保存PID参数到JSON"""
        params = self._get_pid_params()
        if not params:
            return
        controller_id, kp, ki, kd, i_limit, o_limit = params
        controller_name = self.ui.comboBox.currentText()
        data = read_json(PID_CONFIG_PATH)
        data[controller_name] = {
            "kp": kp,
            "ki": ki,
            "kd": kd,
            "i_limit": i_limit,
            "o_limit": o_limit
        }
        if write_json(PID_CONFIG_PATH, data):
            QMessageBox.information(self, "Success", f"PID parameter saved to {PID_CONFIG_PATH}")
        else:
            QMessageBox.critical(self, "Error", "Save failed!")

    def _on_load_pid(self):
        """从JSON加载PID参数"""
        controller_name = self.ui.comboBox.currentText()
        data = read_json(PID_CONFIG_PATH)
        if controller_name not in data:
            QMessageBox.warning(self, "Warning", f"PID configuration for {controller_name} not found!")
            return
        try:
            params = data[controller_name]
            self.ui.kp_Box.setValue(params["kp"])
            self.ui.ki_box.setValue(params["ki"])
            self.ui.kd_box.setValue(params["kd"])
            self.ui.i_limit_val_box.setValue(params["i_limit"])
            self.ui.o_limit_val_box.setValue(params["o_limit"])
            QMessageBox.information(self, "Success", f"PID parameter loaded for {controller_name}!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Load failed: {str(e)}")

    def closeEvent(self, event):
        """关闭窗口"""
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