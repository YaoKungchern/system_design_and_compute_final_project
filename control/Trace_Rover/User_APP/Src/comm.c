/**
 * @file comm.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 通信模块源文件
 * @version 0.1
 * @date 2025-12-03
 *
 * @copyright Copyright (c) 2025
 *
 */

#include "comm.h"

Fifo uart1_fifo;
Fifo uart2_fifo;

uint8_t tx_buffer[64];
uint8_t uart3_buffer[64];
uint8_t uart3_ptr;
uint8_t uart3_cnt;
uint8_t uart3_flag;

extern ctrl_state control_state;
extern vector2D control_value;


extern pid vel_pid[4];
extern pid pos_pid[4];

extern ultrasonic_sensor ultrasonic_sys;
extern base_sys2D rover_pos;
extern base_sys2D rover_vel;

extern dc_motor motor[4];

extern mecanum mecanum_pos;
extern mecanum mecanum_vel;

/*数据帧格式：
头(2字节) + 命令字(1字节) + 数据区(n字节) + 校验字节(1字节) + 尾(2字节)
*/

/**
 * @brief 串口初始化
 *
 */
void UartInit(void)
{
    uint8_t head_uart2[2] = {0xfa, 0xaf};
    uint8_t end_uart2[2]  = {0xfb, 0xbf};
    uint8_t head_uart1[1] = {STEP_MOTOR_ID};
    uint8_t end_uart1[1]  = {STEP_MOTOR_CHECK};

    Fifo_Init(&uart2_fifo, 200, 2, 2, head_uart2, end_uart2);
    Fifo_Init(&uart1_fifo, 200, 1, 1, head_uart1, end_uart1);

    HAL_UART_Receive_IT(&huart2, (uint8_t *)&(uart2_fifo.fifo[uart2_fifo.pointer]), 1);
    HAL_UART_Receive_IT(&huart1, (uint8_t *)&(uart1_fifo.fifo[uart1_fifo.pointer]), 1);
    HAL_UART_Receive_IT(&huart3, (uint8_t *)&(uart3_buffer[uart3_ptr]), 1);
}

/**
 * @brief 串口中断处理函数
 *
 * @param huart 串口设备
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    static FIFO_RESAULT ret;
    if (huart == &huart1)
    {
        ret = Fifo_RefreshExternal(&uart1_fifo);
        if (ret == FIFO_RECEIVED)
        {
            // 处理数据
            uart1_solve(uart1_fifo.fifo);
        }
        // 再次接收
        HAL_UART_Receive_IT(&huart1, (uint8_t *)&(uart1_fifo.fifo[uart1_fifo.pointer]), 1);
    }
    if (huart == &huart2)
    {
        ret = Fifo_RefreshExternal(&uart2_fifo);
        if (ret == FIFO_RECEIVED)
        {
            uart2_solve(uart2_fifo.fifo);
        }
        // 再次接收
        HAL_UART_Receive_IT(&huart2, (uint8_t *)&(uart2_fifo.fifo[uart2_fifo.pointer]), 1);
    }
    if(huart == &huart3)
    {
        if(uart3_buffer[uart3_ptr] == 0xFF)
        {
            uart3_ptr = 0;
            uart3_cnt = 0;
            uart3_flag = 1;
        }
        if(uart3_flag)
        {
            uart3_cnt++;
        }
        if(uart3_cnt == 4)
        {
            if(uart3_buffer[3] == (uint8_t)((0xFF+uart3_buffer[1]+uart3_buffer[2]) & 0xFF))
            {
				float dis = (float)(uart3_buffer[1]<<8 | uart3_buffer[2]) / 1000.0f;
				if(dis < 1.0f)
				{
					ultrasonic_sys.distance = dis;
					tx_buffer[0]=STEP_MOTOR_ID;
					tx_buffer[1]=0x36;
					tx_buffer[2]=STEP_MOTOR_CHECK;
					HAL_UART_Transmit_IT(ultrasonic_sys.huart_stepmotor, tx_buffer, 3);
					uart3_flag = 0;
					uart3_cnt = 0;
					uart3_ptr = 0;
//					ultrasonic_info info;
//					write_ultrasonic_info(&info);
				}
            }
        }
        if(uart3_ptr > 63) uart3_ptr = 0;
        else uart3_ptr++;
        HAL_UART_Receive_IT(&huart3, (uint8_t *)&(uart3_buffer[uart3_ptr]), 1);
    }
}

/**
 * @brief 异或校验函数
 *
 * @param buf 数据缓冲区
 * @param len 数据长度
 * @return uint8_t 校验值
 */
