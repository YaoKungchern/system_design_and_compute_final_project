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

time_slice motor_task;
time_slice nav_task;
time_slice uart_task;

ctrl_state control_state = OPEN_LOOP_ROVER_BASE;
dc_motor_state motor_state = OPEN_LOOP;

vector2D control_value;

pid vel_pid[4];
pid pos_pid[4];

ultrasonic_sensor ultrasonic_sys;

base_sys2D rover_pos;
base_sys2D rover_vel;

dc_motor motor[4];

mecanum mecanum_pos;
mecanum mecanum_vel;
mecanum mecanum_ctrl;

servo_180 servo_cam;

void motor_cb(void)
{
    vector2D value;
    dc_motor_state state;
    switch (control_state)
    {
    case OPEN_LOOP:{
        value = control_value;
        state = OPEN_LOOP;
        break;
    }
    case SPEED_LOOP_ROVER_BASE:{
        value = control_value;
        state = SPEED_LOOP;
        break;
    }
    case SPEED_LOOP_WORLD_BASE:{
        base_sys2D input, output;
        // 注意：速度转换不需要减去当前位置
        base_sys_set_by_vector(&input, control_value.x, control_value.y, 0);
        
        // 直接进行坐标转换，不计算位置误差
        float cos_r = cosf(rover_pos.vector.r);
        float sin_r = sinf(rover_pos.vector.r);
        output.vector.x = cos_r * input.vector.x + sin_r * input.vector.y;
        output.vector.y = -sin_r * input.vector.x + cos_r * input.vector.y;
        output.vector.r = control_value.r;
        vector2matrix(&output);
        
        value = output.vector;
        state = SPEED_LOOP;
        break;
    }
    case POSITION_LOOP_ROVER_BASE:{
        base_sys2D input, output;
        // 计算目标位置与当前位置的误差（机器人坐标系）
        value = control_value;
        value.r = angle_correct_rad(control_value.r);
        state = POSITION_LOOP;
        break;
    }
    case POSITION_LOOP_WORLD_BASE:{
        // 计算目标位置与当前位置的误差
        float error_x = control_value.x - rover_pos.vector.x;
        float error_y = control_value.y - rover_pos.vector.y;
        float target_r = control_value.r;
        float current_r = rover_pos.vector.r;
        float angle_diff = target_r - current_r;
        angle_diff = angle_correct_rad(angle_diff);
        
        // 创建目标位置向量，考虑位置误差
        value.x = error_x;
        value.y = error_y;
        value.r = angle_diff;
        state = POSITION_LOOP;
        break;
    }
    default:
        break;
    }
    if(motor_state != state)
	{
        for(uint8_t i = 0; i < 4; i++)
        {
            motor_set_state(&motor[i], state);
        }
        motor_state = state;
	}
    mecanum_inverse_kinematics(&mecanum_ctrl, value);
    for(uint8_t i = 0; i < 4; i++)
    {
        motor_update(&motor[i], mecanum_ctrl.wheels[i]);
    }
}

void nav_cb(void)
{
    static float last_wheels[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    
    // 保存当前轮子位置用于增量计算
    float current_wheels[4];
    for(uint8_t i = 0; i < 4; i++)
    {
        current_wheels[i] = motor[i].real_position;
    }
    
    // 更新 mecanum_pos（保持兼容性）
    for(uint8_t i = 0; i < 4; i++)
    {
        mecanum_pos.wheels[i] = current_wheels[i];
    }
    mecanum_forward_kinematics(&mecanum_pos, mecanum_pos.wheels);
    
    // 计算轮子位置增量
    float wheel_deltas[4];
    for(uint8_t i = 0; i < 4; i++)
    {
        wheel_deltas[i] = current_wheels[i] - last_wheels[i];
        last_wheels[i] = current_wheels[i];
    }
    
    // 使用增量计算底盘位置（机器人坐标系）
    mecanum temp_mecanum;
    mecanum_forward_kinematics(&temp_mecanum, wheel_deltas);
    
    // 将机器人坐标系的增量转换到世界坐标系
    base_sys2D delta_base, delta_world;
    base_sys_set_by_vector(&delta_base, temp_mecanum.chassis.x, temp_mecanum.chassis.y, temp_mecanum.chassis.r);
    base2world(&rover_pos, &delta_base, &delta_world);
    
    // 更新底盘位置（世界坐标系）
    rover_pos.vector.x = delta_world.vector.x;
    rover_pos.vector.y = delta_world.vector.y;
    rover_pos.vector.r = delta_world.vector.r;
    
    // 角度校正
    rover_pos.vector.r = angle_correct_rad(rover_pos.vector.r);
    
    // 更新齐次变换矩阵
    vector2matrix(&rover_pos);
    
    // 速度计算保持不变
    for(uint8_t i = 0; i < 4; i++)
    {
        mecanum_vel.wheels[i] = motor[i].real_speed;
    }
    mecanum_forward_kinematics(&mecanum_vel, mecanum_vel.wheels);
    rover_vel.vector = mecanum_vel.chassis;
    vector2matrix(&rover_vel);
}

void uart_cb(void)
{
	navigation_info info;
	read_navigation_info(&info);
}

/**
 * @brief 实例化所有对象（所有底层接口在此更改）
 * 
 */
void tasks_init(void)
{
    UartInit();

    ultrasonic_init(&ultrasonic_sys, &huart3, &huart1, 50);
    servo_180_init(&servo_cam, &htim15, TIM_CHANNEL_1);
    servo_180_set_angle(&servo_cam, 90.0f);

    for(uint8_t i = 0; i < 4; i++)
    {
        pid_init(&vel_pid[i], 5.0f, 0.5f, 0.05f, 0.3f, 1.0f);
        pid_init(&pos_pid[i], 1.2f, 0.0f, 0.88f, 0.4f, 1.2f);
    }
    motor_init(&motor[0], &htim4, TIM_CHANNEL_1, &htim2, GPIOD, GPIO_PIN_8, GPIOD, GPIO_PIN_10, CCW, &vel_pid[0], &pos_pid[0]);
    motor_init(&motor[1], &htim4, TIM_CHANNEL_4, &htim8, GPIOD, GPIO_PIN_1, GPIOD, GPIO_PIN_3, CW, &vel_pid[1], &pos_pid[1]);
    motor_init(&motor[2], &htim4, TIM_CHANNEL_3, &htim1, GPIOD, GPIO_PIN_0, GPIOD, GPIO_PIN_2, CW, &vel_pid[2], &pos_pid[2]);
    motor_init(&motor[3], &htim4, TIM_CHANNEL_2, &htim3, GPIOD, GPIO_PIN_9, GPIOD, GPIO_PIN_11, CCW, &vel_pid[3], &pos_pid[3]);

    time_slice_init(&motor_task, 5, motor_cb);
	HAL_Delay(2);
    time_slice_init(&nav_task, 5, nav_cb);
//	time_slice_init(&uart_task, 20, uart_cb);

}

void tasks_run(void)
{
    time_slice_run(&motor_task);
    time_slice_run(&nav_task);
//	time_slice_run(&uart_task);
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/