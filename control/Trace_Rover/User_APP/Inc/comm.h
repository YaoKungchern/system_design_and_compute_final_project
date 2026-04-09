/**
 * @file comm.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 通信模块头文件
 * @version 0.1
 * @date 2025-12-03
 *
 * @copyright Copyright (c) 2025
 *
 */

#ifndef __COMM_H
#define __COMM_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"
#include "usart.h"
#include "fifo.h"
#include "pid.h"
#include "actuator.h"
#include "ultrasonic.h"
#include "mecanum.h"
#include <string.h>

void UartInit(void);
void uart2_solve(uint8_t *buf);
void uart1_solve(uint8_t *buf);

typedef enum {
    OPEN_LOOP_ROVER_BASE = 0x00,
    SPEED_LOOP_ROVER_BASE = 0x01,
    SPEED_LOOP_WORLD_BASE = 0x02,
    POSITION_LOOP_ROVER_BASE = 0x03,
    POSITION_LOOP_WORLD_BASE = 0x04,
} ctrl_state;

typedef struct
{
    uint8_t rw_flag; // 读写标志位，0表示写，1表示读
    uint8_t control_id; // 控制ID
    float delta;   // 误差
    float delta_i; // 积分项
    float delta_d; // 微分项
    float kp; // 比例系数
    float ki; // 积分系数
    float kd; // 微分系数
    float i_limit; // 积分限幅
    float o_limit; // 输出限幅
}pid_info;

typedef struct
{
    uint8_t rw_flag; // 读写标志位，0表示写，1表示读
    vector2D position; // 机器人位置
    vector2D velocity; // 机器人速度
}navigation_info;

typedef struct
{
    uint8_t mode; // 模式切换：
    //模式切换：0x00.开环 0x01.速度闭环（机器人坐标系） 0x02.速度闭环（世界坐标系） 0x03.位置闭环（机器人坐标系） 0x04.位置闭环（世界坐标系）  0xFF.不切换模式
    vector2D value; // 目标值
}control_info;

typedef struct
{
    float distance; // 距离值，单位为米
    float angle; // 角度值，单位为弧度
    float x; // X坐标，单位为米
    float y; // Y坐标，单位为米
} ultrasonic_info;

void write_control_info(control_info *p_control);
void write_navigation_info(navigation_info *p_navigation);
void read_navigation_info(navigation_info *p_navigation);
void write_pid_info(pid_info *p_pid);
void read_pid_info(pid_info *p_pid, uint8_t control_id);
void write_ultrasonic_info(ultrasonic_info *p_ultrasonic);

#pragma pack(pop)

#endif // !__COMM_H
/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/