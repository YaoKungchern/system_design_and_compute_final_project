/**
 * @file states.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 状态机源文件
 * @version 0.1
 * @date 2026-02-12
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "states.h"

extern time_slice sensor_task;
extern time_slice f_pid_task; 
extern time_slice p_pid_task;
extern time_slice impedance_task;
extern time_slice admittance_task;
extern time_slice actuator_task;
extern time_slice led_task;

extern pid force_pid;
extern pid position_pid;
extern impedance_ctrl impedance_controller;
extern admittance_ctrl admittance_controller;

extern uint8_t led_color;
extern float control_value;
extern float actuator_input;

extern uint8_t control_flag;

fsm control_fsm;

void openloop_enter(void)
{
  led_color = LED_BLUE;
}
void openloop_run(void)
{
  actuator_input = control_value;   
}
void openloop_exit(void)
{
  led_color = LED_BLACK;
}
state openloop_state={
    .enter_state = openloop_enter,
    .run_state = openloop_run,
    .exit_state = openloop_exit,
    .transition_func = NULL,
    .next_state = NULL,
    .next_cnt = 0
};

void position_enter(void)
{
  led_color = LED_RED;
  pid_reset(&position_pid);
  time_slice_init(&p_pid_task, 10, p_pid_cb);
}
void position_run(void)
{
  time_slice_run(&p_pid_task);
}
void position_exit(void)
{
  led_color = LED_BLACK;
}
state position_state={
    .enter_state = position_enter,
    .run_state = position_run,
    .exit_state = position_exit,
    .transition_func = NULL,
    .next_state = NULL,
    .next_cnt = 0
};

void force_enter(void)
{
  led_color = LED_MAGENTA;
  pid_reset(&force_pid);
  time_slice_init(&f_pid_task, 10, f_pid_cb);
}
void force_run(void)
{
  time_slice_run(&f_pid_task);
}
void force_exit(void)
{
  led_color = LED_BLACK;
}
state force_state={
    .enter_state = force_enter,
    .run_state = force_run,
    .exit_state = force_exit,
    .transition_func = NULL,
    .next_state = NULL,
    .next_cnt = 0
};

void impedance_enter(void)
{
  led_color = LED_GREEN;
  impedance_reset(&impedance_controller);
  time_slice_init(&impedance_task, 10, impedance_cb);
}
void impedance_run(void)
{
  time_slice_run(&impedance_task);
}
void impedance_exit(void)
{
  led_color = LED_BLACK;
}
state impedance_state={
    .enter_state = impedance_enter,
    .run_state = impedance_run,
    .exit_state = impedance_exit,
    .transition_func = NULL,
    .next_state = NULL,
    .next_cnt = 0
};

void admittance_enter(void)
{
  led_color = LED_CYAN;
  admittance_reset(&admittance_controller);
  time_slice_init(&admittance_task, 10, admittance_cb);
}
void admittance_run(void)
{
  time_slice_run(&admittance_task);
}
void admittance_exit(void)
{
  led_color = LED_BLACK;
}
state admittance_state={
    .enter_state = admittance_enter,
    .run_state = admittance_run,
    .exit_state = admittance_exit,
    .transition_func = NULL,
    .next_state = NULL,
    .next_cnt = 0
};

void init(void)
{
  sensor_init();
  led_set_color(LED_BLUE);
  claw_actuator_init();
  UartInit();
  HAL_Delay(100);
  led_set_color(LED_MAGENTA);
    fsm_init(&control_fsm, &openloop_state);
  HAL_Delay(100);
  time_slice_init(&actuator_task, 20, actuator_cb);
  time_slice_init(&led_task, 500, led_cb);
  time_slice_init(&sensor_task, 5, sensor_cb);
  led_set_color(LED_WHITE);
}

void state_machine_run(void)
{
  switch (control_flag)
  {
  case 0x00: // 开环控制
    fsm_trans_manual(&control_fsm, &openloop_state);
    break;
  case 0x01: // 位置闭环控制
    fsm_trans_manual(&control_fsm, &position_state);
    break;
  case 0x02: // 力闭环控制
    fsm_trans_manual(&control_fsm, &force_state);
    break;
  case 0x03: // 阻抗控制
    fsm_trans_manual(&control_fsm, &impedance_state);
    break;
  case 0x04: //  导纳控制
    fsm_trans_manual(&control_fsm, &admittance_state);
    break;
  
  default:
    break;
  }
    
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/