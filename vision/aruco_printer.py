import cv2
import cv2.aruco as aruco
import numpy as np

# ====================== 你只改这里 ======================
MARKER_ID = [0,1,2,3]
MARKER_SIZE_CM = 10         # 码的实际边长（厘米，纯黑色方块部分）
DPI = 300                  # 打印标准DPI，别动
ARUCO_DICT = aruco.DICT_6X6_250
# ========================================================

# 计算像素
cm2inch = 2.54
size_inch = MARKER_SIZE_CM / cm2inch
size_pixel = int(size_inch * DPI)

# 生成 ArUco 码
for id in MARKER_ID:
    dictionary = aruco.getPredefinedDictionary(ARUCO_DICT)
    marker_img = aruco.generateImageMarker(dictionary, id, size_pixel)

    # 加白边（打印必须留边，否则会被裁掉）
    border_ratio = 0.0          # 白边宽度 20%
    border = int(size_pixel * border_ratio)

    marker_with_border = cv2.copyMakeBorder(
        marker_img, border, border, border, border,
        cv2.BORDER_CONSTANT, value=255
    )

# 保存
    filename = f"vision/aruco/aruco_ID{id}_{MARKER_SIZE_CM}cm.png"
    cv2.imwrite(filename, marker_with_border)

    print(f"已生成：{filename}")
    print(f"纯码尺寸：{MARKER_SIZE_CM} cm")
print("打印时务必关闭自动缩放！")
