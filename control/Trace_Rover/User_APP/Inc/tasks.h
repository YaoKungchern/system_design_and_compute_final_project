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
#include "main.h"
#include "tim.h"
#include "comm.h"
#include "actuator.h"
#include "ultrasonic.h"

void motor_cb(void);
void nav_cb(void);
void tasks_init(void);
void tasks_run(void);

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