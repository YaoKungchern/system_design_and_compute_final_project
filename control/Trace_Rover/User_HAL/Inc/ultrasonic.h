/**
 * @file ultrasonic.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 超声波传感器的C语言抽象
 * @version 0.1
 * @date 2026-04-06
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __ULTRASONIC_H
#define __ULTRASONIC_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"
#include "coordinate2d.h"

#define STEP_MOTOR_ID 0x01 ///< 步进电机ID
#define STEP_MOTOR_CHECK 0x6B ///< 步进电机校验和

#define ANGLE_DIFF 0.0f ///< 角度差值，单位为弧度


typedef struct {
    UART_HandleTypeDef *huart_ultrasonic; ///< 超声波传感器使用的UART句柄
    UART_HandleTypeDef *huart_stepmotor; ///< 步进电机使用的UART句柄
    float distance; ///< 测量到的距离值，单位为米
    float angle; ///< 角度值，单位为度
    float x; ///< 世界坐标系的x坐标，单位为米
    float y; ///< 世界坐标系的y坐标，单位为米
} ultrasonic_sensor;

void ultrasonic_init(ultrasonic_sensor *ultrasonic, UART_HandleTypeDef *huart_ultrasonic, UART_HandleTypeDef *huart_stepmotor, uint16_t rotate_speed);

#pragma pack(pop)
#endif /* __ULTRASONIC_H */

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/