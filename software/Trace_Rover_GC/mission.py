# -*- coding: utf-8 -*-
import json
import os
import time
import threading
from PySide6.QtWidgets import (QWidget, QMessageBox, QTableWidget, QTableWidgetItem,
                               QPushButton, QVBoxLayout, QHBoxLayout, QComboBox,
                               QLineEdit, QLabel, QSpinBox, QCheckBox)
from PySide6.QtCore import Qt, Signal
from config import MISSION_CONFIG_PATH, BASE_DIR

# 命令类型定义
COMMAND_TYPES = ["state", "mov", "servo", "delay"]

# state命令的5种状态类型
STATE_TYPES = {"open": 0x00, "vel_robot": 0x01, "vel_world": 0x02, "pos_robot": 0x03, "pos_world": 0x04}

class MissionWidget(QWidget):
    close_signal = Signal()

    def __init__(self, rover=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mission Planning")
        self.setWindowModality(Qt.NonModal)
        self.resize(600, 500)
        
        # 小车通信实例
        self.rover = rover
        
        # 任务命令列表
        self.mission_commands = []
        
        # 执行状态
        self.is_executing = False
        self.execution_thread = None
        self.repeat_count = 1
        self.is_infinite = False
        
        # 初始化UI
        self._init_ui()
        
        # 加载默认配置
        self._load_mission_from_file()

    def _init_ui(self):
        """初始化界面布局"""
        # 主布局
        main_layout = QVBoxLayout()
        
        # 命令列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Command Type", "Parameters", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        # 监听表格编辑事件，同步更新 mission_commands
        self.table.itemChanged.connect(self._on_table_item_changed)
        main_layout.addWidget(self.table)
        
        # 命令添加区域
        add_layout = QHBoxLayout()
        
        # 命令类型选择
        self.cmd_type_combo = QComboBox()
        self.cmd_type_combo.addItems(COMMAND_TYPES)
        self.cmd_type_combo.currentTextChanged.connect(self._on_cmd_type_changed)
        add_layout.addWidget(QLabel("Command:"))
        add_layout.addWidget(self.cmd_type_combo)
        
        # 参数输入框
        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("Enter parameters...")
        add_layout.addWidget(QLabel("Params:"))
        add_layout.addWidget(self.param_input)
        
        # 添加按钮
        add_btn = QPushButton("Add Command")
        add_btn.clicked.connect(self._on_add_command)
        add_layout.addWidget(add_btn)
        
        main_layout.addLayout(add_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 读取按钮
        load_btn = QPushButton("Load Mission")
        load_btn.clicked.connect(self._on_load_mission)
        button_layout.addWidget(load_btn)
        
        # 保存按钮
        save_btn = QPushButton("Save Mission")
        save_btn.clicked.connect(self._on_save_mission)
        button_layout.addWidget(save_btn)
        
        # 删除选中按钮
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self._on_delete_command)
        button_layout.addWidget(delete_btn)
        
        main_layout.addLayout(button_layout)
        
        # 执行控制区域
        exec_layout = QHBoxLayout()
        
        # 重复执行设置
        self.infinite_checkbox = QCheckBox("Infinite Repeat")
        self.infinite_checkbox.stateChanged.connect(self._on_infinite_changed)
        exec_layout.addWidget(self.infinite_checkbox)
        
        self.repeat_label = QLabel("Repeat Count:")
        exec_layout.addWidget(self.repeat_label)
        
        self.repeat_spinbox = QSpinBox()
        self.repeat_spinbox.setMinimum(1)
        self.repeat_spinbox.setMaximum(999)
        self.repeat_spinbox.setValue(1)
        exec_layout.addWidget(self.repeat_spinbox)
        
        # 开始执行按钮
        self.start_btn = QPushButton("Start Execution")
        self.start_btn.clicked.connect(self._on_start_execution)
        exec_layout.addWidget(self.start_btn)
        
        # 停止执行按钮
        self.stop_btn = QPushButton("Stop Execution")
        self.stop_btn.clicked.connect(self._on_stop_execution)
        self.stop_btn.setEnabled(False)
        exec_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(exec_layout)
        
        # 执行状态标签
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: green")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        
        # 设置参数输入框的初始提示
        self._update_param_hint()

    def _update_param_hint(self):
        """根据命令类型更新参数输入提示"""
        cmd_type = self.cmd_type_combo.currentText()
        hints = {
            "state": "format: state,x,y,yaw (e.g., pos_world,0.0,1.0,90)",
            "mov": "format: x,y,yaw (e.g., 0.5,0.0,0.0)",
            "servo": "format: angle (0-180, e.g., 120)",
            "delay": "format: seconds (e.g., 1.0)"
        }
        self.param_input.setPlaceholderText(hints.get(cmd_type, ""))

    def _on_cmd_type_changed(self):
        """命令类型改变时更新参数提示"""
        self._update_param_hint()

    def _on_infinite_changed(self, state):
        """无限循环复选框状态改变"""
        self.repeat_spinbox.setEnabled(not (state == Qt.Checked))

    def _on_add_command(self):
        """添加命令到列表"""
        cmd_type = self.cmd_type_combo.currentText()
        params = self.param_input.text().strip()
        
        if not params:
            QMessageBox.warning(self, "Warning", "Please enter parameters!")
            return
        
        # 验证参数格式
        if not self._validate_parameters(cmd_type, params):
            return
        
        # 添加到命令列表
        self.mission_commands.append({"name": cmd_type, "params": params})
        
        # 更新表格
        self._update_table()
        
        # 清空输入
        self.param_input.clear()

    def _validate_parameters(self, cmd_type, params):
        """验证参数格式"""
        try:
            if cmd_type == "state":
                parts = params.split(",")
                if len(parts) != 4:
                    raise ValueError("State requires 4 parameters: state,x,y,yaw")
                state_type = parts[0].strip()
                if state_type not in STATE_TYPES.keys():
                    raise ValueError(f"Invalid state type. Must be one of: {list(STATE_TYPES.keys())}")
                # 验证数字参数
                float(parts[1].strip())
                float(parts[2].strip())
                float(parts[3].strip())
            elif cmd_type == "mov":
                parts = params.split(",")
                if len(parts) != 3:
                    raise ValueError("Mov requires 3 parameters: x,y,yaw")
                for p in parts:
                    float(p.strip())
            elif cmd_type == "servo":
                angle = float(params)
                if angle < 0 or angle > 180:
                    raise ValueError("Servo angle must be between 0-180")
            elif cmd_type == "delay":
                delay = float(params)
                if delay < 0:
                    raise ValueError("Delay must be non-negative")
            return True
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Parameters", str(e))
            return False

    def _update_table(self):
        """更新表格显示"""
        # 暂时断开信号，避免更新时触发多次
        self.table.itemChanged.disconnect(self._on_table_item_changed)
        
        self.table.setRowCount(len(self.mission_commands))
        
        for i, cmd in enumerate(self.mission_commands):
            # 命令类型
            type_item = QTableWidgetItem(cmd["name"])
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, type_item)
            
            # 参数
            param_item = QTableWidgetItem(cmd["params"])
            self.table.setItem(i, 1, param_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            
            up_btn = QPushButton("↑")
            up_btn.setFixedSize(30, 25)
            up_btn.clicked.connect(lambda _, idx=i: self._move_command_up(idx))
            
            down_btn = QPushButton("↓")
            down_btn.setFixedSize(30, 25)
            down_btn.clicked.connect(lambda _, idx=i: self._move_command_down(idx))
            
            btn_layout.addWidget(up_btn)
            btn_layout.addWidget(down_btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            self.table.setCellWidget(i, 2, btn_widget)
        
        # 重新连接信号
        self.table.itemChanged.connect(self._on_table_item_changed)

    def _on_table_item_changed(self, item):
        """表格内容变化时同步更新 mission_commands"""
        row = item.row()
        col = item.column()
        
        if row >= 0 and row < len(self.mission_commands):
            if col == 1:  # 参数列
                self.mission_commands[row]["params"] = item.text()
                # 更新状态为未保存
                self.status_label.setText("Status: Modified")
                self.status_label.setStyleSheet("color: orange")
        
        # 调整列宽
        self.table.resizeColumnsToContents()

    def _move_command_up(self, index):
        """向上移动命令"""
        if index > 0:
            self.mission_commands[index], self.mission_commands[index-1] = \
                self.mission_commands[index-1], self.mission_commands[index]
            self._update_table()

    def _move_command_down(self, index):
        """向下移动命令"""
        if index < len(self.mission_commands) - 1:
            self.mission_commands[index], self.mission_commands[index+1] = \
                self.mission_commands[index+1], self.mission_commands[index]
            self._update_table()

    def _on_delete_command(self):
        """删除选中的命令"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a command to delete!")
            return
        
        # 从后往前删除，避免索引错乱
        rows = sorted([row.row() for row in selected_rows], reverse=True)
        for row in rows:
            del self.mission_commands[row]
        
        self._update_table()

    def _load_mission_from_file(self):
        """从文件加载任务规划（支持新的数组格式）"""
        if os.path.exists(os.path.join(BASE_DIR, MISSION_CONFIG_PATH)):
            try:
                with open(os.path.join(BASE_DIR, MISSION_CONFIG_PATH), 'r') as f:
                    data = json.load(f)
                    self.mission_commands = []
                    
                    # 获取任务列表（支持两种格式：直接数组 或 {"mission": [...]}）
                    mission_list = data if isinstance(data, list) else data.get("mission", [])
                    
                    # 新格式：数组形式，支持多个相同类型的命令
                    for cmd_data in mission_list:
                        if "name" in cmd_data and "params" in cmd_data:
                            cmd_type = cmd_data["name"]
                            params = cmd_data["params"]
                            
                            if cmd_type == "state":
                                # state格式: {"state": "pos_world", "mov": [0.0, 1.0, 90]}
                                if isinstance(params, dict) and "state" in params and "mov" in params:
                                    mov_vals = params["mov"]
                                    param_str = f"{params['state']},{mov_vals[0]},{mov_vals[1]},{mov_vals[2]}"
                                    self.mission_commands.append({"name": cmd_type, "params": param_str})
                            elif cmd_type == "delay":
                                # delay格式: {"time": 2.0} 或直接数字
                                if isinstance(params, dict) and "time" in params:
                                    self.mission_commands.append({"name": cmd_type, "params": str(params["time"])})
                                else:
                                    self.mission_commands.append({"name": cmd_type, "params": str(params)})
                            elif cmd_type == "servo":
                                # servo格式: {"angle": 120.0} 或直接数字
                                if isinstance(params, dict) and "angle" in params:
                                    self.mission_commands.append({"name": cmd_type, "params": str(params["angle"])})
                                else:
                                    self.mission_commands.append({"name": cmd_type, "params": str(params)})
                            elif isinstance(params, list):
                                param_str = ",".join(str(p) for p in params)
                                self.mission_commands.append({"name": cmd_type, "params": param_str})
                            else:
                                self.mission_commands.append({"name": cmd_type, "params": str(params)})
                self._update_table()
                self.status_label.setText("Status: Loaded from config")
                self.status_label.setStyleSheet("color: blue")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load mission: {str(e)}")
        else:
            # 创建默认任务示例
            self._create_default_mission()

    def _create_default_mission(self):
        """创建默认任务示例"""
        self.mission_commands = [
            {"name": "state", "params": "pos_world,0.0,0.0,0"},
            {"name": "delay", "params": "1.0"},
            {"name": "mov", "params": "0.5,0.0,0.0"},
            {"name": "delay", "params": "2.0"},
            {"name": "servo", "params": "120"},
            {"name": "delay", "params": "1.0"},
            {"name": "state", "params": "stop,0.0,0.0,0"}
        ]
        self._update_table()

    def _on_load_mission(self):
        """手动加载任务规划"""
        self._load_mission_from_file()

    def _on_save_mission(self):
        """保存任务规划到文件（使用新的数组格式，支持多个相同类型的命令）"""
        if not self.mission_commands:
            QMessageBox.warning(self, "Warning", "No commands to save!")
            return
        
        try:
            # 新格式：数组形式，可以保存任意数量的命令
            data = []
            for cmd in self.mission_commands:
                cmd_type = cmd["name"]
                params = cmd["params"]
                
                cmd_item = {"name": cmd_type}
                
                if cmd_type == "state":
                    # 转换为JSON格式: {"type": "...", "mov": [...]}
                    parts = params.split(",")
                    state_type = parts[0].strip()
                    mov_vals = [float(p.strip()) for p in parts[1:4]]
                    cmd_item["params"] = {"state": state_type, "mov": mov_vals}
                elif cmd_type == "mov":
                    cmd_item["params"] = [float(p.strip()) for p in params.split(",")]
                elif cmd_type == "servo":
                    cmd_item["params"] = float(params)
                elif cmd_type == "delay":
                    cmd_item["params"] = float(params)
                
                data.append(cmd_item)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.join(BASE_DIR, MISSION_CONFIG_PATH)), exist_ok=True)
            
            with open(os.path.join(BASE_DIR, MISSION_CONFIG_PATH), 'w') as f:
                json.dump(data, f, indent=4)
            
            QMessageBox.information(self, "Success", "Mission saved successfully!")
            self.status_label.setText("Status: Saved")
            self.status_label.setStyleSheet("color: green")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save mission: {str(e)}")

    def _on_start_execution(self):
        """开始执行任务"""
        if not self.mission_commands:
            QMessageBox.warning(self, "Warning", "No commands to execute!")
            return
        
        if self.is_executing:
            QMessageBox.warning(self, "Warning", "Mission is already executing!")
            return
        
        # 获取重复次数设置
        if self.infinite_checkbox.isChecked():
            self.is_infinite = True
        else:
            self.is_infinite = False
            self.repeat_count = self.repeat_spinbox.value()
        
        # 更新UI状态
        self.is_executing = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Executing...")
        self.status_label.setStyleSheet("color: red")
        
        # 禁用表格编辑
        self.table.setEnabled(False)
        
        # 启动执行线程
        self.execution_thread = threading.Thread(target=self._execute_mission, daemon=True)
        self.execution_thread.start()

    def _execute_mission(self):
        """执行任务命令"""
        execution_count = 0
        
        while (self.is_infinite or execution_count < self.repeat_count) and self.is_executing:
            execution_count += 1
            
            for i, cmd in enumerate(self.mission_commands):
                if not self.is_executing:
                    break
                
                cmd_type = cmd["name"]
                params = cmd["params"]
                
                try:
                    if cmd_type == "state":
                        # 解析状态命令
                        parts = params.split(",")
                        state_type = parts[0].strip()
                        mov_vals = [float(p.strip()) for p in parts[1:4]]
                        self._execute_state_command(state_type, mov_vals)
                    elif cmd_type == "mov":
                        # 解析运动命令
                        mov_vals = [float(p.strip()) for p in params.split(",")]
                        self._execute_mov_command(mov_vals)
                    elif cmd_type == "servo":
                        # 解析舵机命令
                        angle = float(params)
                        self._execute_servo_command(angle)
                    elif cmd_type == "delay":
                        # 解析延时命令
                        delay_time = float(params)
                        self._execute_delay_command(delay_time)
                except Exception as e:
                    print(f"Command execution error: {e}")
                    continue
            
            time.sleep(0.1)
        
        # 执行完成
        self._execution_finished()

    def _execute_state_command(self, state_type, mov_vals):
        """执行状态命令"""
        print(f"Executing state command: {state_type}, {mov_vals}")
        if self.rover:
            for i in range(5):
                time.sleep(0.2)
                self.rover.write_control(STATE_TYPES.get(state_type, 0x00), mov_vals)

    def _execute_mov_command(self, mov_vals):
        """执行运动命令"""
        print(f"Executing mov command: {mov_vals}")
        if self.rover:
            for i in range(5):
                time.sleep(0.2)
                self.rover.write_control(0xFF, mov_vals)

    def _execute_servo_command(self, angle):
        """执行舵机命令"""
        print(f"Executing servo command: {angle}")
        if self.rover:
            for i in range(5):
                time.sleep(0.2)
                self.rover.write_servo(angle)

    def _execute_delay_command(self, delay_time):
        """执行延时命令"""
        print(f"Executing delay command: {delay_time}s")
        start_time = time.time()
        while time.time() - start_time < delay_time and self.is_executing:
            time.sleep(0.01)

    def _execution_finished(self):
        """执行完成清理"""
        self.is_executing = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.table.setEnabled(True)
        
        if self.is_infinite:
            self.status_label.setText("Status: Stopped")
        else:
            self.status_label.setText("Status: Execution completed")
        self.status_label.setStyleSheet("color: green")

    def _on_stop_execution(self):
        """停止执行任务"""
        self.is_executing = False
        if self.execution_thread:
            self.execution_thread.join(timeout=1)

    def closeEvent(self, event):
        """关闭窗口"""
        self._on_stop_execution()
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