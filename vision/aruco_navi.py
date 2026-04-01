import cv2
import cv2.aruco as aruco
import numpy as np

# ===================== 加载你刚才标定的相机参数 =====================
# 确保 camera_params.npz 和本代码在同一文件夹
params = np.load(r"vision/camera_calib_params.npz")
mtx = params["mtx"]    # 内参矩阵
dist = params["dist"]  # 畸变系数
# ==================================================================

# ArUco 设置
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()

# 打开摄像头
cap = cv2.VideoCapture(1)

# 【改成你打印的 ArUco 真实物理尺寸，单位：米！】
MARKER_SIZE = 0.05  # 5cm → 0.05m，自己按实际改

print("按 q 退出")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 检测 ArUco 码
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        # 画框
        aruco.drawDetectedMarkers(frame, corners, ids)

        # 遍历每个码
        for i in range(len(ids)):
            # 估计位姿：旋转向量 rvec、平移向量 tvec
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(
                corners[i], MARKER_SIZE, mtx, dist
            )

            # 平移向量：相机相对于码的位置（单位：米）
            x = tvec[0][0][0]
            y = tvec[0][0][1]
            z = tvec[0][0][2]

            # 旋转向量 → 欧拉角（度）
            rmat, _ = cv2.Rodrigues(rvec)
            pitch = np.arctan2(rmat[2, 1], rmat[2, 2]) * 180 / np.pi
            yaw   = np.arcsin(-rmat[2, 0]) * 180 / np.pi
            roll  = np.arctan2(rmat[1, 0], rmat[0, 0]) * 180 / np.pi

            # 画坐标轴
            cv2.drawFrameAxes(frame, mtx, dist, rvec, tvec, MARKER_SIZE*0.5)

            # 屏幕显示
            info = f"ID:{ids[i][0]}  X:{x:.2f} Y:{y:.2f} Z:{z:.2f}m"
            angle_info = f"P:{pitch:.0f} Y:{yaw:.0f} R:{roll:.0f}deg"
            cv2.putText(frame, info, (10, 60+i*40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)
            cv2.putText(frame, angle_info, (10, 90+i*40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255),2)
            
            # print(info)

    cv2.imshow("ArUco position", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()