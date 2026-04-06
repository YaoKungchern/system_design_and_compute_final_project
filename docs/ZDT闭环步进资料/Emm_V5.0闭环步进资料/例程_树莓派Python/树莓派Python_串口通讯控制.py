# 感谢用户Concept(981538731)提供的树莓派Python串口通讯控制例程

import time, utime
from machine import Pin, UART
import ustruct
# 初始化LED灯，树莓派PICO默认LED
led_pin = Pin(25, Pin.OUT)
led_pin.value(0) 
# 初始化串口
uart1 =UART(1, baudrate = 115200, bits = 8, parity = None, stop = 1, tx = Pin(4),  rx = Pin(5))  
uart2 =UART(0, baudrate = 115200, bits = 8, parity = None, stop = 1, tx = Pin(12), rx = Pin(13))

# 对照表
'''
    S_VER = 0      # 读取固件版本和对应的硬件版本
    S_RL = 1       # 读取读取相电阻和相电感
    S_PID = 2      # 读取PID参数
    S_VBUS = 3     # 读取总线电压
    S_CPHA = 5     # 读取相电流
    S_ENCL = 7     # 读取经过线性化校准后的编码器值
    S_TPOS = 8     # 读取电机目标位置角度
    S_VEL = 9      # 读取电机实时转速
    S_CPOS = 10    # 读取电机实时位置角度
    S_PERR = 11    # 读取电机位置误差角度
    S_FLAG = 13    # 读取使能/到位/堵转状态标志位
    S_Conf = 14    # 读取驱动参数
    S_State = 15   # 读取系统状态参数
    S_ORG = 16     # 读取正在回零/回零失败状态标志位
'''

def Emm_V5_Read_Sys_Params(addr, s): # 读取驱动板参数
    i = 0
    cmd = bytearray(16)
    cmd[i] = addr
    i += 1 
    func_codes = {
        'S_VER': 0x1F,
        'S_RL': 0x20,
        'S_PID': 0x21,
        'S_VBUS': 0x24,
        'S_CPHA': 0x27,
        'S_ENCL': 0x31,
        'S_TPOS': 0x33,
        'S_VEL': 0x35,
        'S_CPOS': 0x36,
        'S_PERR': 0x37,
        'S_FLAG': 0x3A,
        'S_ORG': 0x3B,
        'S_Conf': 0x42,     # 读取驱动参数，功能码后面还需要加上一个辅助码0x6C
        'S_State': 0x43     # 读取系统状态参数，功能码后面还需要加上一个辅助码0x7A
    }
    if s in func_codes:
        cmd[i] = func_codes[s]
        i += 1
    cmd[i] = 0x6B
    i += 1
    uart1.write(cmd[:i])
    uart2.write(cmd[:i])
    
def Emm_V5_Reset_CurPos_To_Zero(addr): # 将当前位置清零
    cmd = bytearray(4)
    cmd[0] =  addr                          # 地址
    cmd[1] =  0x0A                          # 功能码
    cmd[2] =  0x6D                          # 辅助码
    cmd[3] =  0x6B                          # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)
    
def Emm_V5_Reset_Clog_Pro(addr): # 解除堵转保护
    cmd = bytearray(4)
    cmd[0] =  addr                          # 地址
    cmd[1] =  0x0E                          # 功能码
    cmd[2] =  0x52                          # 辅助码
    cmd[3] =  0x6B                          # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)

def Emm_V5_Modify_Ctrl_Mode(addr, svF, ctrl_mode): # 调用函数修改控制模式
    cmd = bytearray(6)
    cmd[0] = addr          # 地址
    cmd[1] = 0x46          # 功能码
    cmd[2] = 0x69          # 辅助码
    cmd[3] = 0x01 if svF else 0x00  # 是否存储标志, 1为存储, 0为不存储
    cmd[4] = ctrl_mode     # 控制模式
    cmd[5] = 0x6B          # 校验字节
    uart1.write(cmd)        
    uart2.write(cmd)

def Emm_V5_En_Control(addr, state, snF): # 为地址电机使能，并启用多机同步
    cmd = bytearray(16)
    cmd[0] = addr               # 地址
    cmd[1] = 0xF3               # 功能码
    cmd[2] = 0xAB               # 辅助码
    cmd[3] = 0x01 if state else 0x00  # 使能状态，true为0x01，false为0x00
    cmd[4] = 0x01 if snF else 0x00    # 多机同步运动标志，true为0x01，false为0x00
    cmd[5] = 0x6B               # 校验字节
    uart1.write(cmd[:6])
    uart2.write(cmd[:6])


