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
        base_sys_set_by_vector(&input, control_value.x, control_value.y, 0);
        world2base(&rover_pos, &input, &output);
        value = output.vector;
        value.r = control_value.r;
        state = SPEED_LOOP;
        break;
    }
    case POSITION_LOOP_ROVER_BASE:{
        base_sys2D input, output;
        base_sys_set_by_vector(&input, control_value.x, control_value.y, control_value.r);
        base2world(&rover_pos, &input, &output);
        value = output.vector;
        state = POSITION_LOOP;
        break;
    }
    case POSITION_LOOP_WORLD_BASE:{
        value = control_value;
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
	}
	motor_state = state;
    mecanum_inverse_kinematics(&mecanum_ctrl, value);
    for(uint8_t i = 0; i < 4; i++)
    {
        motor_update(&motor[i], mecanum_ctrl.wheels[i]);
    }
}

void nav_cb(void)
{
    for(uint8_t i = 0; i < 4; i++)
    {
        mecanum_pos.wheels[i] = motor[i].real_position;
    }
    mecanum_forward_kinematics(&mecanum_pos, mecanum_pos.wheels);
	mecanum_pos.chassis.r=angle_correct_rad(mecanum_pos.chassis.r);
    rover_pos.vector = mecanum_pos.chassis;
    vector2matrix(&rover_pos);
    
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

    for(uint8_t i = 0; i < 4; i++)
    {
        pid_init(&vel_pid[i], 0.5f, 0.0f, 0.0f, 0.3f, 1.0f);
        pid_init(&pos_pid[i], 0.5f, 0.0f, 0.0f, 0.6f, 2.0f);
    }
    motor_init(&motor[0], &htim4, TIM_CHANNEL_1, &htim2, GPIOD, GPIO_PIN_10, GPIOD, GPIO_PIN_8, &vel_pid[0], &pos_pid[0]);
    motor_init(&motor[1], &htim4, TIM_CHANNEL_4, &htim8, GPIOD, GPIO_PIN_3, GPIOD, GPIO_PIN_1, &vel_pid[1], &pos_pid[1]);
    motor_init(&motor[2], &htim4, TIM_CHANNEL_3, &htim1, GPIOD, GPIO_PIN_2, GPIOD, GPIO_PIN_0, &vel_pid[2], &pos_pid[2]);
    motor_init(&motor[3], &htim4, TIM_CHANNEL_2, &htim3, GPIOD, GPIO_PIN_11, GPIOD, GPIO_PIN_9, &vel_pid[3], &pos_pid[3]);

    time_slice_init(&motor_task, 5, motor_cb);
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