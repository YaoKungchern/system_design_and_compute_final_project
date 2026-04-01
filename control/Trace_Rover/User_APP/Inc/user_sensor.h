/**
 * @file user_sensor.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 用户传感器设计头文件
 * @version 0.1
 * @date 2026-02-13
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __USER_SENSOR_H
#define __USER_SENSOR_H

#pragma pack(push)
#pragma pack(1)

#include "filter.h"
#include "sensor.h"
#include "main.h"

void sensor_init(void);
void sensor_refresh(void);

#pragma pack(pop)
#endif // !__USER_SENSOR_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/