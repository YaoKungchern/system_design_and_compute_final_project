/**
 * @file filter.h
 * @author 沈一祺 (qdsyqaaa@gmail.com)
 * @brief 使用C实现的一些滤波器函数
 * @version 0.1
 * @date 2024-03-15
 *
 * @copyright Copyright (c) 2024
 *
 */
#ifndef __FILTER_H
#define __FILTER_H


#pragma pack(push)
#pragma pack(1)

#ifdef MAIN_H
#include "main.h"
#else
#include <stdint.h>
#endif

/**
 * @brief 卡尔曼滤波器
 *
 */
typedef struct {
    float Q; ///< 过程噪声协方差
    float R; ///< 测量噪声协方差

    float measured_value; ///< 测量值
    float checked_value;  ///< 校验值

    float x_est; ///< 估计值
    float p;     ///< 方差
    float k;     ///< 卡尔曼增益
} kalman_filter;

void  kalman_filter_Init(kalman_filter *p_kf, float Q, float R);
float kalman_filter_Refresh(kalman_filter *p_kf, float measured_value);


/**
 * @brief 均值滤波器
 *
 */
typedef struct {
    uint8_t  length; ///< 数据队列长度
    float    *fifo;   ///< 数据队列
    uint32_t fifo_p; ///< 指针
    float    sum;    ///< 队列元素和
    float    mean;   ///< 队列元素均值
} mean_filter;

void  mean_filter_Init(mean_filter *p_mf, uint8_t length, float *p_fifo);
float mean_filter_Refresh(mean_filter *p_mf, float measured_value);


#pragma pack(pop)


#endif // !__FILTER_H