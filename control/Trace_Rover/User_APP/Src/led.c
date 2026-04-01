/**
 * @file led.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief LED模块源文件
 * @version 0.1
 * @date 2025-12-15
 *
 * @copyright Copyright (c) 2025
 *
 */

#include "led.h"

void led_set_color(uint8_t color)
{
  if(color <= 0x07)
  {
    HAL_GPIO_WritePin(GPIOB, 0XE000, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOB, color << 13, GPIO_PIN_RESET);
  }
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/