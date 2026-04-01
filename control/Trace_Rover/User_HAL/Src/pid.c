/**
 * @file pid.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief PID控制器的C语言实现
 * @version 0.1
 * @date 2025-11-15
 *
 * @copyright Copyright (c) 2025
 *
 */

#include "pid.h"
#include <math.h>

/**
 * @brief PID控制器初始化
 *
 * @param p_pid PID控制器
 * @param kp
 * @param ki
 * @param kd
 * @param i_limit
 * @param o_limit
 */
void pid_init(pid *p_pid, float kp, float ki, float kd, float i_limit, float o_limit)
{
    p_pid->kp = kp;
    p_pid->ki = ki;
    p_pid->kd = kd;

    p_pid->i_limit = i_limit;
    p_pid->o_limit = o_limit;

    p_pid->last_time = HAL_GetTick();
    p_pid->dt = 0.001f;
}

/**
 * @brief PID控制器复位
 *
 * @param p_pid PID控制器
 */
void pid_reset(pid *p_pid)
{
    p_pid->delta = 0.0f;
    p_pid->delta_i = 0.0f;
    p_pid->delta_d = 0.0f;
    p_pid->delta_l = 0.0f;
    p_pid->last_time = HAL_GetTick();
    p_pid->dt = 0.001f;
}

/**
 * @brief PID控制器更新
 *
 * @param p_pid 指定的PID控制器的指针
 * @param delta 输入的误差值更新
 * @return float
 */
float pid_refresh(pid *p_pid, float delta)
{
    p_pid->dt = fmaxf((float)(HAL_GetTick() - p_pid->last_time), 0.1f) / 1000.0f;
    p_pid->last_time = HAL_GetTick();

    p_pid->delta = delta;

    p_pid->delta_i += p_pid->delta * p_pid->dt * p_pid->ki;
    p_pid->delta_i = fmaxf(fminf(p_pid->delta_i, p_pid->i_limit), -p_pid->i_limit);

    p_pid->delta_d = (p_pid->delta - p_pid->delta_l) / p_pid->dt * p_pid->kd;
    p_pid->delta_l = p_pid->delta;

    p_pid->output = fmaxf(fminf(
        p_pid->kp * p_pid->delta + p_pid->delta_i + p_pid->delta_d, p_pid->o_limit
    ), -p_pid->o_limit);
    
    return p_pid->output;
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/