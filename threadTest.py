# 展示所用程序
# 初始声明：本代码一共分为
# Period 1: import各种包
# Period 2: 预设全局变量
# Period 3: CV（计算机视觉）模块函数
# Period 4: 键盘功能函数
# Period 5: 多线程类设计
# Period 6: 主函数
# 在本文件的六个部分外，myHeightData, myChlData, engineMove三个.py文件中分别有同名的类，实现的功能分别为：
# myHeightData: 规定高度的数据类型，自动存储函数，数据绘制成折线图函数
# myChlData   : 规定叶绿素含量的数据类型，自动存储函数，数据绘制成折线图函数
# engineMove  : 旋转舵机和竖直运动舵机的实现函数
# 本质上来讲，CV模块函数、多线程类设计也应该独立为文件，但是由于程序编写生成的过程中需要一些阶段性产出，所以它们因为历史原因就以目前的形式存在于主函数中

# 然后我们来介绍所有的功能
# 线程1：（自动）每t1时间，会自动调整高度到植株最高点位于图像的中心高度、此时记录控制高度的舵机的位置h1,h=h1+Y_LEN/2；在测定的过程中将对于线程上锁
# 线程2：（自动）每t2时间，会自动调整高度到植株高度的一半，通过随机选取测量点，测量植株叶绿素的含量 （升级选项：旋转多次并且测定，取平均值）
# 线程3：（手动）随时等待键盘响应，并且执行以下的操作
# 不用大写，都是小写
# A：ccwRotate()：逆时针转动输入的度数
# D: engineMove.cwRotate ()：顺时针转动输入的度数
# R: engineMove.reRotate ()：旋转舵机复位
# W: engineMove.upMove(): 向上舵机转动输入的度数
# S: engineMove.downMove(): 向下舵机转动输入的度数
# R: engineMove.reRotate(): 旋转舵机复位
# C: chlMeasure: 叶绿素测量功能
# H: hgtMeasure: 高度测量功能
# B: drawChlLineChart: 显示目前叶绿素数据的折线图
# N: drawHeightLineChart: 显示目前高度数据的折线图
# J：FPGA接口1：光照手动自动切换：低电平为自动， 高电平为手动
# K：FPGA接口2：光照模式调节：按一下发一个20ms脉冲
# L：FPGA接口3：手动操控水泵的工作状态，低电平不工作，高电平工作；FPGA的水泵在自动工作，但有手动信息时会覆盖自动信息
# Esc: 退出程序
# 线程4：（自动）每t4时间，自动输出盆栽中空气湿度、温度、光照、土壤湿度

# 在此说明一下图像矩阵的索引方式：
# 左上角是[0][0]
# [行][列]


# Period 1: import各种包
import threading
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from myChlData import myChlData
from myHeightData import myHeightData
from engineMove import engineMove
import random
import sys
import os
import RPi.GPIO as GPIO
import serial


################################################################################################################
# Period 2: 预设定全局变量
PRE_ACCURACY = 3        # 预采集的时候收集多少组数据
GREEN_THRESH = 0.5
X_LEN = 100             # 单位mm,与摄像头距离花盆半径长度的平面上 被拍入图像中的内容的实际长度
Y_LEN = 80             # 单位mm,与摄像头距离花盆半径长度的平面上 被拍入图像中的内容的实际高度
CHL_RANDOM_POINT = 1000   # 测定叶绿素(chlorophyll)时随机选取测量点的数量
MEASURE_ACCURACY = 3    # 考虑到植株不同角度观察的叶片的颜色整体分布不一定一致，此处选择从多个角度进行分别测量取平均
HEIGHT_ACCURACY = 30     # 最高的高度要至少包括heightAccuracy个绿色像素点才算最高点
ERROR_ACCURACY = 20     # 当最高的高度位于图像中最上或最下ERROR_ACCURACY个绿色像素点的范围内，不认为最高点在图像中
# 中心高度的容差范围，(y > Y_LENGTH/2 - 30) and (y < Y_LENGTH/2 + 30)
BASE_HEIGHT = 31       # 土的高度距离机械臂底端的距离
HEIGHT_RANGE = 210.0
ROTATE_ANGLE = 180     # 旋转舵机旋转的范围，此处默认为180度
T1 = 30                # 线程1的间隔时间
T2 = 45                # 线程2的间隔时间
T4 = 30                # 线程4的间隔时间
WAITSENSITIVITY = 30   # 单位ms,指的是每多少ms在键盘接收一次按键信息

