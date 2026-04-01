/**
 * @file user_actuator.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 用户执行器设计头文件
 * @version 0.1
 * @date 2026-02-13
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __USER_ACTUATOR_H
#define __USER_ACTUATOR_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"
#include "actuator.h"

void claw_actuator_init(void);
void claw_actuator_refresh(float input);

#pragma pack(pop)
#endif // !__USER_ACTUATOR_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/