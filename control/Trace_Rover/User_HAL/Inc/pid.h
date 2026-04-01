/**
 * @file pid.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief PID控制器的C语言实现
 * @version 0.1
 * @date 2025-11-15
 *
 * @copyright Copyright (c) 2025
 *
 */
#ifndef __PID_H
#define __PID_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"
#include <math.h>

/**
 * @brief PID控制器
 *
 */
typedef struct
{
    float kp;       // 比例系数
    float ki;       // 积分系数
    float kd;       // 微分系数

    float last_time; // 上一次采样时间
    float dt;        // 采样时间间隔

    float i_limit; // 积分限幅
    float o_limit; // 输出限幅

    float delta;   // 误差
    float delta_i; // 积分项
    float delta_d; // 微分项
    float delta_l; // 上一次误差

    float output; // 控制器输出
} pid;

void pid_init(pid *p_pid, float kp, float ki, float kd, float i_limit, float o_limit);
void pid_reset(pid *p_pid);
float pid_refresh(pid *p_pid, float delta);


#pragma pack(pop)

#endif // !__PID_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/