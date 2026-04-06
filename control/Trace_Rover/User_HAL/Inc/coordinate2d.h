/**
 * @file coordinate2D.h
 * @author 姚康晨 (2134374074@qq.com)
 * @brief 2D坐标系的定义和转换
 * @version 0.1
 * @date 2026-03-31
 *
 * @copyright Copyright (c) 2026
 *
 */

 #ifndef __COORDINATE2D_H
 #define __COORDINATE2D_H
 
 #pragma pack(push)
 #pragma pack(1)

 #include <math.h>
 #include <string.h>

#define DEG2RAD 0.01745329252f // 角度制转弧度制
#define RAD2DEG 57.29577951f   // 弧度制转角度制
#define PI 3.1415926535f        // 圆周率

 typedef struct {
    float x; ///< x坐标
    float y; ///< y坐标
    float r; ///< 角度坐标
 } vector2D;

 typedef struct {
    vector2D vector;
    float h_matrix[3][3]; ///< 齐次变换矩阵
 } base_sys2D;

float angle_correct_deg(float angle);
float angle_correct_rad(float angle);

void base_sys2D_init(base_sys2D *sys);
void vector2matrix(base_sys2D *sys);
void matrix2vector(base_sys2D *sys);
void base_sys_set_by_vector(base_sys2D *sys, float x, float y, float r);
void base_sys_set_by_matrix(base_sys2D *sys, float h_matrix[3][3]);
void base2world(base_sys2D *base, base_sys2D *input, base_sys2D *output);

#pragma pack(pop)

#endif /* __COORDINATE2D_H */

/*__||_____||__
  __||_____||__
  ___\\___//___
  _===========_
  _____|||_____
  _____|||_____
  ______|______
  ___防伪专用___*/