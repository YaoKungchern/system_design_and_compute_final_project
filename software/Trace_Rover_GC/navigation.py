# -*- coding: utf-8 -*-
import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QTimer
from config import *

class StateMonitorWidget(QWidget):
    close_signal = Signal()

    def __init__(self, rover, parent=None):
        super().__init__(parent)
        self.setWindowTitle("navigation state monitor")
        self.setMinimumSize(1000, 600)

        # 小车通信实例
        self.rover = rover
        # 数据缓存
        self.trajectory_data = np.array([[0.0, 0.0]])  # 轨迹数据
        self.ultrasonic_cache = []                     # 超声波缓存
        self.velocity_data = {
            "x": np.zeros(VELOCITY_PLOT_POINTS),
            "y": np.zeros(VELOCITY_PLOT_POINTS),
            "yaw": np.zeros(VELOCITY_PLOT_POINTS)
        }
        self.time_axis = np.arange(VELOCITY_PLOT_POINTS)

        # 初始化UI和绘图
        self._init_ui()
        self._init_plots()

        # 定时读取导航数据
        self.timer = QTimer()
        self.timer.setInterval(int(1000 / NAV_READ_FREQ))
        self.timer.timeout.connect(self._update_data)
        self.timer.start()

    def _init_ui(self):
        """初始化UI布局"""
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # 左侧：2D轨迹+超声波散点
        self.trajectory_plot = pg.PlotWidget(title="rover trajectory + ultrasonic radar")
        left_layout.addWidget(self.trajectory_plot)

        # 极坐标超声波 + 速度曲线
        self.polar_plot = pg.PlotWidget(title="ultrasonic polar coordinates")
        self.polar_plot.setAspectLocked(lock=True, ratio=1)
        self.velocity_plot = pg.PlotWidget(title="3-axis velocity curves")
        right_layout.addWidget(self.polar_plot)
        right_layout.addWidget(self.velocity_plot)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

    def _init_plots(self):
        """初始化绘图元素"""
        # 轨迹曲线
        self.trajectory_curve = self.trajectory_plot.plot(
            self.trajectory_data[:, 0], self.trajectory_data[:, 1],
            pen=pg.mkPen(color="red", width=2), name="轨迹"
        )
        # 超声波散点（笛卡尔）
        self.ultrasonic_scatter = pg.ScatterPlotItem(
            size=8, pen=pg.mkPen(color="blue"), brush=pg.mkBrush(color="blue"), name="超声波"
        )
        self.trajectory_plot.addItem(self.ultrasonic_scatter)

        # 极坐标超声波散点
        self.polar_scatter = pg.ScatterPlotItem(
            size=8, pen=pg.mkPen(color="green"), brush=pg.mkBrush(color="green")
        )
        self.polar_plot.addItem(self.polar_scatter)

        # 速度曲线
        self.vel_x_curve = self.velocity_plot.plot(
            self.time_axis, self.velocity_data["x"], pen=pg.mkPen(color="red"), name="X速度"
        )
        self.vel_y_curve = self.velocity_plot.plot(
            self.time_axis, self.velocity_data["y"], pen=pg.mkPen(color="green"), name="Y速度"
        )
        self.vel_yaw_curve = self.velocity_plot.plot(
            self.time_axis, self.velocity_data["yaw"], pen=pg.mkPen(color="blue"), name="Yaw速度"
        )
        self.velocity_plot.addLegend()

    def _update_data(self):
        """更新导航和超声波数据"""
        try:
            # 读取导航数据
            self.rover.read_nav()
            state = self.rover.get_state()

            # 更新轨迹
            new_pos = np.array([[state.pos[0], state.pos[1]]])
            self.trajectory_data = np.vstack([self.trajectory_data, new_pos])
            self.trajectory_curve.setData(self.trajectory_data[:, 0], self.trajectory_data[:, 1])

            # 更新超声波缓存
            if hasattr(state, "distance") and hasattr(state, "angle"):
                self.ultrasonic_cache.append((state.distance, state.angle))
                if len(self.ultrasonic_cache) > ULTRASONIC_MAX_CACHE:
                    self.ultrasonic_cache.pop(0)

                # 更新笛卡尔坐标超声波散点
                cartesian_pts = [polar_to_cartesian(r, theta) for r, theta in self.ultrasonic_cache]
                x_ultra = [pt[0] for pt in cartesian_pts]
                y_ultra = [pt[1] for pt in cartesian_pts]
                self.ultrasonic_scatter.setData(x=x_ultra, y=y_ultra)

                # 更新极坐标超声波散点（最近5个）
                recent_ultra = self.ultrasonic_cache[-ULTRASONIC_POLAR_MAX:]
                polar_pts = [(r * np.cos(np.radians(theta)), r * np.sin(np.radians(theta))) for r, theta in recent_ultra]
                x_polar = [pt[0] for pt in polar_pts]
                y_polar = [pt[1] for pt in polar_pts]
                self.polar_scatter.setData(x=x_polar, y=y_polar)

            # 更新速度曲线
            self.velocity_data["x"] = np.roll(self.velocity_data["x"], -1)
            self.velocity_data["x"][-1] = state.vel[0]
            self.velocity_data["y"] = np.roll(self.velocity_data["y"], -1)
            self.velocity_data["y"][-1] = state.vel[1]
            self.velocity_data["yaw"] = np.roll(self.velocity_data["yaw"], -1)
            self.velocity_data["yaw"][-1] = state.vel[2]

            self.vel_x_curve.setData(self.time_axis, self.velocity_data["x"])
            self.vel_y_curve.setData(self.time_axis, self.velocity_data["y"])
            self.vel_yaw_curve.setData(self.time_axis, self.velocity_data["yaw"])

        except Exception as e:
            print(f"数据更新失败：{e}")

    def closeEvent(self, event):
        """关闭窗口"""
        self.timer.stop()
        self.close_signal.emit()
        event.accept()