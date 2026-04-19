# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt, Signal
from main_widget import Ui_Form as MainUiForm
from trace_rover_comm import trace_rover
from control import NewControlWidget
from pid import NewPidWidget
from navigation import StateMonitorWidget
from vision import VisionWidget
from config import MAC_ADDRESS

class NewMainWidget(QWidget):
    # 定义信号：设备连接状态变化
    conn_state_changed = Signal(bool, trace_rover)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = MainUiForm()
        self.ui.setupUi(self)
        self.setWindowTitle("Trace Rover Ground Control Software")
        self.ui.mac_line.setText(MAC_ADDRESS)

        # 初始化子窗口实例（单例）
        self.control_widget = None
        self.pid_widget = None
        self.state_widget = None
        self.vision_widget = None

        # 小车通信实例
        self.rover = None
        self.is_connected = False

        # 初始化控件
        self._init_widgets()

    def _init_widgets(self):
        """初始化控件逻辑"""
        # 设备连接/断开按钮
        self.ui.connect_button.clicked.connect(self._on_connect)
        self.ui.disconnect_button.clicked.connect(self._on_disconnect)
        self.ui.disconnect_button.setEnabled(False)

        # 功能模块按钮
        self.ui.control_button.clicked.connect(self._open_control_widget)
        self.ui.vision_button.clicked.connect(self._open_vision_widget)
        self.ui.navigation_button.clicked.connect(self._open_state_widget)
        self.ui.pid_button.clicked.connect(self._open_pid_widget)

        # 初始状态
        self.ui.connect_state.setText("unconnected")

    def _on_connect(self):
        """连接小车"""
        mac_addr = self.ui.mac_line.text().strip()
        if not mac_addr:
            QMessageBox.warning(self, "Warning", "Please select or input MAC address!")
            return

        try:
            self.rover = trace_rover(mac_addr)
            self.is_connected = True
            self.ui.connect_state.setText("connected")
            self.ui.connect_button.setEnabled(False)
            self.ui.disconnect_button.setEnabled(True)
            self.conn_state_changed.emit(True, self.rover)
            QMessageBox.information(self, "Success", f"Connected to: {mac_addr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")

    def _on_disconnect(self):
        """断开连接"""
        if self.rover:
            self.rover.close()
            self.rover = None
        self.is_connected = False
        self.ui.connect_state.setText("unconnected")
        self.ui.connect_button.setEnabled(True)
        self.ui.disconnect_button.setEnabled(False)
        self.conn_state_changed.emit(False, None)

        # 关闭所有子窗口
        self._close_all_sub_widgets()

    def _open_control_widget(self):
        """打开运动控制窗口（单例）"""
        if not self.is_connected:
            QMessageBox.warning(self, "Warning", "Please connect to the rover first!")
            return
        if not self.control_widget:
            self.control_widget = NewControlWidget(self.rover, None)
            self.control_widget.close_signal.connect(lambda: setattr(self, "control_widget", None))
        self.control_widget.show()
        self.control_widget.raise_()

    def _open_vision_widget(self):
        """打开视觉识别窗口（单例）"""
        if not self.is_connected:
            QMessageBox.warning(self, "Warning", "Please connect to the rover first!")
            return
        if not self.vision_widget:
            self.vision_widget = VisionWidget(self.rover, None)
            self.vision_widget.close_signal.connect(lambda: setattr(self, "vision_widget", None))
        self.vision_widget.show()
        self.vision_widget.raise_()

    def _open_state_widget(self):
        """打开状态监控窗口（单例）"""
        if not self.is_connected:
            QMessageBox.warning(self, "Warning", "Please connect to the rover first!")
            return
        if not self.state_widget:
            self.state_widget = StateMonitorWidget(self.rover, None)
            self.state_widget.close_signal.connect(lambda: setattr(self, "state_widget", None))
        self.state_widget.show()
        self.state_widget.raise_()

    def _open_pid_widget(self):
        """打开PID调参窗口（单例）"""
        if not self.is_connected:
            QMessageBox.warning(self, "Warning", "Please connect to the rover first!")
            return
        if not self.pid_widget:
            self.pid_widget = NewPidWidget(self.rover, None)
            self.pid_widget.close_signal.connect(lambda: setattr(self, "pid_widget", None))
        self.pid_widget.show()
        self.pid_widget.raise_()

    def _close_all_sub_widgets(self):
        """关闭所有子窗口"""
        for widget in [self.control_widget, self.pid_widget, self.state_widget, self.vision_widget]:
            if widget:
                widget.close()

    def closeEvent(self, event):
        """关闭主窗口时清理资源"""
        self._on_disconnect()
        event.accept()
        
'''__||_____||__
   __||_____||__
   ___\\___//___
   _===========_
   _____|||_____
   _____|||_____
   ______|______
   ___防伪专用___'''