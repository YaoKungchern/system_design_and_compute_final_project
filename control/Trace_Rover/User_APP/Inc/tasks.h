/**
 * @file states.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 时间片任务头文件
 * @version 0.1
 * @date 2026-02-12
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __TASKS_H
#define __TASKS_H

#pragma pack(push)
#pragma pack(1)

#include "time_slice.h"
#include "user_sensor.h"
#include "user_control.h"
#include "user_actuator.h"
#include "led.h"
#include "main.h"

void sensor_cb(void);
void f_pid_cb(void);
void p_pid_cb(void);
void impedance_cb(void);
void admittance_cb(void);
void actuator_cb(void);
void led_cb(void);

#pragma pack(pop)

#endif // !__TASKS_H
/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/