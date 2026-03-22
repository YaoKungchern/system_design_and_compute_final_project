import cv2
import numpy as np
import glob
import os

# ====================== 你需要修改的参数 ======================
# 1. 棋盘格内角点数量（宽×高）：你的是9×12
CHECKERBOARD = (8, 11)
# 2. 棋盘格单个格子的真实物理尺寸（单位：mm，自己用尺子量）
SQUARE_SIZE = 30  # 示例：25mm，按实际修改
# 3. 棋盘格图片的路径（支持jpg/png，可直接放当前文件夹）
IMAGE_PATH = r"vision\calibrate_img\*.jpg"  # 若图片在子文件夹，改写成 "calib_imgs/*.png"
# =============================================================

# 标定终止条件（迭代次数+精度）
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 初始化3D世界坐标（棋盘格平面为z=0）
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) * SQUARE_SIZE

# 存储所有图片的3D点和2D像素点
objpoints = []  # 3D世界点
imgpoints = []  # 2D图像点

# 读取所有棋盘格图片
images = glob.glob(IMAGE_PATH)
if len(images) == 0:
    print(f"错误：未找到图片！请检查路径：{IMAGE_PATH}")
    print("提示：图片格式支持jpg/png，路径可写为 '*.jpg' 或 'calib_imgs/*.png'")
    exit()

print(f"找到 {len(images)} 张图片，开始检测角点...")

# 遍历每张图片检测内角点
valid_count = 0  # 有效检测到角点的图片数
for idx, fname in enumerate(images):
    img = cv2.imread(fname)
    if img is None:
        print(f"跳过：图片 {fname} 读取失败")
        continue
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 检测棋盘格内角点
    ret, corners = cv2.findChessboardCorners(
        gray, CHECKERBOARD, 
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE
    )
    
    # 如果检测到足够角点，优化精度并保存
    if ret:
        objpoints.append(objp)
        # 亚像素级优化角点坐标（提升标定精度）
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        valid_count += 1
        print(f"图片 {idx+1}/{len(images)}：检测到角点 ✔️")
    else:
        print(f"图片 {idx+1}/{len(images)}：未检测到角点 ❌")

# 检查有效图片数量（至少需要10张才够精准）
if valid_count < 10:
    print(f"警告：仅检测到 {valid_count} 张有效图片（建议≥10张）")
    confirm = input("是否继续标定？(y/n)：")
    if confirm.lower() != 'y':
        exit()

# 开始相机标定（核心：计算内参、畸变系数）
print("\n开始标定...")
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

# 输出标定结果
print("\n===================== 标定结果 =====================")
print(f"标定是否成功：{'是' if ret else '否'}")
print("\n1. 相机内参矩阵 (mtx)：")
print(mtx)
print("\n2. 畸变系数 (dist) [k1, k2, p1, p2, k3]：")
print(dist)

# 计算重投影误差（越小越好，<0.5为优秀，<1为合格）
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    mean_error += error
mean_error /= len(objpoints)
print(f"\n3. 平均重投影误差：{mean_error:.4f}（越小越好，<0.5为优秀）")

# 保存标定参数到文件（后续ArUco定位直接用）
save_file = "camera_calib_params.npz"
np.savez(save_file, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
print(f"\n4. 标定参数已保存到：{os.path.abspath(save_file)}")

# 可选：验证一张图片的校正效果
test_img = cv2.imread(images[0])
undistorted_img = cv2.undistort(test_img, mtx, dist, None, mtx)
cv2.imwrite("original_img.jpg", test_img)
cv2.imwrite("undistorted_img.jpg", undistorted_img)
print("\n5. 校正效果对比图已保存：original_img.jpg / undistorted_img.jpg")

# 关闭所有窗口
cv2.destroyAllWindows()