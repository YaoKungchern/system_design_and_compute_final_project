/**
 * @file communication.c
 * @author 沈一祺 (qdsyqaaa@gmail.com)
 * @brief 为潜航器提供的一些关于通信的库
 * @version 0.1
 * @date 2024-03-15
 *
 * @copyright Copyright (c) 2024
 *
 */
#include "fifo.h"

#include <stdio.h>
#include <stdlib.h>


/**
 * @brief FIFO初始化
 *
 * @param p_fifo FIFO
 * @param allowable_length FIFO最大长度
 * @param head_length 头长度
 * @param end_length 尾长度
 * @param head 头
 * @param end 尾
 */
void Fifo_Init(Fifo *p_fifo, int allowable_length, int head_length, int end_length, uint8_t *head, uint8_t *end)
{
    // 限制头长度
    if (head_length > 16)
        p_fifo->head_length = 16;
    else
        p_fifo->head_length = head_length;

    // 限制尾长度
    if (end_length > 16)
        p_fifo->end_length = 16;
    else
        p_fifo->end_length = end_length;

    // 限制队列长度
    if (allowable_length > 256)
        p_fifo->allowable_length = 256;
    else
        p_fifo->allowable_length = allowable_length;

    // 检查长度是否过短
    if (p_fifo->allowable_length < p_fifo->end_length + p_fifo->head_length)
        p_fifo->allowable_length = p_fifo->end_length + p_fifo->head_length;

    // 设置头
    Fifo_SetHead(p_fifo, head);

    // 设置尾巴
    Fifo_SetEnd(p_fifo, end);

    p_fifo->pointer      = 0;
    p_fifo->head_checked = 0;
}

/**
 * @brief 设置头
 *
 * @param p_fifo FIFO
 * @param head 头
 */
void Fifo_SetHead(Fifo *p_fifo, uint8_t *head)
{
    for (int i = 0; i < p_fifo->head_length; i++)
        p_fifo->head[i] = head[i];
}

/**
 * @brief 设置尾
 *
 * @param p_fifo FIFO
 * @param end 尾
 */
void Fifo_SetEnd(Fifo *p_fifo, uint8_t *end)
{
    for (int i = 0; i < p_fifo->end_length; i++)
        p_fifo->end[i] = end[i];
}
