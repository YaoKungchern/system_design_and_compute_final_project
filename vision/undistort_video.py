import cv2
import numpy as np

# 解析命令行参数

input_video = r"C:\Users\21343\Pictures\Camera Roll\WIN_20260325_22_20_14_Pro.mp4"
output_video = r"C:\Users\21343\Pictures\Camera Roll\undistorted_video6.mp4"
params=r'vision/camera_calib_params.npz'


# ===================== 加载相机参数 =====================
try:
    params = np.load(params)
    mtx = params["mtx"]    # 内参矩阵
    dist = params["dist"]  # 畸变系数
    print("相机参数加载成功")
except Exception as e:
    print(f"加载相机参数失败: {e}")
    exit(1)
# =======================================================

# 打开输入视频
cap = cv2.VideoCapture(input_video)
if not cap.isOpened():
    print(f"无法打开输入视频: {input_video}")
    exit(1)

# 获取视频属性
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 创建视频写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用MP4编码
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
if not out.isOpened():
    print(f"无法创建输出视频: {output_video}")
    cap.release()
    exit(1)

print(f"开始处理视频: {input_video}")
print(f"输出视频: {output_video}")
print(f"视频分辨率: {width}x{height}, 帧率: {fps:.2f}")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 进行畸变校正
    undistorted_frame = cv2.undistort(frame, mtx, dist)
    
    # 写入输出视频
    out.write(undistorted_frame)
    
    frame_count += 1
    if frame_count % 100 == 0:
        print(f"已处理 {frame_count} 帧")

# 释放资源
cap.release()
out.release()
print(f"视频处理完成，共处理 {frame_count} 帧")
print(f"去畸变视频已保存至: {output_video}")