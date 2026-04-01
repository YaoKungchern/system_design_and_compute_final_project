/**
 * @file user_control.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 用户控制器设计源文件
 * @version 0.1
 * @date 2026-02-13
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "user_control.h"

pid force_pid;
pid position_pid;

impedance_ctrl impedance_controller;
admittance_ctrl admittance_controller;

void control_init(void)
{
    pid_init(&force_pid, F_KP, F_KI, F_KD, F_I_LIMIT, F_O_LIMIT);
    pid_init(&position_pid, P_KP, P_KI, P_KD, P_I_LIMIT, P_O_LIMIT);

    impedance_init(&impedance_controller, M, B, K, &force_pid);
    admittance_init(&admittance_controller, M, B, K, &position_pid);
}



/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/