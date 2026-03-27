import cv2
import os

# 解析命令行参数

video_folder = r"C:\Users\21343\Pictures\Camera Roll"
output_folder = r"E:\document\s_d&c\raw_img"
frame_interval = 30


# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 支持的视频文件扩展名
video_extensions = ['.mp4', '.avi', '.mov', '.mkv']

# 遍历视频文件夹
video_files = []
for root, _, files in os.walk(video_folder):
    for file in files:
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(os.path.join(root, file))

if not video_files:
    print(f"在 {video_folder} 中未找到视频文件")
    exit(1)

print(f"找到 {len(video_files)} 个视频文件")
print(f"帧间隔: {frame_interval}")
print(f"输出文件夹: {output_folder}")

# 处理每个视频文件
for video_idx, video_path in enumerate(video_files):
    video_name = os.path.basename(video_path)
    video_basename = os.path.splitext(video_name)[0]
    
    print(f"\n处理视频 {video_idx + 1}/{len(video_files)}: {video_name}")
    
    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频: {video_path}")
        continue
    
    # 获取视频属性
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"视频总帧数: {total_frames}, 帧率: {fps:.2f}")
    
    # 提取帧
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 按指定间隔保存帧
        if frame_count % frame_interval == 0:
            # 生成输出文件名
            output_filename = f"{video_basename}_frame_{frame_count:06d}.jpg"
            output_path = os.path.join(output_folder, output_filename)
            
            # 保存帧
            cv2.imwrite(output_path, frame)
            saved_count += 1
            
            if saved_count % 10 == 0:
                print(f"已保存 {saved_count} 帧")
        
        frame_count += 1
    
    # 释放资源
    cap.release()
    
    print(f"视频处理完成，共保存 {saved_count} 帧")

print(f"\n所有视频处理完成")
print(f"提取的帧已保存至: {output_folder}")