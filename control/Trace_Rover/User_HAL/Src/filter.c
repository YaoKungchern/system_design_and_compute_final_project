/**
 * @file filter.c
 * @author 沈一祺 (qdsyqaaa@gmail.com)
 * @brief 使用C实现的一些滤波器函数
 * @version 0.1
 * @date 2024-03-11
 *
 * @copyright Copyright (c) 2024
 *
 */

#include "filter.h"


/**
 * @brief 卡尔曼滤波器初始化
 *
 * @param p_kf 卡尔曼滤波器
 * @param Q  过程噪声协方差；环境噪声越大，Q越大
 * @param R  测量噪声协方差；测量误差越大，R越大
 */
void kalman_filter_Init(kalman_filter *p_kf, float Q, float R)
{
    p_kf->Q = Q;
    p_kf->R = R;

    p_kf->x_est = 0.0; // 估计值
    p_kf->p     = 1.0; // 方差
    p_kf->k     = 0.0; // 卡尔曼增益
}

/**
 * @brief 卡尔曼滤波器更新
 *
 * @param p_kf 卡尔曼滤波器
 * @param measured_value 测量值
 * @return float 校验值
 */
float kalman_filter_Refresh(kalman_filter *p_kf, float measured_value)
{
    p_kf->measured_value = measured_value;

    // 预测
    float x_pred = p_kf->x_est;
    float p_pred = p_kf->p + p_kf->Q;

    // 更新
    p_kf->k     = p_pred / (p_pred + p_kf->R);
    p_kf->x_est = x_pred + p_kf->k * (measured_value - x_pred);
    p_kf->p     = (1 - p_kf->k) * p_pred;

    // p_kf->checked_value = p_kf->x_est;
    return p_kf->checked_value = p_kf->x_est;
}

/**
 * @brief 均值滤波器初始化
 *
 * @param p_mf 均值滤波器
 * @param length 队列长度
 * @param p_fifo 队列缓冲区起始地址
 */
void mean_filter_Init(mean_filter *p_mf, uint8_t length, float *p_fifo)
{
    p_mf->sum = 0.0f;
    if (length > 0)
        p_mf->length = length;
    else
        p_mf->length = 0;
    p_mf->fifo   = p_fifo;
    p_mf->fifo_p = 0;

    for (uint8_t i = 0; i < length; i++)
    {
        p_mf->fifo[i] = 0;
    }
}

/**
 * @brief 均值滤波器更新
 *
 * @param p_mf 均值滤波器
 * @param measured_value 测量值
 */
float mean_filter_Refresh(mean_filter *p_mf, float measured_value)
{
    // float sum = 0;

    // p_mf->fifo_p++;
    // if (p_mf->fifo_p >= p_mf->length)
    //     p_mf->fifo_p = 0;
    p_mf->fifo_p = (p_mf->fifo_p + 1) % p_mf->length;
    p_mf->sum -= p_mf->fifo[p_mf->fifo_p];
    p_mf->fifo[p_mf->fifo_p] = measured_value;
    p_mf->sum += measured_value;

    // for (uint8_t i = 0; i < p_mf->length; i++)
    // {
    //     sum += p_mf->fifo[i];
    // }
    // p_mf->sum = sum;

    return p_mf->mean = p_mf->sum / p_mf->length;
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/