# 文件参数
HEIGHT_SRC = "./heightFile.txt"  # 高度记录的文件
CHL_SRC = "./chlFile.txt"        # 叶绿素记录的文件

# 舵机参数
MOVE_SINGLE_DIS = 1  # 每按一次按键upMove或者downMove，舵机移动向上或者向下移动1个单位角度
ROTATE_SINGLE_ANG = 3  # 每按一次按键cwRotate或者ccwRotate，旋转舵机旋转1度


################################################################################################################
# Period 3: CV（计算机视觉）模块函数
def leafJudger(src):
    # 将src转成浮点数；考虑到环境中会出现蓝色分量，故而选取灰度的计算值为绿色减去蓝色分量
    fsrc = np.array(src, dtype=np.float32) / 255.0
    (b, g, r) = cv2.split(fsrc)
    gray1 = g - b  # gray1是作为阈值分割的判据，这是通过实操后发现gray1的分隔效果更加好
    gray2 = g    # gray2是参考吴少俊论文中g-r和chl的线性度最好，故而作为叶绿素含量的判据

    # 寻找灰度最大值
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray1)
    # print(cv2.minMaxLoc(gray1))

    # 二值化处理
    gray_u8 = np.array((gray1 - minVal) / (maxVal - minVal)
                       * 255, dtype=np.uint8)
    (thresh, bin_img) = cv2.threshold(gray_u8, -1.0, 255, cv2.THRESH_OTSU)
    #cv2.imshow('bin_img', bin_img)
    # print(thresh)
    return (thresh, bin_img, gray2)


# 会自动调整高度到植株最高点位于图像的中心高度、此时记录控制高度的舵机的位置h1,h=h1+Y_LEN/2
def hgtMeasure(pic):
    # src = cv2.imread("./4.jpeg")  # Debug所用数据
    # src = Snapshot
    (thresh, bin_img, __) = leafJudger(pic)
    # if thresh < BASIC_THRESH:
    #     print('the plant is not in the view')
    #     raise MyError('Plant not in the view')
    for y in range(1, Y_LENGTH):
        counter = 0
        for x in range(1, X_LENGTH):
            if bin_img[y][x] == 255:
                counter += 1
        if counter >= HEIGHT_ACCURACY:
            return y
    return 0


def heightMeasure():
    myEngine.reMove()
    myEngine.upMove(1)
    myEngine.reMove()
    myEngine.reMove()
    while True:
        time.sleep(1)
        ret, frame = capture.read()
        frame = cv2.flip(frame, 1)
        g = chlMeasure(frame)
        if myEngine.hgt_level == 60:
            raise MyError('Height Error')
        if g - BASIC_LIGHT > GREEN_THRESH:
            # print("end searching")
            break
        else:
            myEngine.upMove(4)
            time.sleep(3)
    while True:
        ret, frame = capture.read()  # 摄像头读取,ret为是否成功打开摄像头,true,false。 frame为视频的每一帧图像
        frame = cv2.flip(frame, 1)
        y = hgtMeasure(frame)
        g = chlMeasure(frame)
        if ((y < float(Y_LENGTH/2) - HEIGHT_RANGE) and (myEngine.hgt_level == 40)) or ((y > float(Y_LENGTH/2) + HEIGHT_RANGE) and (myEngine.hgt_level == 40)):
            raise MyError('Height Error')
            # return -1
        if (y > float(Y_LENGTH/2) - HEIGHT_RANGE) and (y < float(Y_LENGTH/2) + HEIGHT_RANGE):  # 在一定范围内就认为h已然介于中间位置
            return round(myEngine.height + (0.5-float(y)/Y_LENGTH)*Y_LEN - BASE_HEIGHT, 1)
        if (y < ERROR_ACCURACY and g - BASIC_LIGHT > GREEN_THRESH+10):
            myEngine.upMove(5)
            time.sleep(0.3)
            continue
        if (y < float(Y_LENGTH/2) - HEIGHT_RANGE and g - BASIC_LIGHT > GREEN_THRESH+7):
            myEngine.upMove(2)
            time.sleep(0.3)
            continue
        if (y > Y_LENGTH - ERROR_ACCURACY and g - BASIC_LIGHT > GREEN_THRESH+10):
            myEngine.downMove(5)
            time.sleep(0.3)
            continue
        if (y > Y_LENGTH/2 + HEIGHT_RANGE and g - BASIC_LIGHT > GREEN_THRESH+10):
            myEngine.downMove(2)
            time.sleep(0.3)
            continue
        else:
            raise MyError('Height Error')
            # return -

