import cv2
import time
import sys
import cv2
import numpy as np


def video_demo():
    capture = cv2.VideoCapture(0)  # 0为电脑内置摄像头
    while(True):
        ret, frame = capture.read()  # 摄像头读取,ret为是否成功打开摄像头,true,false。 frame为视频的每一帧图像
        frame = cv2.flip(frame, 1)  # 摄像头是和人对立的，将图像左右调换回来正常显示。
        cv2.imshow("video", frame)
        print("begin")
        keyResult = cv2.waitKey(10000)
        if keyResult & 0xFF == 97:  # A：ccwRotate()：逆时针转动输入的度数

            print("Thread3 gets the lock")
            print('A')

            print("Thread3 releases the lock")
        elif keyResult & 0xFF == 100:  # D: cwRotate ()：顺时针转动输入的度数

            print("Thread3 gets the lock")
            print('D')

            print("Thread3 releases the lock")
        elif keyResult & 0xFF == 114:  # R: reotate ()：旋转舵机复位

            print("Thread3 gets the lock")
            print('R')

            print("Thread3 releases the lock")
        elif keyResult & 0xFF == 119:  # W: upMove(): 向上舵机转动输入的度数

            print("Thread3 gets the lock")
            print('W')

            print("Thread3 releases the lock")
        elif keyResult & 0xFF == 115:  # S: downMove(): 向下舵机转动输入的度数

            print("Thread3 gets the lock")
            print('S')

            print("Thread3 releases the lock")
        elif keyResult & 0xFF == 104:  # H: hgtMeasure: 高度测量功能

            print("Thread3 gets the lock")
            print('H')

            print("Thread3 releases the lock")
        elif keyResult & 0xFF == 99:  # C: chlMeasure: 叶绿素测量功能

            print("Thread3 gets the lock")
            print('C')

            print("Thread3 releases the lock")
        elif keyResult & 0xFF == 106:  # J: drawHeightLineChart: 显示目前高度数据的折线图
            print('J')
        elif keyResult & 0xFF == 107:  # K: drawChlLineChart: 显示目前叶绿素数据的折线图
            print('K')
        elif keyResult & 0xFF == 27:  # Esc: 退出程序
            print('program ended')
            sys.exit(0)


video_demo()
cv2.destroyAllWindows()
