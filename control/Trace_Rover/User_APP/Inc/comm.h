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
#include "fifo.h"
#include "pid.h"
#include "compliance.h"
#include <string.h>

void UartInit(void);
void serial_solve(uint8_t *buf);

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
    float m; // 质量系数
    float b; // 阻尼系数
    float k; // 刚度系数
}compliance_info;

typedef struct
{
    uint8_t mode; // 模式切换：
    //0x00开环 0x01位置闭环 0x02力闭环 0x03阻抗控制 0x04导纳控制 0xFF不切换模式
    float value; // 目标值
}control_info;

void write_control_info(control_info *p_control);
void write_compliance_info(compliance_info *p_compliance);
void read_compliance_info(compliance_info *p_compliance);
void write_pid_info(pid_info *p_pid);
void read_pid_info(pid_info *p_pid, uint8_t control_id);

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