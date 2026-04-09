# import serial
import asyncio
from bleak import BleakClient
import struct
import threading
import time
import copy
from dataclasses import dataclass, field
import sys

# ==========================================================
#  通信协议定义
# ==========================================================
# 帧头和帧尾
HEAD = b'\xFA\xAF'
TAIL = b'\xFB\xBF'

# DX-BT24 固定的透传服务和特征值（不用改！）
UART_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
UART_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# 功能指令 ID
CMD_PID = 0x50  # PID参数设置
CMD_NAV = 0x4E   #导航指令
CMD_CONTROL = 0x4D  # 运动控制指令
CMD_ULTRASONIC = 0x55  # 超声波指令指令

@dataclass
class RobotState:   # pid_info + compliance_info + control_info
    """
    [数据看板]
    “共享内存块”，用来存放读回来的最新状态。
    """
    # --- PID 相关信息 (0x50) ---
    pid_mode: int = 0  # 模式标志位
    controller_id: int = 0  # 控制器ID (0:速度环, 1:位置环)

    # 调试用的中间变量
    delta: float = 0.0  # 误差
    delta_d: float = 0.0  # 微分
    delta_i: float = 0.0  # 积分

    # PID 核心参数
    kp: float = 0.0
    ki: float = 0.0
    kd: float = 0.0
    i_limit: float = 0.0  # 积分限幅
    o_limit: float = 0.0  # 输出限幅

    # --- 导航信息 (0x4E) ---
    nav_mode: int = 0
    pos: list = field(default_factory=lambda: [0.0 for _ in range(3)])  # 位置
    vel: list = field(default_factory=lambda: [0.0 for _ in range(3)])  # 速度

    # --- 运动控制反馈 (0x4D) ---
    control_mode: int = 0xFF
    control_val: list = field(default_factory=lambda: [0.0 for _ in range(3)])  # 控制值
    
    # --- 超声波信息 (0x55) ---
    distance: float = 0.0  # 超声波距离
    angle: float = 0.0  # 超声波角度
    x: float = 0.0  # 超声波世界坐标系X轴坐标
    y: float = 0.0  # 超声波世界坐标系Y轴坐标

