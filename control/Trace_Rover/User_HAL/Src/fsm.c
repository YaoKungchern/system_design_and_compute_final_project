/**
 * @file fsm.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 有限状态机的C语言实现
 * @version 0.1
 * @date 2025-11-18
 *
 * @copyright Copyright (c) 2025
 *
 */

#include "fsm.h"

/**
 * @brief 初始化有限状态机
 * 
 * @param fsm 有限状态机指针
 * @param initial_state 初始状态指针
 *
 */
void fsm_init(fsm *fsm, state *initial_state)
{
    fsm->state = initial_state;
    fsm->state->enter_state();
}

/**
 * @brief 手动转换状态
 * 
 * @param fsm 有限状态机指针
 * @param next_state 下一个状态指针
 */
void fsm_trans_manual(fsm *fsm, state *next_state)
{
    fsm->state->exit_state();
    fsm->state = next_state;
    fsm->state->enter_state();
}

/**
 * @brief 根据状态转换函数转换状态
 * 
 * @param fsm 有限状态机指针
 * @param trans_func 状态转换函数指针数组指针
 * @param next_state 邻接状态指针数组指针
 * @param next_cnt 邻接状态数量
 */
void fsm_trans(fsm *fsm, transition *trans_func, state **next_state, uint8_t next_cnt)
{
    for(uint8_t i = 0; i < next_cnt; i++)
    {
        if(trans_func[i]())
        {
            fsm_trans_manual(fsm, next_state[i]);
            break;
        }
    }
}



/**
 * @brief 运行有限状态机
 *
 * @param fsm 有限状态机指针
 */
void fsm_run(fsm *fsm)
{
    fsm->state->run_state();
    fsm_trans(fsm, fsm->state->transition_func, 
        fsm->state->next_state, 
        fsm->state->next_cnt);
}

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/