def Emm_V5_Vel_Control(addr, dir, vel, acc, snF): # 地址电机，设置方向为CW，速度为1000RPM，加速度为50，无多机同步
    cmd = bytearray(16)
    cmd[0] = addr                  # 地址
    cmd[1] = 0xF6                  # 功能码
    cmd[2] = dir                   # 方向，0为CW，其余值为CCW
    cmd[3] = (vel >> 8) & 0xFF     # 速度(RPM)高8位字节
    cmd[4] = vel & 0xFF            # 速度(RPM)低8位字节
    cmd[5] = acc                   # 加速度，注意：0是直接启动
    cmd[6] = 0x01 if snF else 0x00 # 多机同步运动标志，true为0x01，false为0x00
    cmd[7] = 0x6B                  # 校验字节
    uart1.write(cmd[:8])
    uart2.write(cmd[:8])


def Emm_V5_Pos_Control(addr, dir, vel, acc, clk, raF, snF): # 地址电机，设置方向为CW，速度为1000RPM，加速度为50，脉冲数为2000，相对运动，无多机同步
    cmd = bytearray(16)
    cmd[0] = addr                      # 地址
    cmd[1] = 0xFD                      # 功能码
    cmd[2] = dir                       # 方向
    cmd[3] = (vel >> 8) & 0xFF         # 速度(RPM)高8位字节
    cmd[4] = vel & 0xFF                # 速度(RPM)低8位字节 
    cmd[5] = acc                       # 加速度，注意：0是直接启动
    cmd[6] = (clk >> 24) & 0xFF        # 脉冲数高8位字节(bit24 - bit31)
    cmd[7] = (clk >> 16) & 0xFF        # 脉冲数(bit16 - bit23)
    cmd[8] = (clk >> 8) & 0xFF         # 脉冲数(bit8  - bit15)
    cmd[9] = clk & 0xFF                # 脉冲数低8位字节(bit0  - bit7)
    cmd[10] = 0x01 if raF else 0x00    # 相位/绝对标志，true为0x01，false为0x00
    cmd[11] = 0x01 if snF else 0x00    # 多机同步运动标志，true为0x01，false为0x00
    cmd[12] = 0x6B                     # 校验字节
    uart1.write(cmd[:13])
    uart2.write(cmd[:13])


def Emm_V5_Stop_Now(addr, snF): # 地址电机，不启用多机同步，立即停止
    cmd = bytearray(5)
    cmd[0] = addr               # 地址
    cmd[1] = 0xFE               # 功能码
    cmd[2] = 0x98               # 辅助码
    cmd[3] = 0x01 if snF else 0x00  # 多机同步运动标志，true为0x01，false为0x00
    cmd[4] = 0x6B               # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)


def Emm_V5_Synchronous_motion(addr): # 执行地址电机多机同步运动命令
    cmd = bytearray(4)
    cmd[0] = addr               # 地址
    cmd[1] = 0xFF               # 功能码
    cmd[2] = 0x66               # 辅助码
    cmd[3] = 0x6B               # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)


def Emm_V5_Origin_Set_O(addr, svF): # 为地址电机设置单圈回零零点位置并存储设置
    cmd = bytearray(5)
    cmd[0] = addr               # 地址
    cmd[1] = 0x93               # 功能码
    cmd[2] = 0x88               # 辅助码
    cmd[3] = 0x01 if svF else 0x00  # 是否存储标志，true为0x01，false为0x00
    cmd[4] = 0x6B               # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)

def Emm_V5_Origin_Modify_Params(addr, svF, o_mode, o_dir, o_vel, o_tm, sl_vel, sl_ma, sl_ms, potF): # 修改地址为 0x01 的电机回零参数
    cmd = bytearray(20)
    cmd[0] = addr                             # 地址
    cmd[1] = 0x4C                             # 功能码
    cmd[2] = 0xAE                             # 辅助码
    cmd[3] = 0x01 if svF else 0x00            # 是否存储标志，true为0x01，false为0x00
    cmd[4] = o_mode                           # 回零模式
    cmd[5] = o_dir                            # 回零方向
    cmd[6] = (o_vel >> 8) & 0xFF              # 回零速度高8位字节
    cmd[7] = o_vel & 0xFF                     # 回零速度低8位字节
    cmd[8] = (o_tm >> 24) & 0xFF              # 回零超时时间高8位字节
    cmd[9] = (o_tm >> 16) & 0xFF              # 回零超时时间次高8位字节
    cmd[10] = (o_tm >> 8) & 0xFF              # 回零超时时间次低8位字节
    cmd[11] = o_tm & 0xFF                     # 回零超时时间低8位字节
    cmd[12] = (sl_vel >> 8) & 0xFF            # 无限位碰撞检测转速高8位字节
    cmd[13] = sl_vel & 0xFF                   # 无限位碰撞检测转速低8位字节
    cmd[14] = (sl_ma >> 8) & 0xFF             # 无限位碰撞检测电流高8位字节
    cmd[15] = sl_ma & 0xFF                    # 无限位碰撞检测电流低8位字节
    cmd[16] = (sl_ms >> 8) & 0xFF             # 无限位碰撞检测时间高8位字节
    cmd[17] = sl_ms & 0xFF                    # 无限位碰撞检测时间低8位字节
    cmd[18] = 0x01 if potF else 0x00          # 上电自动触发回零，true为0x01，false为0x00
    cmd[19] = 0x6B                            # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)


