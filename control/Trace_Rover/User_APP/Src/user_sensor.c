/**
 * @file user_sensor.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 用户传感器设计源文件
 * @version 0.1
 * @date 2026-02-13
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "user_sensor.h"

kalman_filter touch_sensor_1_kalman_filter;
mean_filter touch_sensor_1_mean_filter;
float touch_sensor_1_mean_filter_fifo[10];
adc_sensor touch_sensor_1;

kalman_filter touch_sensor_2_kalman_filter;
mean_filter touch_sensor_2_mean_filter;
float touch_sensor_2_mean_filter_fifo[10];
adc_sensor touch_sensor_2;

kalman_filter position_sensor_kalman_filter;
mean_filter position_sensor_mean_filter;
float position_sensor_mean_filter_fifo[10];
adc_sensor position_sensor;

float touch_sensor_map_function(uint16_t adc_value)
{
    return (float)adc_value * 3.3f / 4095.0f;
    // 在此处添加ADC值到物理量的映射代码
}

float position_sensor_map_function(uint16_t adc_value)
{
    return (float)adc_value * 3.3f / 4095.0f;
    // 在此处添加ADC值到物理量的映射代码
}

float touch_sensor_1_filter_function(float measured_value)
{
    // 在此处添加对测量值进行滤波的代码
    float checked_value;
    checked_value = kalman_filter_Refresh(&touch_sensor_1_kalman_filter, measured_value);
    checked_value = mean_filter_Refresh(&touch_sensor_1_mean_filter, checked_value);
    return checked_value;
}

float touch_sensor_2_filter_function(float measured_value)
{
    // 在此处添加对测量值进行滤波的代码
    float checked_value;
    checked_value = kalman_filter_Refresh(&touch_sensor_2_kalman_filter, measured_value);
    checked_value = mean_filter_Refresh(&touch_sensor_2_mean_filter, checked_value);
    return checked_value;
}

float position_sensor_filter_function(float measured_value)
{
    // 在此处添加对测量值进行滤波的代码
    float checked_value;
    checked_value = kalman_filter_Refresh(&position_sensor_kalman_filter, measured_value);
    checked_value = mean_filter_Refresh(&position_sensor_mean_filter, checked_value);
    return checked_value;
}

void sensor_init(void)
{
    // 在此处添加传感器任务初始化代码
    kalman_filter_Init(&touch_sensor_1_kalman_filter, 0.1f, 0.3f);
    mean_filter_Init(&touch_sensor_1_mean_filter, 10, touch_sensor_1_mean_filter_fifo);
    adc_sensor_init(&touch_sensor_1, &hadc1, ADC_SINGLE_ENDED, ADC_CHANNEL_1,
                    touch_sensor_map_function, touch_sensor_1_filter_function);

    kalman_filter_Init(&touch_sensor_2_kalman_filter, 0.1f, 0.3f);
    mean_filter_Init(&touch_sensor_2_mean_filter, 10, touch_sensor_2_mean_filter_fifo);
    adc_sensor_init(&touch_sensor_2, &hadc2, ADC_SINGLE_ENDED, ADC_CHANNEL_2,
                    touch_sensor_map_function, touch_sensor_2_filter_function);

    kalman_filter_Init(&position_sensor_kalman_filter, 0.1f, 0.3f);
    mean_filter_Init(&position_sensor_mean_filter, 10, position_sensor_mean_filter_fifo);
    adc_sensor_init(&position_sensor, &hadc5, ADC_SINGLE_ENDED, ADC_CHANNEL_1,
                    position_sensor_map_function, position_sensor_filter_function);

    for(uint8_t i = 0; i < 10; i++)
    {
        HAL_Delay(10);
        adc_sensor_refresh(&touch_sensor_1);
        adc_sensor_refresh(&touch_sensor_2);
        adc_sensor_refresh(&position_sensor);
    }
}

void sensor_refresh(void)
{
    // 在此处添加传感器任务刷新代码
    adc_sensor_refresh(&touch_sensor_1);
    adc_sensor_refresh(&touch_sensor_2);
    adc_sensor_refresh(&position_sensor);
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/