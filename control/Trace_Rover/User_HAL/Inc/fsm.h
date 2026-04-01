/**
 * @file fsm.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 有限状态机的C语言实现
 * @version 0.1
 * @date 2025-11-18
 *
 * @copyright Copyright (c) 2025
 *
 */

#ifndef __FSM_H
#define __FSM_H

#pragma pack(push)
#pragma pack(1)

#ifdef MAIN_H
#include "main.h"
#else
#include <stdint.h>
#endif

//为什么有人会在单片机工程里封装状态机呢？

struct STATE; // 前向声明
typedef uint8_t (*transition)(void); // 转换函数类型

/**
 * @brief 状态机结构体
 *
 * @param enter_state 进入状态函数指针
 * @param run_state 运行状态函数指针
 * @param exit_state 退出状态函数指针
 * @param transition_func 状态转换函数指针数组指针
 * @param next_state 邻接状态结构体指针数组指针
 * @param next_cnt 邻接状态数量
 */
typedef struct STATE{
    void (*enter_state)(void); // 进入状态函数指针
    void (*run_state)(void);   // 运行状态函数指针
    void (*exit_state)(void);  // 退出状态函数指针
    
    transition        *transition_func; // 状态转换函数指针数组指针
    struct STATE     **next_state;      // 邻接状态结构体指针数组指针
    uint8_t            next_cnt;        // 邻接状态数量
}state;

typedef struct{
    state *state; // 当前状态指针   
}fsm;

void fsm_init(fsm *fsm, state *initial_state);
void fsm_trans_manual(fsm *fsm, state *next_state);
void fsm_trans(fsm *fsm, transition *trans_func, state **next_state, uint8_t next_cnt);
void fsm_run(fsm *fsm);


#pragma pack(pop)

#endif // !__FSM_H

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/