# 随机选取若干叶片上的测量点(全局变量中设定的数量为chl_random_point) 测定当前图像的叶绿素含量
# 单次测量叶绿素的函数。但是注意，在单次测量的函数中不包括自动调节高度，使用chlMeasure的先决条件是图像中确实存在绿色色点


def chlMeasure(pic):
    # src = cv2.imread("./4.jpeg")
    (thresh, bin_img, gray2) = leafJudger(pic)
    counter = 0
    adder = 0
    while counter < CHL_RANDOM_POINT:
        x = random.randint(1, X_LENGTH-1)
        y = random.randint(1, Y_LENGTH-1)
        if bin_img[y][x]:
            adder += gray2[y][x]
            counter += 1
    return round((adder/CHL_RANDOM_POINT)*255, 2)


def totalChlMeasure():
    myEngine.reRotate()
    try:
        hgt = heightMeasure()
    except:
        print('the height exceed the measuring range or the plant is not in the view')
    else:
        myEngine.downMove(myEngine.hgt_level/2)
    finally:
        totalAdder = 0
        ret, frame = capture.read()
        totalAdder += chlMeasure(frame)
        for i in range(1, MEASURE_ACCURACY):
            myEngine.ccwRotate(ROTATE_ANGLE/MEASURE_ACCURACY)
            ret, frame = capture.read()
            totalAdder += chlMeasure(frame)
        myEngine.reRotate()
        return totalAdder/MEASURE_ACCURACY


################################################################################################################
# Period 4: 键盘响应函数
def waitRequestThread():
    while True:
        ret, frame = capture.read()  # 摄像头读取,ret为是否成功打开摄像头,true,false。 frame为视频的每一帧图像
        frame = cv2.flip(frame, 1)  # 摄像头是和人对立的，将图像左右调换回来正常显示。
        cv2.imshow("video", frame)
        keyResult = cv2.waitKey(40)
        if keyResult & 0xFF == 97:  # a：ccwRotate()：逆时针转动输入的度数
            threadLock.acquire()
            # print('A')
            myEngine.ccwRotate(ROTATE_SINGLE_ANG)
            threadLock.release()
        elif keyResult & 0xFF == 100:  # d: myEngine.cwRotate ()：顺时针转动输入的度数
            threadLock.acquire()
            # print('D')
            myEngine.cwRotate(ROTATE_SINGLE_ANG)
            threadLock.release()
        elif keyResult & 0xFF == 114:  # r: reotate ()：旋转舵机复位
            threadLock.acquire()
            # print('R')
            myEngine.reRotate()
            threadLock.release()
        elif keyResult & 0xFF == 119:  # w: myEngine.upMove(): 向上舵机转动输入的度数
            threadLock.acquire()
            myEngine.upMove(MOVE_SINGLE_DIS)
            threadLock.release()
        elif keyResult & 0xFF == 115:  # s: myEngine.downMove(): 向下舵机转动输入的度数
            threadLock.acquire()
            myEngine.downMove(MOVE_SINGLE_DIS)
            threadLock.release()
        elif keyResult & 0xFF == 104:  # h: hgtMeasure: 高度测量功能
            threadLock.acquire()
            print("################### 手动高度测量 ###################")
            try:
                height = heightMeasure()
            except:
                print(
                    'the height exceed the measuring range or the plant is not in the view')
            else:
                nowTime = time.ctime(time.time())
                myHeightData(nowTime, height)
                print("time:", nowTime, ", Height is:", height, " (mm)")
            finally:
                threadLock.release()

        elif keyResult & 0xFF == 103:  # g: chlMeasure: 叶绿素测量功能
            threadLock.acquire()
            nowTime = time.ctime(time.time())
            chl = round(totalChlMeasure()-BASIC_LIGHT, 2)
            if chl < 0:
                chl = 0
            print("################### 手动叶绿素测量 ###################")
            print("time:", nowTime, ", chlorophyll is:", chl)
            threadLock.release()

        elif keyResult & 0xFF == 110:  # n: drawHeightLineChart: 显示目前高度数据的折线图
            myHeightData.drawHeightLineChart()
        elif keyResult & 0xFF == 98:  # b: drawChlLineChart: 显示目前叶绿素数据的折线图
            myChlData.drawChlLineChart()
        elif keyResult & 0xFF == 106:  # j: 切换光照手动或自动模式
            print("################# Light Mode Switch #################")
            GPIO.output(LIGHT_MODE, not GPIO.input(LIGHT_MODE))
        elif keyResult & 0xFF == 107:  # k: 光照模式调节：按一下发一个脉冲
            print("############### Light Intensity Switch ###############")
            GPIO.output(LIGHT_SGN, GPIO.HIGH)
            time.sleep(0.02)
            GPIO.output(LIGHT_SGN, GPIO.LOW)
        # elif keyResult & 0xFF == 118:  # v: 水泵手动自动切换 ：低电平为自动， 高电平为手动
        #     GPIO.output(PUMP_MODE,not GPIO.input(LIGHT_MODE))
        elif keyResult & 0xFF == 108:  # l: 水泵手动模式下工作信号 ：在手动模式下，低电平不工作，高电平工作
            print("################## Pump Switch ###################")
            GPIO.output(PUMP_SGN, not GPIO.input(PUMP_SGN))
        elif keyResult & 0xFF == 27:  # Esc: 退出程序
            print('program ended')
            myChlData.saveToFile(CHL_SRC)
            myHeightData.saveToFile(HEIGHT_SRC)
            GPIO.cleanup()
            os._exit(0)
        time.sleep(0.2)