def Emm_V5_Origin_Trigger_Return(addr, o_mode, snF): # 触发地址电机回零，回零模式为0，不启用多机同步标志
    cmd = bytearray(5)
    cmd[0] = addr                            # 地址
    cmd[1] = 0x9A                            # 功能码
    cmd[2] = o_mode                          # 回零模式
    cmd[3] = 0x01 if snF else 0x00           # 多机同步运动标志，true为0x01，false为0x00
    cmd[4] = 0x6B                            # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)


def Emm_V5_Origin_Interrupt(addr): # 为地址为0x01的电机发送强制中断退出回零命令
    cmd = bytearray(4)
    cmd[0] = addr      # 地址
    cmd[1] = 0x9C      # 功能码
    cmd[2] = 0x48      # 辅助码
    cmd[3] = 0x6B      # 校验字节
    uart1.write(cmd)
    uart2.write(cmd)

def Emm_V5_Receive_Data(uart):
    i = 0
    rxCmd = bytearray(128)
    lTime = cTime = utime.ticks_ms()
    while True:
        if uart.any():
            if i < 128:
                rxCmd[i] = uart.read(1)[0]
                i += 1
                lTime = utime.ticks_ms()
        else:
            cTime = utime.ticks_ms()
            if utime.ticks_diff(cTime, lTime) > 100: 
                hex_data = ' '.join(['{:02x}'.format(b) for b in rxCmd[:i]])  # 转换为16进制并保留字符前的数字0，添加空格
                hex_data = hex_data.strip('00 ')  # 去掉16进制字符串前后的无效0
                if hex_data and hex_data[0] != '0':  # 如果首字符不是0，则在首字符前添加一个0
                    hex_data = '0' + hex_data
                return hex_data, len(hex_data.replace(' ', ''))//2  # 返回数据和数据长度

def Real_time_location():
    # 定义实时位置变量
    pos1 = 0.0
    pos2 = 0.0
    Motor_Cur_Pos1 = 0.0
    Motor_Cur_Pos2 = 0.0
    # 读取电机实时位置
    Emm_V5_Read_Sys_Params(1, 'S_CPOS')
    time.sleep_ms(1)
    Emm_V5_Read_Sys_Params(2, 'S_CPOS')
    # 命令数据缓存在数组data上，长度为count
    data1, count1 = Emm_V5_Receive_Data(uart1)
    data2, count2 = Emm_V5_Receive_Data(uart2)
    #调试用
    #print("UART1 Data: ", data1, " Count: ", count1)
    #print("UART2 Data: ", data2, " Count: ", count2)
    data1_hex = data1.split()
    data2_hex = data2.split()
    if count1 > 0 and count2 > 0 and data1 and data2 and int(data1_hex[0], 16) == 0x01 and int(data1_hex[1], 16) == 0x36 and int(data2_hex[0], 16) == 0x02 and int(data2_hex[1], 16) == 0x36 :
        # 拼接成uint32_t类型
        pos1 = ustruct.unpack('>I', bytes.fromhex(''.join(data1_hex[3:7])))[0]
        pos2 = ustruct.unpack('>I', bytes.fromhex(''.join(data2_hex[3:7])))[0]
        # 角度转换
        Motor_Cur_Pos1 = float(pos1) * 360.0 / 65536.0
        Motor_Cur_Pos2 = float(pos2) * 360.0 / 65536.0
        if int(data1_hex[2], 16):
            Motor_Cur_Pos1 = -Motor_Cur_Pos1
        if int(data2_hex[2], 16):
            Motor_Cur_Pos2 = -Motor_Cur_Pos2
    else:
        pass
        
    # 调试用
    print('Motor1: {:.1f}, Motor2: {:.1f}'.format(Motor_Cur_Pos1, Motor_Cur_Pos2))  # 将浮点数转换为字符串，再打印到串口，设置转换结果为4位数，其中1位小数
    
    time.sleep_ms(1)
    