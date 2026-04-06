/**
 * @file mecanum.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 麦克纳姆轮的运动学模型
 * @version 0.1
 * @date 2026-03-31
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "mecanum.h"

/**
 * @brief 初始化麦卡纳姆轮的运动学模型
 * 
 * @param m 麦卡纳姆轮的运动学模型
 */
void mecanum_init(mecanum *m)
{
    for (int i = 0; i < 4; i++)
    {
        m->wheels[i] = 0.0f;
    }
    m->chassis.x = 0.0f;
    m->chassis.y = 0.0f;
    m->chassis.r = 0.0f;
}

/**
 * @brief 前向运动学模型
 * 
 * @param m 麦卡纳姆轮的运动学模型
 * @param wheels 轮子信息数组
 */
void mecanum_forward_kinematics(mecanum *m, float wheels[4])
{
    m->chassis.x = (wheels[0] + wheels[1] + wheels[2] + wheels[3]) * WHEEL_RADIUS / 4.0f;
    m->chassis.y = (-wheels[0] + wheels[1] - wheels[2] + wheels[3]) * WHEEL_RADIUS / 4.0f;
    m->chassis.r = (-wheels[0] + wheels[1] + wheels[2] - wheels[3]) * WHEEL_RADIUS / (4.0f * (CHASSIS_LENGTH + CHASSIS_WIDTH));

    m->wheels = wheels;
}

/**
 * @brief 逆向运动学模型
 * 
 * @param m 麦卡纳姆轮的运动学模型
 * @param chassis 机器人底盘信息
 */
void mecanum_inverse_kinematics(mecanum *m, vector2D chassis)
{
    m->wheels[0] = (chassis.x - chassis.y - (CHASSIS_LENGTH + CHASSIS_WIDTH) * chassis.r) / WHEEL_RADIUS;
    m->wheels[1] = (chassis.x + chassis.y + (CHASSIS_LENGTH + CHASSIS_WIDTH) * chassis.r) / WHEEL_RADIUS;
    m->wheels[2] = (chassis.x - chassis.y + (CHASSIS_LENGTH + CHASSIS_WIDTH) * chassis.r) / WHEEL_RADIUS;
    m->wheels[3] = (chassis.x + chassis.y - (CHASSIS_LENGTH + CHASSIS_WIDTH) * chassis.r) / WHEEL_RADIUS;

    m->chassis = chassis;
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/