################################################################################################################
# Period 5: 多线程类设计
exitFlag = 0
workingSgn = 0   # 当一个测量过程正在进行中时


class myThread (threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        # 第一线程：（自动）每t1时间，会自动调整高度到植株最高点位于图像的中心高度、此时记录控制高度的舵机的位置h1,h=h1+Y_LEN/2；在测定的过程中将对于线程上锁
        if self.threadID == 1:
            print("########### Starting " + self.name + " ###########")
            while True:
                if exitFlag:
                    (threading.Thread).exit()
                threadLock.acquire()
                print("################### 自动高度测量 ###################")
                # print("Thread1 gets the lock")
                try:
                    height = heightMeasure()
                except:
                    print(
                        'the height exceed the measuring range or plant is not in the view')
                else:
                    nowTime = time.ctime(time.time())
                    myHeightData(nowTime, height)
                    print("time:", nowTime, ", Height is:", height, " (mm)")

                finally:
                    threadLock.release()
                    # print("Thread1 releases the lock")
                    time.sleep(T1)
            print("Exiting " + self.name)

        # 第二线程：（自动）每t2时间，会自动调整高度到植株高度的一半，通过随机选取测量点，测量植株叶绿素的含量 （升级选项：旋转多次并且测定，取平均值）
        if self.threadID == 2:
            print("########### Starting " + self.name + " ###########")
            while True:
                if exitFlag:
                    (threading.Thread).exit()
                threadLock.acquire()
                print("################### 自动叶绿素测量 ###################")
                nowTime = time.ctime(time.time())
                chl = round(totalChlMeasure()-BASIC_LIGHT, 2)
                if chl < 0:
                    chl = 0
                myChlData(nowTime, chl)
                print("time:", nowTime, ", chlorophyll is:", chl)
                threadLock.release()
                time.sleep(T2)
            print("Exiting " + self.name)

        # 第三线程：不断监听键盘的输入并且执行响应按键的函数
        if self.threadID == 3:
            print("########### Starting " + self.name + " ###########")
            if exitFlag:
                (threading.Thread).exit()
            waitRequestThread()
            print("Exiting " + self.name)

        # 第四线程：接收FPGA的数据信息
            # 数据样例：59327600232189\n
            # 空气湿度：59.3%
            # 温度：27.6摄氏度
            # 光强：(00)232 lx（高位零没有缺省，保持发送数据格式一致）
            # 土壤湿度：18.9%
        if self.threadID == 4:
            print("########### Starting " + self.name + " ###########")
            ted = serial.Serial(port="/dev/ttyAMA1", baudrate=9600)
            while True:
                while True:
                    sgn = str(ted.read(1), 'utf-8')
                    if(sgn == 'J'):
                        break
                am1 = int(str(ted.read(1), 'utf-8'))
                am2 = int(str(ted.read(1), 'utf-8'))
                am3 = int(str(ted.read(1), 'utf-8'))
                t1 = int(str(ted.read(1), 'utf-8'))
                t2 = int(str(ted.read(1), 'utf-8'))
                t3 = int(str(ted.read(1), 'utf-8'))
                l1 = int(str(ted.read(1), 'utf-8'))
                l2 = int(str(ted.read(1), 'utf-8'))
                l3 = int(str(ted.read(1), 'utf-8'))
                l4 = int(str(ted.read(1), 'utf-8'))
                l5 = int(str(ted.read(1), 'utf-8'))
                gm1 = int(str(ted.read(1), 'utf-8'))
                gm2 = int(str(ted.read(1), 'utf-8'))
                gm3 = int(str(ted.read(1), 'utf-8'))
                am = am1*10+am2+am3*0.1
                temp = t1*10+t2+t3*0.1
                lgt = l1*10000+l2*1000+l3*100+l4*10+l5
                gm = gm1*10+gm2+gm3*0.1
                print("################### FPGA信息流 ###################")
                print("空气湿度：", am, "%\n湿度：", temp,
                      "摄氏度\n光强：", lgt, "lx\n土壤湿度：", gm, "%")
                time.sleep(T4)
                ted.flushInput()


################################################################################################################
# Period 6: 自定义异常函数
class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

################################################################################################################
# Period 7: 主函数执行


# 打开摄像头
capture = cv2.VideoCapture(0)  # 0为电脑内置摄像头
ret, frame = capture.read()  # 摄像头读取,ret为是否成功打开摄像头,true,false。 frame为视频的每一帧图像
X_LENGTH = frame.shape[1]        # x方向像素点个数
Y_LENGTH = frame.shape[0]          # y方向像素点个数
print("摄像头像素为", X_LENGTH, Y_LENGTH)
print("正在采集环境信息，请勿在摄像头视野内放置植物")
time.sleep(1)
print("正在采集中，请稍等")
my_counter = 0
my_thresh = 0
my_light = 0
while True:
    if(my_counter == PRE_ACCURACY):
        break
    ret, frame = capture.read()
    (thresh, __, __) = leafJudger(frame)
    my_thresh += thresh
    my_light += chlMeasure(frame)
    my_counter += 1

BASIC_LIGHT = my_light/PRE_ACCURACY
BASIC_THRESH = my_thresh/PRE_ACCURACY
print("basic_light:", BASIC_THRESH)
print("采集完毕，正在启动多线程")

# 创建线程锁
threadLock = threading.Lock()
threads = []

# 初始化树莓派通信接口
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
LIGHT_MODE = 16
LIGHT_SGN = 18
# PUMP_MODE =36     # FPGA的水泵在自动工作，但有手动信息时会覆盖自动信息,所以此处不需要PUMP_MODE的输出端口来进行模式转换
PUMP_SGN = 22
GPIO.setup(LIGHT_MODE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LIGHT_SGN, GPIO.OUT, initial=GPIO.LOW)
# GPIO.setup(PUMP_MODE,GPIO.OUT,initial = GPIO.LOW)       # FPGA的水泵在自动工作，但有手动信息时会覆盖自动信息,所以此处不需要PUMP_MODE的输出端口来进行模式转换
GPIO.setup(PUMP_SGN, GPIO.OUT, initial=GPIO.LOW)

# 初始化舵机
myEngine = engineMove()

# 创建新线程
thread1 = myThread(1, "Auto-hgtMeasure")
thread2 = myThread(2, "Auto-chlMeasure")
thread3 = myThread(3, "Manual-control")
thread4 = myThread(4, "Auto-FPGA")

# 开启线程
thread1.start()
thread2.start()
thread3.start()
thread4.start()
