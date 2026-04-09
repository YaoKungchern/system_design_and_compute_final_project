/**
 * @file actuator.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief STM32平台执行器的C语言抽象(针对带编码器的两相直流电机)
 * @version 0.1
 * @date 2026-03-30
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "actuator.h"

/**
 * @brief 初始化直流电机
 * 
 * @param motor 直流电机指针
 * @param htim 定时器句柄
 * @param channel 定时器通道
 * @param enc_htim 编码器定时器句柄
 * @param gpio_port_1 GPIO端口1
 * @param gpio_pin_1 GPIO引脚1
 * @param gpio_port_2 GPIO端口2
 * @param gpio_pin_2 GPIO引脚2
 * @param v_pid 速度PID控制器指针
 * @param p_pid 位置PID控制器指针
 */
void motor_init(dc_motor *motor, TIM_HandleTypeDef *htim, uint32_t channel, 
    TIM_HandleTypeDef *enc_htim, GPIO_TypeDef *gpio_port_1, uint16_t gpio_pin_1, 
    GPIO_TypeDef *gpio_port_2, uint16_t gpio_pin_2,
    pid *v_pid, pid *p_pid) {
    
    motor->htim = htim;
    motor->channel = channel;
    motor->enc_htim = enc_htim;
    motor->gpio_port_1 = gpio_port_1;
    motor->gpio_pin_1 = gpio_pin_1;
    motor->gpio_port_2 = gpio_port_2;
    motor->gpio_pin_2 = gpio_pin_2;
    motor->v_pid = *v_pid;
    motor->p_pid = *p_pid;

    // 初始化pwm定时器
    HAL_TIM_PWM_Start(motor->htim, motor->channel);

    // 初始化编码器定时器
    HAL_TIM_Encoder_Start(motor->enc_htim, TIM_CHANNEL_ALL);

    motor->last_time = HAL_GetTick();
}

/**
 * @brief 输出直流电机的PWM占空比
 * 
 * @param motor 直流电机指针
 * @param input 输入值，范围为-1到1，对应电机转速的正负和大小
 */
void motor_output(dc_motor *motor, float input) {
    // 输入为-1到1之间的值，对应电机转速的正负和大小
    // 限制输出范围
    input = fmax(input, -MOTOR_PWM_MAX);
    input = fmin(input, MOTOR_PWM_MAX);
    uint16_t pwm_value = (uint16_t)(fabs(input) * MOTOR_PWM_MAX);
    // 设置PWM占空比
    HAL_GPIO_WritePin(motor->gpio_port_1, motor->gpio_pin_1, input >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(motor->gpio_port_2, motor->gpio_pin_2, input >= 0 ? GPIO_PIN_RESET : GPIO_PIN_SET);

    __HAL_TIM_SET_COMPARE(motor->htim, motor->channel, pwm_value);
}

/**
 * @brief 设置直流电机的状态
 * 
 * @param motor 直流电机指针
 * @param state 直流电机状态
 */
void motor_set_state(dc_motor *motor, dc_motor_state state) {
    // 状态切换时重置PID控制器
    pid_reset(&motor->v_pid);
    pid_reset(&motor->p_pid);
    motor->state = state;
}

/**
 * @brief 更新直流电机的状态
 * 
 * @param motor 直流电机指针
 * @param input 输入值
 */
void motor_update(dc_motor *motor, float input) {
    // 读取编码器计数
    int16_t encoder_count = (int16_t)__HAL_TIM_GET_COUNTER(motor->enc_htim);    // 强制将32位寄存器和16位寄存器统一成int16_t
    float delta_position = (encoder_count / ENCODER_PPR) * (2 * 3.1415926535f * TIRE_RADIUS) / ENCODER_GEAR_RATIO;
    __HAL_TIM_SET_COUNTER(motor->enc_htim, 0); // 重置编码器计数

    // 计算当前速度和位置
    motor->real_position -= delta_position;
    uint32_t current_time = HAL_GetTick();
    motor->real_speed = delta_position / ((current_time - motor->last_time) / 1000.0f);
    motor->last_time = current_time;

    switch (motor->state)
    {
    case OPEN_LOOP:
        // 开环控制
        motor_output(motor, input);
        break;
    case SPEED_LOOP:
        // 速度环控制
        motor->target_speed = input;
        pid_refresh(&motor->v_pid, motor->target_speed - motor->real_speed);
        motor_output(motor, motor->v_pid.output);
        break;
    case POSITION_LOOP:
        // 串级控制
        // 外环：位置环
        motor->target_position = input;
        float position_error = motor->target_position - motor->real_position;
        pid_refresh(&motor->p_pid, position_error);
        // 内环：速度环
        motor->target_speed = motor->p_pid.output;
        float speed_error = motor->target_speed - motor->real_speed;
        pid_refresh(&motor->v_pid, speed_error);
        motor_output(motor, motor->v_pid.output);
        break;
    
    default:
        break;
    }
}

/**
 * @brief 初始化180度舵机
 * 
 * @param servo 180度舵机指针
 * @param htim 定时器句柄
 * @param channel 定时器通道
 */
void servo_180_init(servo_180 *servo, TIM_HandleTypeDef *htim, uint32_t channel) {
    servo->htim = htim;
    servo->channel = channel;
    HAL_TIM_PWM_Start(servo->htim, servo->channel);
}

/**
 * @brief 设置180度舵机的角度
 * 
 * @param servo 180度舵机指针
 * @param angle 角度值，范围为0到180度
 */
void servo_180_set_angle(servo_180 *servo, float angle) {
    // 限制角度范围
    angle = fmax(angle, 0.0f);
    angle = fmin(angle, 180.0f);
    // 将角度转换为PWM占空比
    uint16_t pwm_value = (uint16_t)((angle / 180.0f) * SERVO_PWM_MAX + SERVO_PWM_MIN);
    __HAL_TIM_SET_COMPARE(servo->htim, servo->channel, pwm_value);
}



/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/