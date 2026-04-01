/**
 * @file time_slice.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 使用C实现时间片轮询算法
 * @version 0.1
 * @date 2025-11-14
 *
 * @copyright Copyright (c) 2025
 *
 */

 #include "time_slice.h"

 /**
 * @brief 时间片任务初始化
 *
 * @param ts 时间片结构体
 * @param interval  时间间隔，单位：ms
 * @param callback  时间片任务回调函数
 */
void time_slice_init(time_slice *ts, uint16_t interval, void (*callback)(void))
{
    ts->last_time = HAL_GetTick();
    ts->interval = interval;
    ts->callback = callback;
}

/**
 * @brief 时间片任务运行
 *
 * @param ts 时间片结构体指针
 */
void time_slice_run(time_slice *ts)
{
    if (HAL_GetTick() - ts->last_time >= ts->interval)
    {
        ts->last_time = HAL_GetTick();
        ts->callback();
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