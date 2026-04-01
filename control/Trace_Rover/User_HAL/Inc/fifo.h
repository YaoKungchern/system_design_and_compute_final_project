/**
 * @file communication.h
 * @author 沈一祺 (qdsyqaaa@gmail.com)
 * @brief 为潜航器提供的一些关于通信的库
 * @version 0.1
 * @date 2024-03-15
 *
 * @copyright Copyright (c) 2024
 *
 */
#ifndef __COMMUNICATION_H
#define __COMMUNICATION_H


#pragma pack(push)
#pragma pack(1)

#ifdef MAIN_H
#include "main.h"
#else
#include <stdint.h>
#endif

typedef enum {
    FIFO_RECEIVED        = 0, ///< 完成接收
    FIFO_FINISH_ONE      = 1, ///< 完成一个字节的接收
    FIFO_HEAD_CHECKED    = 2, ///< 头校验完成
    FIFO_END_CHECKED     = 3, ///< 尾校验完成
    FIFO_OVERFLOW        = 4, ///< 接收溢出
    FIFO_REFERSH_TIMEOUT = 5  ///< 更新程序超时退出
} FIFO_RESAULT;


/**
 * @brief 数据fifo
 *
 */
typedef struct {
    uint8_t fifo[256]; ///< 存储队列

    uint8_t head[16]; ///< 头
    uint8_t end[16];  ///< 尾

    int pointer;      ///< 指针
    int head_checked; ///< 头是否被校验

    int allowable_length; ///< 容许的队列最大长度\n 不超过256
    int head_length;      ///< 头长度\n 不超过16
    int end_length;       ///< 尾长度\n 不超过16
} Fifo;


void Fifo_Init(Fifo *p_fifo, int allowable_length, int head_length, int end_length, uint8_t *head, uint8_t *end);
void Fifo_SetHead(Fifo *p_fifo, uint8_t *head);
void Fifo_SetEnd(Fifo *p_fifo, uint8_t *end);

/**
 * @brief 头校验
 *
 * @param p_fifo 待校验头的队列
 * @return int
 */
static inline int head_check(Fifo *p_fifo)
{
    if (p_fifo->pointer >= p_fifo->head_length)
    {
        for (int i = 0; i < p_fifo->head_length; i++)
        {
            if (p_fifo->fifo[p_fifo->pointer - i] != p_fifo->head[p_fifo->head_length - i - 1])
            {
                return 0;
            }
        }
        return 1;
    }
    else
        return 0;
}

/**
 * @brief 尾校验
 *
 * @param p_fifo 待校验尾的队列
 * @return int
 */
static inline int end_check(Fifo *p_fifo)
{
    if (p_fifo->pointer >= p_fifo->end_length + p_fifo->head_length - 1)
    {
        for (int i = 0; i < p_fifo->end_length; i++)
        {
            if (p_fifo->fifo[p_fifo->pointer - i] != p_fifo->end[p_fifo->end_length - i - 1])
            {
                return 0;
            }
        }
        return 1;
    }
    else
        return 0;
}

/**
 * @brief 队列内部刷新
 *
 * @param p_fifo 队列
 * @param input 输入
 * @return FIFO_RESAULT 校验结果
 */
static inline FIFO_RESAULT Fifo_RefreshInternal(Fifo *p_fifo, uint8_t input)
{
    p_fifo->fifo[p_fifo->pointer] = input;

    // 校验头
    if (!p_fifo->head_checked && head_check(p_fifo))
    {
        for (int i = 0; i < p_fifo->head_length; i++)
        {
            p_fifo->fifo[i] = p_fifo->head[i];
        }
        p_fifo->pointer = p_fifo->head_length;

        p_fifo->head_checked = 1;
        return FIFO_HEAD_CHECKED;
    }

    // 校验尾
    if (p_fifo->head_checked && end_check(p_fifo))
    {
        p_fifo->pointer      = 0;
        p_fifo->head_checked = 0;

        // 此时可直接使用 p_fifo->fifo 读取数据
        return FIFO_RECEIVED;
    }

    if (p_fifo->pointer > p_fifo->allowable_length)
    {
        p_fifo->pointer      = 0;
        p_fifo->head_checked = 0;
        return FIFO_OVERFLOW;
    }
    else
    {
        p_fifo->pointer++;
        return FIFO_FINISH_ONE;
    }
    return FIFO_REFERSH_TIMEOUT;
}

/**
 * @brief 队列外部刷新
 *
 * @param p_fifo 队列
 * @return FIFO_RESAULT 校验结果
 */
static inline FIFO_RESAULT Fifo_RefreshExternal(Fifo *p_fifo)
{
    // 校验头
    if (!p_fifo->head_checked && head_check(p_fifo))
    {
        for (int i = 0; i < p_fifo->head_length; i++)
        {
            p_fifo->fifo[i] = p_fifo->head[i];
        }
        p_fifo->pointer = p_fifo->head_length;

        p_fifo->head_checked = 1;
        return FIFO_HEAD_CHECKED;
    }

    // 校验尾
    if (p_fifo->head_checked && end_check(p_fifo))
    {
        p_fifo->pointer      = 0;
        p_fifo->head_checked = 0;

        // 此时可直接使用 p_fifo->fifo 读取数据
        return FIFO_RECEIVED;
    }

    if (p_fifo->pointer > p_fifo->allowable_length)
    {
        p_fifo->pointer      = 0;
        p_fifo->head_checked = 0;
        return FIFO_OVERFLOW;
    }
    else
    {
        p_fifo->pointer++;
        return FIFO_FINISH_ONE;
    }
    return FIFO_REFERSH_TIMEOUT;
}


#pragma pack(pop)


#endif // !__COMMUNICATION_H