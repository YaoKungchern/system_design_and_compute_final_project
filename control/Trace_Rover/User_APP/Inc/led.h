/**
 * @file led.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief LED模块头文件
 * @version 0.1
 * @date 2025-12-15
 *
 * @copyright Copyright (c) 2025
 *
 */

#ifndef __LED_H
#define __LED_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"

#define LED_BLACK 0x00
#define LED_BLUE  0x01
#define LED_RED   0x02
#define LED_GREEN 0x04
#define LED_YELLOW (LED_RED | LED_GREEN)
#define LED_CYAN   (LED_GREEN | LED_BLUE)
#define LED_MAGENTA (LED_RED | LED_BLUE)
#define LED_WHITE  (LED_RED | LED_GREEN | LED_BLUE)

void led_set_color(uint8_t color);

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