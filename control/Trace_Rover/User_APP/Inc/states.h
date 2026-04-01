/**
 * @file states.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 状态机头文件
 * @version 0.1
 * @date 2026-02-12
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __STATES_H
#define __STATES_H

#pragma pack(push)
#pragma pack(1)

#include "fsm.h"
#include "comm.h"
#include "tasks.h"

void init(void);
void state_machine_run(void);

#pragma pack(pop)

#endif // !__LED_H
/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/