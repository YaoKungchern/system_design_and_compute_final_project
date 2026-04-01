/**
 * @file sensor.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief STM32平台传感器的C语言抽象
 * @version 0.1
 * @date 2025-11-16
 *
 * @copyright Copyright (c) 2025
 *
 */

#ifndef __SENSOR_H
#define __SENSOR_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"

#define TIM_CAP_FREQ 1000000.0f

/**
 * @brief ADC传感器数据结构体
 *
 * @param hadc ADC句柄
 * @param SingleDiff 单端/差分模式
 * @param channel ADC通道
 * @param measured_value 测量值
 * @param filtered_value 滤波值
 * @param map_func 映射函数指针
 * @param filter_func 滤波函数指针
 */
typedef struct
{
    ADC_HandleTypeDef *hadc; // ADC句柄
    uint32_t SingleDiff; // 单端/差分模式
    uint32_t channel; // ADC通道
    float measured_value; // 测量值
    float filtered_value; // 滤波值

    float (*map_func)(uint16_t adc_value); // 映射函数指针
    float (*filter_func)(float measured_value); // 滤波函数指针
} adc_sensor;

void adc_sensor_init(adc_sensor *p_sensor, 
  ADC_HandleTypeDef *hadc, uint32_t SingleDiff, uint32_t channel,
  float (*map_func)(uint16_t adc_value),
  float (*filter_func)(float measured_value));

float adc_sensor_refresh (adc_sensor *p_sensor);

/**
 * @brief FSK传感器数据结构体
 *
 * @param htim TIM句柄
 * @param channel TIM通道
 * @param measured_freq 测量频率
 * @param filtered_freq 滤波频率
 * @param map_func 映射函数指针
 * @param filter_func 滤波函数指针
 */
typedef struct
{
    TIM_HandleTypeDef *htim; // TIM句柄
    uint32_t channel; // TIM通道
    float measured_freq; // 测量频率
    float filtered_freq; // 滤波频率

    float (*map_func)(float filtered_freq); // 映射函数指针
    float (*filter_func)(float measured_freq); // 滤波函数指针
} fsk_sensor;

void fsk_sensor_init(fsk_sensor *p_sensor,
  TIM_HandleTypeDef *htim, uint32_t channel,
  float (*map_func)(float filtered_freq),
  float (*filter_func)(float measured_freq));

float fsk_sensor_refresh (fsk_sensor *p_sensor);

/**
 * @brief PWM传感器数据结构体
 *
 * @param htim TIM句柄
 * @param channel TIM通道
 * @param measured_freq 测量频率
 * @param frequency 频率
 * @param freq_error 频率误差
 * @param measured_duty 测量占空比
 * @param filtered_duty 滤波占空比
 * @param map_func 映射函数指针
 * @param filter_func 滤波函数指针
 */
typedef struct
{
    TIM_HandleTypeDef *htim; // TIM句柄
    uint32_t channel1; // TIM通道1
    uint32_t channel2; // TIM通道2
    float measured_freq; // 测量频率
    float frequency; // 设定频率
    float freq_error; // 频率误差
    float measured_duty; // 测量占空比
    float filtered_duty; // 滤波占空比

    float (*map_func)(float filtered_duty); // 映射函数指针
    float (*filter_func)(float measured_duty); // 滤波函数指针
} pwm_sensor;

void pwm_sensor_init(pwm_sensor *p_sensor,
  TIM_HandleTypeDef *htim, uint32_t channel1, uint32_t channel2,
  float frequency, float freq_error,
  float (*map_func)(float filtered_duty),
  float (*filter_func)(float measured_duty));

float pwm_sensor_refresh (pwm_sensor *p_sensor);

#pragma pack(pop)

#endif // !__SENSOR_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/