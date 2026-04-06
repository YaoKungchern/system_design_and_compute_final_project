/**
 * @file actuator.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief STM32平台执行器的C语言抽象(针对带编码器的两相直流电机)
 * @version 0.1
 * @date 2026-03-30
 *
 * @copyright Copyright (c) 2026
 *
 */

#ifndef __ACTUATOR_H
#define __ACTUATOR_H

#pragma pack(push)
#pragma pack(1)

#include "main.h"
#include "pid.h"

#define ENCODER_PPR 2048.0f ///< 编码器每转脉冲数
#define ENCODER_GEAR_RATIO 1.0f ///< 编码器齿轮比
#define TIRE_RADIUS 0.05f ///< 轮子半径

#define MOTOR_PWM_MAX 1000 // 最大PWM占空比
#define SERVO_PWM_MAX 20000 // 180度舵机最大PWM占空比
#define SERVO_PWM_MIN 500 // 180度舵机最小PWM占空比


typedef enum {
    OPEN_LOOP = 0,
    SPEED_LOOP,
    POSITION_LOOP,
} dc_motor_state;

typedef struct {
    TIM_HandleTypeDef *htim; ///< 定时器句柄
    uint32_t channel;        ///< 定时器通道

    TIM_HandleTypeDef *enc_htim; ///< 编码器定时器句柄

    GPIO_TypeDef *gpio_port_1; ///< GPIO端口1
    uint16_t gpio_pin_1;       ///< GPIO引脚1

    GPIO_TypeDef *gpio_port_2; ///< GPIO端口2
    uint16_t gpio_pin_2;       ///< GPIO引脚2


    float real_speed;           ///< 当前速度
    float target_speed;         ///< 目标速度
    pid v_pid;                    ///< 速度PID控制器

    float real_position;        ///< 当前位置   
    float target_position;      ///< 目标位置
    pid p_pid;                    ///< 位置PID控制器

    dc_motor_state state;       ///< 当前状态

    uint32_t last_time; ///< 上次更新时间

} dc_motor;

typedef struct {
    TIM_HandleTypeDef *htim; ///< 定时器句柄
    uint32_t channel;        ///< 定时器通道
} servo_180;

void motor_init(dc_motor *motor, TIM_HandleTypeDef *htim, uint32_t channel, 
    TIM_HandleTypeDef *enc_htim, GPIO_TypeDef *gpio_port_1, uint16_t gpio_pin_1, 
    GPIO_TypeDef *gpio_port_2, uint16_t gpio_pin_2,
    pid *v_pid, pid *p_pid);

void motor_set_state(dc_motor *motor, dc_motor_state state);    
void motor_update(dc_motor *motor, float input);

void servo_180_init(servo_180 *servo, TIM_HandleTypeDef *htim, uint32_t channel);
void servo_180_set_angle(servo_180 *servo, float angle);



#pragma pack(pop)

#endif // !__ACTUATOR_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/