class trace_rover:
    # def __init__(self, port: str, baudrate=115200)->None:
    def __init__(self, mac_address: str)->None:
        # timeout=0.1 防止卡死
        # self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.client = BleakClient(mac_address)

        # 实例化状态对象
        self.state = RobotState()

        self._running = True
        self._buffer = bytearray()  # 接收缓冲区
        self._lock = threading.Lock()  # 线程锁
        self._notification_received = False
        self._connected = False

        # 创建并启动事件循环线程
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._event_loop_thread, daemon=True)
        self.loop_thread.start()

        # 连接BLE设备
        try:
            asyncio.run_coroutine_threadsafe(self._connect(), self.loop).result()
        except Exception as e:
            print(f"无法连接BLE设备: {e}")
            self.close()
            raise

        # 启动后台接收线程
        self.thread = threading.Thread(target=self._reader_thread, daemon=True)
        self.thread.start()
    
    def _event_loop_thread(self):
        """事件循环线程"""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
    
    async def _connect(self):
        """连接BLE设备并设置通知"""
        await self.client.connect()
        await self.client.start_notify(UART_CHAR_UUID, self._notification_handler)
        self._connected = True

    def close(self)->None:
        """关闭连接"""
        self._running = False
        self._connected = False
        
        # 停止通知并断开连接
        async def disconnect():
            try:
                await self.client.stop_notify(UART_CHAR_UUID)
            except:
                pass
            try:
                await self.client.disconnect()
            except:
                pass
            # 停止事件循环
            self.loop.stop()
        
        try:
            asyncio.run_coroutine_threadsafe(disconnect(), self.loop).result()
        except:
            pass
        
        # 等待线程结束
        try:
            self.thread.join(timeout=2.0)
            self.loop_thread.join(timeout=2.0)
        except:
            pass
        
    def get_state(self)->RobotState:
        """ [给UI调用的接口]"""
        with self._lock:
            return copy.copy(self.state)

    # ==========================================================
    #  校验
    # ==========================================================
    def _calc_checksum(self, cmd_id: int, data_bytes: bytes)->int:
        """ 校验位计算 """
        check = cmd_id
        for b in data_bytes:
            check ^= b
        return check

    # ==========================================================
    #  底层发送逻辑
    # ==========================================================
    def _send_frame(self, cmd_id: int, data_bytes: bytes)->None:
        """
        Frame = [HEAD (2B)] + [CMD (1B)] + [DATA (NB)] + [CHECK (1B)] + [TAIL (2B)]
        """
        # 1. 算出数据的校验位
        checksum = self._calc_checksum(cmd_id, data_bytes)

        # 2. 拼装字节流
        # struct.pack('B', x) 把整数转成 1个字节的二进制
        frame = HEAD + struct.pack('B', cmd_id) + data_bytes + struct.pack('B', checksum) + TAIL

        # 3. 发送出去
        # self.ser.write(frame)
        try:
            asyncio.run_coroutine_threadsafe(self.client.write_gatt_char(UART_CHAR_UUID, frame), self.loop).result()
        except Exception as e:
            print(f"发送数据失败: {e}")

        # 调试输出：以十六进制大写形式打印，方便看发了什么
        print(f"Sent: {frame.hex(' ').upper()}")

    # ==========================================================
    #  业务指令封装
    # ==========================================================

    def write_pid(self, controller_id: int, kp: float, ki: float, kd: float, i_limit: float, o_limit: float)->None:
        """
        发送 PID 参数
        """
        rw_flag = 0x00  #“写入”操作

        fmt = '<BBffffffff'

        data = struct.pack(fmt,
                           rw_flag,
                           controller_id,
                           0.0, 0.0, 0.0,  # 下位机结构体里有这三个变量，写入时我们不用管，填0占位
                           kp, ki, kd,
                           i_limit, o_limit)

        self._send_frame(CMD_PID, data)

    def read_pid(self, controller_id: int)->None:
        """
        请求读取 PID
        """
        rw_flag = 0x01
        data = struct.pack('<BB', rw_flag, controller_id)
        self._send_frame(CMD_PID, data)

    def write_nav(self, pos: list)->None:
        """
        写入导航参数 (Mode, Position)
        """
        rw_flag = 0x00
        fmt = '<Bffffff'
        data = struct.pack(fmt, rw_flag, pos[0], pos[1], pos[2], 0.0, 0.0, 0.0)
        # 速度写入不生效
        self._send_frame(CMD_NAV, data)

    def read_nav(self)->None:
        """
        请求读取导航参数
        """
        rw_flag = 0x01
        data = struct.pack('<B', rw_flag)
        self._send_frame(CMD_NAV, data)

    def write_control(self, mode: int, value: list)->None:
        """
        发送运动控制指令
        5字节
        """
        fmt = '<Bfff'
        data = struct.pack(fmt, mode, value[0], value[1], value[2])
        self._send_frame(CMD_CONTROL, data)

    # ==========================================================
    #  接收线程
    # ==========================================================
    def _notification_handler(self, sender, data):
        """BLE通知处理函数"""
        if not self._connected:
            return
        # 看原始字节是什么
        # print(f"DEBUG Received Raw: {data.hex(' ').upper()}")
        self._buffer.extend(data)
        self._parse_buffer()
        self._notification_received = True
    
    def _reader_thread(self):
        while self._running:
            try:
                if not self.client.is_connected:
                    time.sleep(0.005)
            except Exception as e:
                print(f"BLE Error: {e}")
                time.sleep(1)
    def _parse_buffer(self):
        """
        [解包逻辑]
        最小帧长 = Head(2) + Cmd(1) + Data(至少1) + Check(1) + Tail(2) = 7字节
        """
        while len(self._buffer) >= 7:
            # Step 1: 找帧头
            head_idx = self._buffer.find(HEAD)

            if head_idx == -1:
                # 没找到头
                self._buffer.clear()
                return

            if head_idx > 0:
                # 找到了头，但是头前面有一些垃圾数据，删掉前面的
                del self._buffer[:head_idx]
                continue  # 删完垃圾重新循环，现在的 buffer[0] 就是 HEAD 了

            # Step 2: 提取指令 ID
            # buffer[0:2] -- HEAD，buffer[2] -- CMD
            if len(self._buffer) < 3: return  # 长度不够，继续等数据
            cmd_id = self._buffer[2]

            # Step 3: 查表确定数据长度
            data_len = 0
            fmt = ""

            if cmd_id == CMD_PID:
                # 下位机回传的 PID 包也是完整的结构体，所以是 34 字节
                data_len = 34
                fmt = '<BBffffffff'
            elif cmd_id == CMD_NAV:
                data_len = 25
                fmt = '<Bffffff'
            elif cmd_id == CMD_CONTROL:
                data_len = 13
                fmt = '<Bfff'
            elif cmd_id == CMD_ULTRASONIC:
                data_len = 16
                fmt = '<ffff'
            else:
                # 收到一个不认识的 CMD。可能因为数据错乱，跳过帧头往后找
                del self._buffer[0:2]
                continue

            # Step 4: 计算整帧理论长度
            frame_len = 2 + 1 + data_len + 1 + 2

            if len(self._buffer) < frame_len:
                return  # 数据还没收全 (粘包处理)，退出函数等待下一次接收

            # Step 5: 验证帧尾
            # 检查 buffer 的最后两个字节是不是 FB BF
            if self._buffer[frame_len - 2: frame_len] != TAIL:
                del self._buffer[0:2]  # 删掉这个假头，继续往后找
                continue

            # Step 6:校验验证 (XOR Check)
            # 取出数据部分 [3 : 3+data_len]
            data_payload = self._buffer[3: 3 + data_len]
            # 取出收到的校验位
            recv_checksum = self._buffer[3 + data_len]

            # 自己算：用 ID 和 数据 算异或
            calc_checksum = self._calc_checksum(cmd_id, data_payload)

            # if recv_checksum != calc_checksum:
            #     # print(f"[Warn] 校验失败! 收到的:{recv_checksum:02X} 算出的:{calc_checksum:02X}")
            #     # print(f"[Warn] 帧数据: {self._buffer[:frame_len].hex(' ').upper()}")
            #     # print(f"[Warn] 指令ID: {cmd_id:02X}, 数据长度: {data_len}")
            #     # 校验失败，删掉这一整帧，不处理
            #     del self._buffer[:frame_len]
            #     continue

            # Step 7: 解包 (Unpack)
            try:
                unpacked = struct.unpack(fmt, data_payload)
                self._update_state(cmd_id, unpacked)
            except struct.error:
                print("Struct Unpack failed (数据格式对不上)")

            # Step 8:
            del self._buffer[:frame_len]

    def _update_state(self, cmd_id, data):
        """
        将解包后的元组数据填入 RobotState 对象中
        """
        with self._lock:
            if cmd_id == CMD_PID:
                self.state.pid_mode = data[0]
                self.state.controller_id = data[1]
                self.state.delta = data[2]
                self.state.kp = data[5]
                self.state.ki = data[6]
                self.state.kd = data[7]
                self.state.i_limit = data[8]
                self.state.o_limit = data[9]
                print(f"收到反馈 PID: Kp={self.state.kp:.2f}")

            elif cmd_id == CMD_NAV:
                self.state.nav_mode = data[0]
                self.state.pos = [data[1], data[2], data[3]]
                self.state.vel = [data[4], data[5], data[6]]
                # print(f"收到反馈 Nav: Pos={self.state.pos}, Vel={self.state.vel}")

            elif cmd_id == CMD_CONTROL:
                self.state.control_mode = data[0]
                self.state.control_val = [data[1], data[2], data[3]]
            
            elif cmd_id == CMD_ULTRASONIC:
                self.state.distance = data[0] 
                self.state.angle = data[1]
                self.state.x = data[2]
                self.state.y = data[3]
                print(f"收到反馈 Ultrasonic: {self.state.distance}")

