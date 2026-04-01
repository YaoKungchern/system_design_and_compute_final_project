/**
 * @file sensor.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 传感器模块的C语言实现
 * @version 0.1
 * @date 2025-11-16
 *
 * @copyright Copyright (c) 2025
 *
 */

#include "sensor.h"

/**
 * @brief 传感器初始化
 *
 * @param p_sensor    ADC传感器结构体
 * @param hadc        ADC句柄
 * @param SingleDiff  单端/差分模式
 * @param channel     ADC通道
 * @param map_func    映射函数指针
 * @param filter_func 滤波函数指针
 */
void adc_sensor_init(adc_sensor *p_sensor,
  ADC_HandleTypeDef *hadc, uint32_t SingleDiff, uint32_t channel,
  float (*map_func)(uint16_t adc_value),
  float (*filter_func)(float measured_value))
{
    p_sensor->hadc = hadc;
    p_sensor->SingleDiff = SingleDiff;
    p_sensor->channel = channel;
    p_sensor->map_func = map_func;
    p_sensor->filter_func = filter_func;
    HAL_ADCEx_Calibration_Start(p_sensor->hadc, p_sensor->SingleDiff);
    HAL_ADC_Start(p_sensor->hadc);
    HAL_ADC_PollForConversion(p_sensor->hadc, 10);
    p_sensor->filtered_value = p_sensor->measured_value = HAL_ADC_GetValue(p_sensor->hadc);  
}

/**
 * @brief 传感器刷新
 *
 * @param sensor 传感器结构体
 */
float adc_sensor_refresh (adc_sensor *p_sensor)
{
    HAL_ADC_Start(p_sensor->hadc);
    // HAL_ADC_PollForConversion(p_sensor->hadc, 10);
    p_sensor->measured_value = p_sensor->map_func(HAL_ADC_GetValue(p_sensor->hadc));
    p_sensor->filtered_value = p_sensor->filter_func(p_sensor->measured_value);
    return p_sensor->filtered_value;
}

/**
 * @brief FSK传感器初始化
 *
 * @note 注意，定时器频率应设定为TIM_CAP_FREQ，以简化计算
 * @param p_sensor    FSK传感器结构体
 * @param htim        TIM句柄
 * @param channel     TIM通道
 * @param map_func    映射函数指针
 * @param filter_func 滤波函数指针
 */
void fsk_sensor_init(fsk_sensor *p_sensor,
  TIM_HandleTypeDef *htim, uint32_t channel,
  float (*map_func)(float filtered_freq),
  float (*filter_func)(float measured_freq))
{
    p_sensor->htim = htim;
    p_sensor->channel = channel;
    p_sensor->map_func = map_func;
    p_sensor->filter_func = filter_func;
    HAL_TIM_IC_Start(p_sensor->htim, p_sensor->channel);
}

/**
 * @brief FSK传感器刷新
 *
 * @param sensor FSK传感器结构体
 */
float fsk_sensor_refresh (fsk_sensor *p_sensor)
{
    uint32_t capture = HAL_TIM_ReadCapturedValue(p_sensor->htim, p_sensor->channel);
    p_sensor->htim->Instance->CNT = 0; // 重置计数器
    HAL_TIM_IC_Start_IT(p_sensor->htim, p_sensor->channel);

    p_sensor->measured_freq = p_sensor->map_func(TIM_CAP_FREQ / capture);
    p_sensor->filtered_freq = p_sensor->filter_func(p_sensor->measured_freq);
    return p_sensor->filtered_freq;
}

/**
 * @brief PWM传感器初始化
 *
 * @note 注意，定时器频率应设定为TIM_CAP_FREQ，以简化计算
 * @param p_sensor    PWM传感器结构体
 * @param htim        TIM句柄
 * @param channel1    TIM通道1
 * @param channel2    TIM通道2
 * @param frequency   设定频率
 * @param freq_error  频率误差
 * @param map_func    映射函数指针
 * @param filter_func 滤波函数指针
 */
void pwm_sensor_init(pwm_sensor *p_sensor,
  TIM_HandleTypeDef *htim, uint32_t channel1, uint32_t channel2,
  float frequency, float freq_error,
  float (*map_func)(float filtered_freq),
  float (*filter_func)(float measured_freq))
{
    p_sensor->htim = htim;
    p_sensor->channel1 = channel1;
    p_sensor->channel2 = channel2;
    p_sensor->frequency = frequency;
    p_sensor->freq_error = freq_error;
    p_sensor->map_func = map_func;
    p_sensor->filter_func = filter_func;
    HAL_TIM_IC_Start(p_sensor->htim, p_sensor->channel1);
    HAL_TIM_IC_Start(p_sensor->htim, p_sensor->channel2);
}

/**
 * @brief PWM传感器刷新
 *
 * @param sensor PWM传感器结构体
 */
float pwm_sensor_refresh(pwm_sensor *p_sensor)
{
    uint32_t capture1 = HAL_TIM_ReadCapturedValue(p_sensor->htim, p_sensor->channel1);
    uint32_t capture2 = HAL_TIM_ReadCapturedValue(p_sensor->htim, p_sensor->channel2);
    p_sensor->htim->Instance->CNT = 0; // 重置计数器
    HAL_TIM_IC_Start_IT(p_sensor->htim, p_sensor->channel1);
    HAL_TIM_IC_Start_IT(p_sensor->htim, p_sensor->channel2);

    p_sensor->measured_freq = TIM_CAP_FREQ / capture1;
    if(p_sensor->measured_freq >= p_sensor->frequency * (1 - p_sensor->freq_error) &&
        p_sensor->measured_freq <= p_sensor->frequency * (1 + p_sensor->freq_error))
    {
        p_sensor->measured_duty = 1.0f * capture2 / (1.0f * capture1) * 100.0f;// 百分比
        p_sensor->filtered_duty = p_sensor->filter_func(p_sensor->measured_duty);
    }
    return p_sensor->filtered_duty;
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/