uint8_t check_data(uint8_t *buf, int len)
{
    uint8_t check = 0;
    for (uint16_t i = 0; i < len; i++)
    {
        check ^= buf[i];
    }
    return check;
}

/**
 * @brief 串口数据处理函数
 *
 * @param buf 接收缓冲区
 */
void uart2_solve(uint8_t *buf)
{
  switch(buf[2])
  {
    case 0x4D: // 运动控制指令
    {
        control_info control;
        memcpy(&control, buf + 3, sizeof(control_info));
        write_control_info(&control);
        break;
    }
    case 0x4E: // 导航信息
    {
        navigation_info navigation;
        if(buf[3] == 0x01){
            read_navigation_info(&navigation);}
        if(buf[3] == 0x00){
        memcpy(&navigation, buf + 3, sizeof(navigation_info));
        write_navigation_info(&navigation);}
      break;
    }
    case 0x50: // PID控制器信息
    {
        pid_info pid;
        if(buf[3] == 0x01)
            read_pid_info(&pid, buf[4]);
        if(buf[3] == 0x00){
            memcpy(&pid, buf + 3, sizeof(pid_info));
            write_pid_info(&pid);}
      break;
    }
    // case 0x55: // 超声波信息
    // {
    //     ultrasonic_info ultrasonic;
    //     if(buf[3] == 1 && buf[5] == check_data(buf+2, 3))
    //         write_ultrasonic_info(&ultrasonic);
    //   break;
    // }
    default:
      break;
  }
}

void uart1_solve(uint8_t *buf)
{
    if(buf[1] == 0x36 && buf[7] == STEP_MOTOR_CHECK)
    {
        uint32_t angle;
        memcpy(&angle, buf + 3, sizeof(uint32_t));
        ultrasonic_sys.angle = -(buf[2]*2-1) * (angle * 2 * PI) / 65536.0f;
        ultrasonic_sys.angle = angle_correct_rad(ultrasonic_sys.angle-ANGLE_DIFF);
        ultrasonic_info ultrasonic_buffer;
        write_ultrasonic_info(&ultrasonic_buffer);
    }
}

void write_control_info(control_info *p_control)
{
    if(control_state != p_control->mode && p_control->mode != 0xFF)
        control_state = p_control->mode;
    control_value = p_control->value;
}

void write_navigation_info(navigation_info *p_navigation)
{
    rover_pos.vector = p_navigation->position;
    vector2matrix(&rover_pos);

    mecanum_inverse_kinematics(&mecanum_pos, p_navigation->position);
    for(uint8_t i = 0; i < 4; i++)
    {
        motor[i].real_position = mecanum_pos.wheels[i];
    }
}

void read_navigation_info(navigation_info *p_navigation)
{
    p_navigation->rw_flag = 1;
    p_navigation->position = rover_pos.vector;
    p_navigation->velocity = rover_vel.vector;
    memcpy(tx_buffer, uart2_fifo.head, 2);
    tx_buffer[2] = 0x4E;
    memcpy(tx_buffer + 3, p_navigation, sizeof(navigation_info));
    tx_buffer[3 + sizeof(navigation_info)] = check_data(tx_buffer + 2, sizeof(navigation_info) + 1);
    memcpy(tx_buffer + 4 + sizeof(navigation_info), uart2_fifo.end, 2);
    HAL_UART_Transmit_IT(&huart2, tx_buffer, 6 + sizeof(navigation_info));
}

