/**
 * @file time_slice.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 使用C实现时间片轮询算法
 * @version 0.1
 * @date 2025-11-14
 *
 * @copyright Copyright (c) 2025
 *
 */
#ifndef __TIME_SLICE_H
#define __TIME_SLICE_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"

/**
 * @brief delay no more
 *
 */
typedef struct
{
    uint32_t last_time; ///< 上次时间戳
    uint16_t interval; ///< 时间间隔
    void     (*callback)(void); ///< 回调函数指针
} time_slice;

void time_slice_init(time_slice *ts, uint16_t interval, void (*callback)(void));
void time_slice_run(time_slice *ts);

#pragma pack(pop)


#endif // !__TIME_SLICE_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/