/**
 * @file mecanum.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 麦克纳姆轮的运动学模型
 * @version 0.1
 * @date 2026-03-31
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __MECANUM_H
#define __MECANUM_H

#pragma pack(push)
#pragma pack(1)

#define WHEEL_RADIUS 0.05f // 轮子半径，单位为米
#define CHASSIS_LENGTH 0.3f  // 机器人长度，单位为米
#define CHASSIS_WIDTH 0.2f   // 机器人宽度，单位为米

#include "coordinate2D.h"

typedef struct {
    float wheels[4]; // 四个轮子的信息
    vector2D chassis; // 机器人底盘的信息
} mecanum;

void mecanum_init(mecanum *m);
void mecanum_forward_kinematics(mecanum *m, float wheel[4]);
void mecanum_inverse_kinematics(mecanum *m, vector2D chassis);

#pragma pack(pop)

#endif /* __COORDINATE2D_H */

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/