/**
 * @file states.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 时间片任务源文件
 * @version 0.1
 * @date 2026-02-12
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "tasks.h"

time_slice sensor_task;
time_slice f_pid_task;
time_slice p_pid_task;
time_slice impedance_task;
time_slice admittance_task;
time_slice actuator_task;
time_slice led_task;

uint8_t led_color;
uint8_t led_flag;
float actuator_input;
extern float control_value;

extern adc_sensor touch_sensor_1;
extern adc_sensor touch_sensor_2;
extern adc_sensor position_sensor;

extern pid force_pid;
extern pid position_pid;
extern impedance_ctrl impedance_controller;
extern admittance_ctrl admittance_controller;


void led_cb(void)
{
    led_flag ^= 1;
    if(led_flag)
        led_set_color(led_color);
    else
        led_set_color(LED_BLACK);
}



void sensor_cb(void)
{
    sensor_refresh();
}


void f_pid_cb(void)
{
    actuator_input = pid_refresh(&force_pid, control_value - 
        (touch_sensor_1.filtered_value + touch_sensor_2.filtered_value) / 2.0f);
}

void p_pid_cb(void)
{
    actuator_input = pid_refresh(&position_pid, control_value - position_sensor.filtered_value);
}

void impedance_cb(void)
{
    actuator_input = impedance_refresh(&impedance_controller, control_value, position_sensor.filtered_value,
        (touch_sensor_1.filtered_value + touch_sensor_2.filtered_value) / 2.0f);
}

void admittance_cb(void)
{
    actuator_input = admittance_refresh(&admittance_controller,
        control_value,
        (touch_sensor_1.filtered_value + touch_sensor_2.filtered_value) / 2.0f,
        position_sensor.filtered_value);
}

void actuator_cb(void)
{
    // 在此处添加执行器刷新代码
    claw_actuator_refresh(actuator_input);
}


/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/