void write_pid_info(pid_info *p_pid)
{
    if(p_pid->control_id == 0x01) // 位置环
    {
        for(uint8_t i = 0; i < 4; i++)
        {
            pos_pid[i].kp = p_pid->kp;
            pos_pid[i].ki = p_pid->ki;
            pos_pid[i].kd = p_pid->kd;
            pos_pid[i].i_limit = p_pid->i_limit;
            pos_pid[i].o_limit = p_pid->o_limit;
        }
    }
    else if(p_pid->control_id == 0x00) // 速度环
    {
        for(uint8_t i = 0; i < 4; i++)
        {
            vel_pid[i].kp = p_pid->kp;
            vel_pid[i].ki = p_pid->ki;
            vel_pid[i].kd = p_pid->kd;
            vel_pid[i].i_limit = p_pid->i_limit;
            vel_pid[i].o_limit = p_pid->o_limit;
        }
    }
}

void read_pid_info(pid_info *p_pid, uint8_t control_id)
{
    p_pid->rw_flag = 1;
    p_pid->control_id = control_id;
    if(p_pid->control_id == 0x01) // 位置环
    {
        p_pid->delta = pos_pid[0].delta_i;
        p_pid->delta_i = pos_pid[0].delta_i;
        p_pid->delta_d = pos_pid[0].delta_d;
        p_pid->kp = pos_pid[0].kp;
        p_pid->ki = pos_pid[0].ki;
        p_pid->kd = pos_pid[0].kd;
        p_pid->i_limit = pos_pid[0].i_limit;
        p_pid->o_limit = pos_pid[0].o_limit;
    }
    else if(p_pid->control_id == 0x00) // 速度环
    {
        p_pid->delta = vel_pid[0].delta_i;
        p_pid->delta_i = vel_pid[0].delta_i;
        p_pid->delta_d = vel_pid[0].delta_d;
        p_pid->kp = vel_pid[0].kp;
        p_pid->ki = vel_pid[0].ki;
        p_pid->kd = vel_pid[0].kd;
        p_pid->i_limit = vel_pid[0].i_limit;
        p_pid->o_limit = vel_pid[0].o_limit;
    }
    memcpy(tx_buffer, uart2_fifo.head, 2);
    tx_buffer[2] = 0x50;
    memcpy(tx_buffer + 3, p_pid, sizeof(pid_info));
    tx_buffer[3 + sizeof(pid_info)] = check_data(tx_buffer + 2, sizeof(pid_info) + 1);
    memcpy(tx_buffer + 4 + sizeof(pid_info), uart2_fifo.end, 2);
    HAL_UART_Transmit_IT(&huart2, tx_buffer, 6 + sizeof(pid_info));
}

void write_ultrasonic_info(ultrasonic_info *p_ultrasonic)
{
        float x = cos(ultrasonic_sys.angle) * ultrasonic_sys.distance;
        float y = sin(ultrasonic_sys.angle) * ultrasonic_sys.distance;
        base_sys2D barrier_rover;
        base_sys2D barrier_base;
        base_sys_set_by_vector(&barrier_rover, x, y, 0.0f);
        base2world(&rover_pos, &barrier_rover, &barrier_base);
        ultrasonic_sys.x = barrier_base.vector.x;
        ultrasonic_sys.y = barrier_base.vector.y;
        p_ultrasonic->distance = ultrasonic_sys.distance;
        p_ultrasonic->angle = ultrasonic_sys.angle;
        p_ultrasonic->x = ultrasonic_sys.x;
        p_ultrasonic->y = ultrasonic_sys.y;
        memcpy(tx_buffer, uart2_fifo.head, 2);
        tx_buffer[2] = 0x55;
        memcpy(tx_buffer + 3, p_ultrasonic, sizeof(ultrasonic_info));
        tx_buffer[3 + sizeof(ultrasonic_info)] = check_data(tx_buffer + 2, sizeof(ultrasonic_info) + 1);
        memcpy(tx_buffer + 4 + sizeof(ultrasonic_info), uart2_fifo.end, 2);
        HAL_UART_Transmit_IT(&huart2, tx_buffer, 6 + sizeof(ultrasonic_info));

}


/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/