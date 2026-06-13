# -*- coding: utf-8 -*-
import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QTimer
from config import *
from utils import polar_to_cartesian

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
        self.ultrasonic_polar_cache = []                     # 超声波极坐标缓存
        self.ultrasonic_cartesian_cache = []                     # 超声波笛卡尔坐标缓存
        self.last_ultrasonic_data = None                        # 上次超声波数据（用于去重）
        self.velocity_data = {
            "x": np.zeros(VELOCITY_PLOT_POINTS),
            "y": np.zeros(VELOCITY_PLOT_POINTS),
            "yaw": np.zeros(VELOCITY_PLOT_POINTS)
        }
        self.time_axis = np.arange(VELOCITY_PLOT_POINTS)
        
        # 坐标轴范围
        self.trajectory_x_range = [-10, 10]  # 轨迹X轴范围
        self.trajectory_y_range = [-10, 10]  # 轨迹Y轴范围
        self.polar_range = [0, 1]           # 极坐标范围
        self.vel_x_range = [-1.5, 1.5]           # X速度范围
        self.vel_y_range = [-1.5, 1.5]           # Y速度范围
        self.vel_yaw_range = [-6, 6]       # Yaw速度范围

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

        # 极坐标超声波 + 速度曲线（分成三个图）
        self.polar_plot = pg.PlotWidget(title="ultrasonic polar coordinates")
        self.polar_plot.setAspectLocked(lock=True, ratio=1)
        
        # X速度曲线
        self.vel_x_plot = pg.PlotWidget(title="X velocity")
        self.vel_x_plot.setMaximumHeight(100)
        # Y速度曲线
        self.vel_y_plot = pg.PlotWidget(title="Y velocity")
        self.vel_y_plot.setMaximumHeight(100)
        # Yaw速度曲线
        self.vel_yaw_plot = pg.PlotWidget(title="Yaw velocity")
        self.vel_yaw_plot.setMaximumHeight(100)
        
        right_layout.addWidget(self.polar_plot, stretch=3)
        right_layout.addWidget(self.vel_x_plot, stretch=1)
        right_layout.addWidget(self.vel_y_plot, stretch=1)
        right_layout.addWidget(self.vel_yaw_plot, stretch=1)

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
        
        # 小车当前位置和方向箭头
        self.rover_arrow = pg.ArrowItem(
            angle=90, tipAngle=30, headLen=20, tailLen=10, tailWidth=3,
            pen=pg.mkPen(color="green", width=2), brush=pg.mkBrush(color="green")
        )
        self.trajectory_plot.addItem(self.rover_arrow)

        # 极坐标超声波散点
        self.polar_scatter = pg.ScatterPlotItem(
            size=8, pen=pg.mkPen(color="green"), brush=pg.mkBrush(color="green")
        )
        self.polar_plot.addItem(self.polar_scatter)
        
        # 极坐标网格：同心圆和辐射射线
        self._add_polar_grid()

        # X速度曲线
        self.vel_x_curve = self.vel_x_plot.plot(
            self.time_axis, self.velocity_data["x"], pen=pg.mkPen(color="red"), name="X速度"
        )
        self.vel_x_plot.addLegend()
        
        # Y速度曲线
        self.vel_y_curve = self.vel_y_plot.plot(
            self.time_axis, self.velocity_data["y"], pen=pg.mkPen(color="green"), name="Y速度"
        )
        self.vel_y_plot.addLegend()
        
        # Yaw速度曲线
        self.vel_yaw_curve = self.vel_yaw_plot.plot(
            self.time_axis, self.velocity_data["yaw"], pen=pg.mkPen(color="blue"), name="Yaw速度"
        )
        self.vel_yaw_plot.addLegend()
        
        # 设置初始坐标轴范围
        self.trajectory_plot.setXRange(self.trajectory_x_range[0], self.trajectory_x_range[1])
        self.trajectory_plot.setYRange(self.trajectory_y_range[0], self.trajectory_y_range[1])
        self.polar_plot.setXRange(-self.polar_range[1], self.polar_range[1])
        self.polar_plot.setYRange(-self.polar_range[1], self.polar_range[1])
        self.vel_x_plot.setYRange(self.vel_x_range[0], self.vel_x_range[1])
        self.vel_y_plot.setYRange(self.vel_y_range[0], self.vel_y_range[1])
        self.vel_yaw_plot.setYRange(self.vel_yaw_range[0], self.vel_yaw_range[1])
        
        # 隐藏极坐标图的坐标轴，使用自定义网格
        self.polar_plot.hideAxis('left')
        self.polar_plot.hideAxis('bottom')

    def _update_data(self):
        """更新导航和超声波数据"""
        try:
            # 读取导航数据
            self.rover.read_nav()
            state = self.rover.get_state()
            
            for i in state.pos:
                if abs(i) > 1000:  # 如果位置数据异常，跳过更新
                    print(f"警告：检测到异常位置数据 {state.pos}，跳过本次更新")
                    return
            
            for i in state.vel:
                if abs(i) > 10:  # 如果速度数据异常，跳过更新
                    print(f"警告：检测到异常速度数据 {state.vel}, 跳过本次更新")
                    return

            # 更新轨迹
            new_pos = np.array([[state.pos[0], state.pos[1]]])
            self.trajectory_data = np.vstack([self.trajectory_data, new_pos])
            self.trajectory_curve.setData(self.trajectory_data[:, 0], self.trajectory_data[:, 1])
            
            # 更新小车位置和方向箭头
            angle = state.pos[2]
            
            # 设置箭头位置和方向
            self.rover_arrow.setPos(state.pos[0], state.pos[1])
            self.rover_arrow.setStyle(angle=-angle/np.pi*180+90)
            
            # 检查并调整轨迹图坐标轴范围
            if (state.pos[0] < self.trajectory_x_range[0] or 
                state.pos[0] > self.trajectory_x_range[1] or
                state.pos[1] < self.trajectory_y_range[0] or 
                state.pos[1] > self.trajectory_y_range[1]):
                # 扩展范围
                min_x = min(self.trajectory_data[:, 0])
                max_x = max(self.trajectory_data[:, 0])
                min_y = min(self.trajectory_data[:, 1])
                max_y = max(self.trajectory_data[:, 1])
                # 添加一些余量
                padding = 1
                self.trajectory_x_range = [min_x - padding, max_x + padding]
                self.trajectory_y_range = [min_y - padding, max_y + padding]
                self.trajectory_plot.setXRange(self.trajectory_x_range[0], self.trajectory_x_range[1])
                self.trajectory_plot.setYRange(self.trajectory_y_range[0], self.trajectory_y_range[1])
            
            # 检查并调整轨迹图坐标轴范围
            if (state.pos[0] < self.trajectory_x_range[0] or 
                state.pos[0] > self.trajectory_x_range[1] or
                state.pos[1] < self.trajectory_y_range[0] or 
                state.pos[1] > self.trajectory_y_range[1]):
                # 扩展范围
                min_x = min(self.trajectory_data[:, 0])
                max_x = max(self.trajectory_data[:, 0])
                min_y = min(self.trajectory_data[:, 1])
                max_y = max(self.trajectory_data[:, 1])
                # 添加一些余量
                padding = 1
                self.trajectory_x_range = [min_x - padding, max_x + padding]
                self.trajectory_y_range = [min_y - padding, max_y + padding]
                self.trajectory_plot.setXRange(self.trajectory_x_range[0], self.trajectory_x_range[1])
                self.trajectory_plot.setYRange(self.trajectory_y_range[0], self.trajectory_y_range[1])

            # 更新超声波缓存（只有数据真正更新时才添加）
            current_ultrasonic = (state.distance, state.angle, state.x, state.y)
            if current_ultrasonic != self.last_ultrasonic_data:
                self.last_ultrasonic_data = current_ultrasonic
                self.ultrasonic_polar_cache.append((state.distance, state.angle))
                self.ultrasonic_cartesian_cache.append((state.x, state.y))
                
                if len(self.ultrasonic_polar_cache) > ULTRASONIC_POLAR_MAX:
                    self.ultrasonic_polar_cache.pop(0)
                if len(self.ultrasonic_cartesian_cache) > ULTRASONIC_MAX_CACHE:
                    self.ultrasonic_cartesian_cache.pop(0)

            # 更新笛卡尔坐标超声波散点
            x_ultra = [pt[0] for pt in self.ultrasonic_cartesian_cache]
            y_ultra = [pt[1] for pt in self.ultrasonic_cartesian_cache]
            self.ultrasonic_scatter.setData(x=x_ultra, y=y_ultra)

            # 更新极坐标超声波散点（最近5个）
            recent_ultra = self.ultrasonic_polar_cache[-ULTRASONIC_POLAR_MAX:]
            polar_pts = [(r * np.cos(theta), r * np.sin(theta)) for r, theta in recent_ultra]
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
            
            # 检查并调整速度图坐标轴范围
            if (state.vel[0] < self.vel_x_range[0] or state.vel[0] > self.vel_x_range[1]):
                # 扩展X速度范围
                min_val = min(self.velocity_data["x"])
                max_val = max(self.velocity_data["x"])
                padding = 0.5
                self.vel_x_range = [min_val - padding, max_val + padding]
                self.vel_x_plot.setYRange(self.vel_x_range[0], self.vel_x_range[1])
            
            if (state.vel[1] < self.vel_y_range[0] or state.vel[1] > self.vel_y_range[1]):
                # 扩展Y速度范围
                min_val = min(self.velocity_data["y"])
                max_val = max(self.velocity_data["y"])
                padding = 0.5
                self.vel_y_range = [min_val - padding, max_val + padding]
                self.vel_y_plot.setYRange(self.vel_y_range[0], self.vel_y_range[1])
            
            if (state.vel[2] < self.vel_yaw_range[0] or state.vel[2] > self.vel_yaw_range[1]):
                # 扩展Yaw速度范围
                min_val = min(self.velocity_data["yaw"])
                max_val = max(self.velocity_data["yaw"])
                padding = 1
                self.vel_yaw_range = [min_val - padding, max_val + padding]
                self.vel_yaw_plot.setYRange(self.vel_yaw_range[0], self.vel_yaw_range[1])
            
            # 检查并调整极坐标图范围
            if state.distance > self.polar_range[1]:
                # 扩展极坐标范围
                self.polar_range[1] = state.distance + 2
                self.polar_plot.setXRange(-self.polar_range[1], self.polar_range[1])
                self.polar_plot.setYRange(-self.polar_range[1], self.polar_range[1])
                # 更新极坐标网格
                self._update_polar_grid()

        except Exception as e:
            print(f"数据更新失败：{e}")
    
    def _add_polar_grid(self):
        """添加极坐标网格（同心圆和辐射射线）"""
        from PySide6.QtWidgets import QGraphicsEllipseItem
        
        # 同心圆
        self.concentric_circles = []
        num_circles = 5  # 5个同心圆
        for i in range(1, num_circles + 1):
            radius = (self.polar_range[1] / num_circles) * i
            circle = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)
            circle.setPen(pg.mkPen(color="gray", width=1, style=Qt.DashLine))
            self.polar_plot.addItem(circle)
            self.concentric_circles.append(circle)
        
        # 辐射射线（12条，30度间隔）
        self.rays = []
        num_rays = 12
        for i in range(num_rays):
            angle = i * (360 / num_rays)
            angle_rad = np.deg2rad(angle)
            x_end = self.polar_range[1] * np.cos(angle_rad)
            y_end = self.polar_range[1] * np.sin(angle_rad)
            ray = pg.PlotCurveItem(
                [0, x_end], [0, y_end],
                pen=pg.mkPen(color="gray", width=1, style=Qt.DashLine)
            )
            self.polar_plot.addItem(ray)
            self.rays.append(ray)
    
    def _update_polar_grid(self):
        """更新极坐标网格以适应新的范围"""
        # 移除旧的同心圆
        for circle in self.concentric_circles:
            self.polar_plot.removeItem(circle)
        self.concentric_circles.clear()
        
        # 移除旧的射线
        for ray in self.rays:
            self.polar_plot.removeItem(ray)
        self.rays.clear()
        
        # 添加新的网格
        self._add_polar_grid()

    def closeEvent(self, event):
        """关闭窗口"""
        self.timer.stop()
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