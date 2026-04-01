import cv2
from ultralytics import YOLO

# 加载YOLO模型
model = YOLO(r'vision/best.pt')  # 确保best.pt在同一目录

# 打开摄像头
cap = cv2.VideoCapture(1)  # 0表示默认摄像头，1表示外部摄像头

print("按 q 退出")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 使用YOLO模型进行检测
    results = model(frame)
    
    # 在帧上绘制检测结果
    annotated_frame = results[0].plot()
    
    # 显示结果
    cv2.imshow("YOLO Realtime Detection", annotated_frame)
    
    # 按q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()