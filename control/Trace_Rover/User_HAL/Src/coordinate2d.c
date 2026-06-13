/**
 * @file coordinate2d.c
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 2D坐标系的定义和转换
 * @version 0.1
 * @date 2026-03-31
 *
 * @copyright Copyright (c) 2026
 *
 */

#include "coordinate2D.h"

/**
 * @brief 角度修正函数，将角度限制在-180到180度之间
 * 
 * @param angle 输入角度，单位为度
 * @return float 修正后的角度，单位为度
 */
float angle_correct_deg(float angle) {
    while (angle >= 180.0f) {
        angle -= 360.0f;
    }
    while (angle < -180.0f) {
        angle += 360.0f;
    }
    return angle;
}

/**
 * @brief 弧度制下角度值矫正
 *
 * @param angle 待矫正角度值
 * @return float 正确角度值
 */
float angle_correct_rad(float angle)
{
    // 使用 fmod 进行更精确的角度校正
    // 将角度限制在 (-PI, PI] 范围内
    float remainder = fmodf(angle, 2 * PI);
    
    // fmod 返回值的符号与被除数相同
    // 需要处理边界情况：当余数为 -PI 时，转换为 PI
    if (remainder <= -PI) {
        remainder += 2 * PI;
    } else if (remainder > PI) {
        remainder -= 2 * PI;
    }
    
    return remainder;
}

/**
 * @brief 向量转换为矩阵
 * 
 * @param sys 机器人底盘信息
 */
void vector2matrix(base_sys2D *sys) {
    float cos_r = cosf(sys->vector.r);
    float sin_r = sinf(sys->vector.r);
    sys->h_matrix[0][0] = cos_r;
    sys->h_matrix[0][1] = -sin_r;
    sys->h_matrix[0][2] = sys->vector.x;
    sys->h_matrix[1][0] = sin_r;
    sys->h_matrix[1][1] = cos_r;
    sys->h_matrix[1][2] = sys->vector.y;
    sys->h_matrix[2][0] = 0.0f;
    sys->h_matrix[2][1] = 0.0f;
    sys->h_matrix[2][2] = 1.0f;
}

/**
 * @brief 矩阵转换为向量
 * 
 * @param sys 机器人底盘信息
 */
void matrix2vector(base_sys2D *sys) {
    sys->vector.x = sys->h_matrix[0][2];
    sys->vector.y = sys->h_matrix[1][2];
    sys->vector.r = atan2f(sys->h_matrix[1][0], sys->h_matrix[0][0]);
}

/**
 * @brief 初始化机器人底盘信息
 * 
 * @param sys 机器人底盘信息
 */
void base_sys2D_init(base_sys2D *sys) {
    sys->vector.x = 0.0f;
    sys->vector.y = 0.0f;
    sys->vector.r = 0.0f;
    vector2matrix(sys);
}

/**
 * @brief 设置机器人底盘信息为向量
 * 
 * @param sys 机器人底盘信息
 * @param x x坐标
 * @param y y坐标
 * @param r 角度
 */
void base_sys_set_by_vector(base_sys2D *sys, float x, float y, float r) {
    sys->vector.x = x;
    sys->vector.y = y;
    sys->vector.r = r;
    vector2matrix(sys);
}

/**
 * @brief 设置机器人底盘信息为矩阵
 * 
 * @param sys 机器人底盘信息
 * @param h_matrix 3x3矩阵
 */
void base_sys_set_by_matrix(base_sys2D *sys, float h_matrix[3][3]) {
    memcpy(sys->h_matrix, h_matrix, sizeof(sys->h_matrix)); 
    matrix2vector(sys);
}

/**
 * @brief 机器人底盘坐标转换为世界坐标
 * 
 * @param base 机器人底盘信息
 * @param input 输入坐标
 * @param output 输出坐标
 */
void base2world(base_sys2D *base, base_sys2D *input, base_sys2D *output) {
    float x = input->vector.x;
    float y = input->vector.y;
    float r = input->vector.r;

    float cos_r = cosf(base->vector.r);
    float sin_r = sinf(base->vector.r);

    output->vector.x = base->vector.x + cos_r * x - sin_r * y;
    output->vector.y = base->vector.y + sin_r * x + cos_r * y;
    output->vector.r = angle_correct_rad(base->vector.r + r);
    vector2matrix(output);
}

/**
 * @brief 世界坐标转换为机器人底盘坐标
 * 
 * @param base 机器人底盘信息
 * @param input 世界坐标系下的输入坐标
 * @param output 转换后的机器人底盘坐标系下的输出坐标
 */
void world2base(base_sys2D *base, base_sys2D *input, base_sys2D *output) {
    float x = input->vector.x - base->vector.x;
    float y = input->vector.y - base->vector.y;
    float r = input->vector.r;

    float cos_r = cosf(base->vector.r);
    float sin_r = sinf(base->vector.r);

    output->vector.x = cos_r * x + sin_r * y;
    output->vector.y = -sin_r * x + cos_r * y;
    output->vector.r = angle_correct_rad(r - base->vector.r);
    vector2matrix(output);
}


/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/