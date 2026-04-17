/**
 * @file ultrasonic.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 超声波传感器的C语言抽象
 * @version 0.1
 * @date 2026-04-06
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "ultrasonic.h"

/**
 * @brief 超声波传感器初始化函数
 * @param ultrasonic 超声波传感器对象指针
 * @param huart_ultrasonic 超声波传感器使用的UART句柄
 * @param huart_stepmotor 步进电机使用的UART句柄
 * @param rotate_speed 旋转速度，单位为rpm
 */
 void ultrasonic_init(ultrasonic_sensor *ultrasonic, 
    UART_HandleTypeDef *huart_ultrasonic, UART_HandleTypeDef *huart_stepmotor,
    uint16_t rotate_speed)
 {
     ultrasonic->huart_ultrasonic = huart_ultrasonic;
     ultrasonic->huart_stepmotor = huart_stepmotor;
     ultrasonic->distance = 0.0f;
     ultrasonic->angle = 0.0f;
     ultrasonic->x = 0.0f;
     ultrasonic->y = 0.0f;

//     uint8_t init_cmd[6] = {STEP_MOTOR_ID, 0xF3, 0xAB, 0x01, 0x00, STEP_MOTOR_CHECK}; // 初始化命令
//     HAL_UART_Transmit_IT(ultrasonic->huart_stepmotor, init_cmd, 6);
     HAL_Delay(1000); // 等待电机初始化完成
     uint8_t speed_h = (rotate_speed >> 8) & 0xFF;
     uint8_t speed_l = rotate_speed & 0xFF;
     uint8_t start_cmd[8] = {STEP_MOTOR_ID, 0xF6, 0x01, speed_h, speed_l,0x00, 0x00, STEP_MOTOR_CHECK}; // 启动命令
	 HAL_UART_Transmit_IT(ultrasonic->huart_stepmotor, start_cmd, 8);
	 HAL_Delay(100);
	 HAL_UART_Transmit_IT(ultrasonic->huart_stepmotor, start_cmd, 8);
 }

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/