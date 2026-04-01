/**
 * @file user_actuator.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 用户执行器设计源文件
 * @version 0.1
 * @date 2026-02-13
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "user_actuator.h"

void claw_actuator_init(void)
{
    // 在此处添加执行器初始化代码
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_7, GPIO_PIN_RESET);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);
}

uint16_t claw_actuator_map(float input)
{
    return (uint16_t)(0.5f + input); // 直接映射
}

void claw_actuator_refresh(float input)
{
    // 在此处添加执行器刷新代码
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_7, input > 0);
    uint16_t pulse = claw_actuator_map(input);
    pulse = output_limit(0, 19999, pulse);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, pulse);
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/