# ==========================================================
#  测试
# ==========================================================
if __name__ == "__main__":
    try:
        # 1. 打开串口 (请根据电脑实际情况修改 COM 号)
        robot = trace_rover("48:87:2D:82:0C:48")

        # 2. 发送一个写指令：设置 PID 的 Kp=1.0
        print(">>> 正在发送 PID 写入指令 (Kp=1.0)...")
        robot.write_pid(controller_id=0x00, kp=1.0, ki=0.0, kd=0.0, i_limit=0.3, o_limit=1.0)

        # 3. 发送一个读请求：问下位机“你现在的参数是多少？”
        # 稍微延时一下，防止指令太快下位机处理不过来
        time.sleep(0.1)
        print(">>> 正在发送 PID 读取请求...")
        robot.read_pid(controller_id=0x00)
        
        time.sleep(1.0)
        # robot.write_control(mode=0x01, value=[0.0, 0.0, 1.0])

        # 4. 模拟主循环，观察数据更新
        # 实际项目中，这里可能是 GUI 的 update 循环
        print(">>> 等待接收数据回传...")
        for i in range(100):
            time.sleep(0.5)
            # 获取最新的状态副本
            state = robot.get_state()
            robot.read_pid(controller_id=0x00)  # 不断请求 PID 状态，看看参数有没有更新
            print(f"当前状态 kp: {state.kp:.2f}")
            
            # robot.read_nav()
            # print(f"当前状态 pos: {state.pos[0], state.pos[1], state.pos[2]}") # 解开注释可查看
            # print(f"当前状态 speed: {state.vel[0], state.vel[1], state.vel[2]}") # 解开注释可查看

        # 5. 测试结束，关闭资源
        robot.close()
        print(">>> 测试结束，BLE连接已关闭。")

    # except serial.SerialException:
    except Exception as e:
        print(f"!!! 无法连接BLE设备，请检查蓝牙是否开启，或者MAC地址是否正确: {e}")
    # except Exception as e:
    #     print(f"!!! 发生未知错误: {e}")