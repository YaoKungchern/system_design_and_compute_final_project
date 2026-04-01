/**
 * @file user_control.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 用户控制器设计头文件
 * @version 0.1
 * @date 2026-02-13
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __USER_CONTROL_H
#define __USER_CONTROL_H

#pragma pack(push)
#pragma pack(1)

#include "pid.h"
#include "compliance.h"
#include "main.h"

#define F_KP 0.1f
#define F_KI 0.0f
#define F_KD 0.0f
#define F_I_LIMIT 0.0f
#define F_O_LIMIT 0.0f
#define P_KP 0.1f
#define P_KI 0.0f
#define P_KD 0.0f
#define P_I_LIMIT 0.0f
#define P_O_LIMIT 0.0f
#define M 1.0f
#define B 1.0f
#define K 1.0f

void control_init(void);

#pragma pack(pop)
#endif // !__USER_CONTROL_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/