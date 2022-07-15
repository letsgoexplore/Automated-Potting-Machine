import RPi.GPIO as GPIO
import time
import math

# 舵机PWM最小度数和最大度数对应的占空比（参考https://www.bilibili.com/video/BV1wu411k7Zi/?spm_id_from=pageDriver&vd_source=7d05ac8f5cdf136f57944d766cf1b359）
# ROTATE_PWM_MIN = 3  # 需要手动调节， 调节方式参见上面视频链接
# ROTATW_PWM_MAX = 13
# ANGLE_MIN = 0
# ANGLE_MAX = 360
# 参见上面视频链接7:00的角度和PWM输入的变换
# def angleCal(angle):
#     return round((angle - ANGLE_MIN)*(ROTATW_PWM_MAX - ROTATE_PWM_MIN)/(ANGLE_MAX - ANGLE_MIN)+ROTATE_PWM_MIN, 2)

# GPIO口设置
MOVE_ENGINE = 7
SERVO_PINTOP = 11
SERVO_PINMID = 13  # middleservo GPIO17
SERVO_PINEND = 15  # end
RADIUS = 124  # 机械臂单臂长度为124mm
MOVE_ANGLE_MIN = 58
MOVE_ANGLE_MAX = 180

# 旋转舵机测量参数：对于本项目中的舵机而言，time.sleep相同时间内，2.5和10.46的正转和反转的角度相同
CCW_ROTATE_SPEED = 2.5
CW_ROTATE_SPEED = 12


def angleToDutyCycle(angle):
    return 2.5 + angle / 180.0 * 10


def degCalTime(angle):
    return round(angle*10/360, 3)


class engineMove:
    rotateAngle = 0
    hgt_level = 0     # 变化范围为(20,60)
    height = 0

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(MOVE_ENGINE, GPIO.OUT, initial=False)
        GPIO.setup(SERVO_PINTOP, GPIO.OUT, initial=False)
        GPIO.setup(SERVO_PINMID, GPIO.OUT, initial=False)
        GPIO.setup(SERVO_PINEND, GPIO.OUT, initial=False)
        self.rotateEgn = GPIO.PWM(MOVE_ENGINE, 50)
        self.ptop = GPIO.PWM(SERVO_PINTOP, 50)    # 初始频率为50HZ
        self.pmid = GPIO.PWM(SERVO_PINMID, 50)
        self.pend = GPIO.PWM(SERVO_PINEND, 50)
        self.rotateEgn.start(0)
        self.ptop.start(angleToDutyCycle(20))  # 舵机初始化角度为90
        self.pmid.start(angleToDutyCycle(40))
        self.pend.start(angleToDutyCycle(20))
        time.sleep(0.5)
        self.rotateEgn.ChangeDutyCycle(0)
        self.ptop.ChangeDutyCycle(0)  # 清空当前占空比，使舵机停止抖动
        self.pmid.ChangeDutyCycle(0)
        self.pend.ChangeDutyCycle(0)

    def moveFun(self, angle):  # 假定输入范围为20-60（包括60），这一个函数的意思是转动到这一个角度, 最后变换完要更新height值，这一值是sin（实际角度）
        self.ptop.ChangeDutyCycle(angleToDutyCycle(angle)-0.3)
        self.pend.ChangeDutyCycle(angleToDutyCycle(angle))
        self.pmid.ChangeDutyCycle(angleToDutyCycle(2 * angle))
        time.sleep(0.1)
        self.ptop.ChangeDutyCycle(0)  # 清空当前占空比，使舵机停止抖动
        self.pmid.ChangeDutyCycle(0)
        self.pend.ChangeDutyCycle(0)

        # 由于角度线性分布，测量出angle=20和angle=60的角度为58度和180度进行线性运算；这一表达式表达不完美，在此致歉
        agl = MOVE_ANGLE_MIN + \
            (MOVE_ANGLE_MAX - MOVE_ANGLE_MIN)*(angle-20)/(60-20)
        self.height =round( 2 * RADIUS * (math.sin((agl*3.1415)/360)),1)

    # 此处由于用到的是360度舵机，它的控制是通过time.sleep的时间控制的，所以在此就不写通用类了
    # def rotateFun(self, angle):
    #     self.rotateEgn.ChangeDutyCycle(rotateToDutyCycle(angle))
    #     time.sleep(0.1)
    #     self.rotateEgn.ChangeDutyCycle(0)

    ########################################################################################
    # 专用类函数
    # deg是指旋转的角度而非旋转到的角度，即ccwRotate(60)是在现有的角度控制舵机的同时，记得修改rotateDegree和height的实时值

    def ccwRotate(self, deg):
        if self.rotateAngle + deg < 360:
            self.rotateAngle += deg
            self.rotateEgn.ChangeDutyCycle(CCW_ROTATE_SPEED)
            time.sleep(degCalTime(deg))
            self.rotateEgn.ChangeDutyCycle(0)
            time.sleep(0.1)
        else:
            angle = 360 - self.rotateAngle
            self.rotateAngle = 360
            self.rotateEgn.ChangeDutyCycle(CCW_ROTATE_SPEED)
            time.sleep(degCalTime(angle))
            self.rotateEgn.ChangeDutyCycle(0)
            time.sleep(0.1)

    def cwRotate(self, deg):      # 控制舵机的同时，记得修改rotateDegree和height的实时值
        if self.rotateAngle - deg > 0:
            self.rotateAngle -= deg
            self.rotateEgn.ChangeDutyCycle(CW_ROTATE_SPEED)
            time.sleep(degCalTime(deg))
            self.rotateEgn.ChangeDutyCycle(0)
            time.sleep(0.1)
        else:
            angle = self.rotateAngle
            self.rotateAngle = 0
            self.rotateEgn.ChangeDutyCycle(CW_ROTATE_SPEED)
            time.sleep(degCalTime(angle))
            self.rotateEgn.ChangeDutyCycle(0)
            time.sleep(0.1)

    # 此处由于本项目中采取机械臂控制上下移动，所以精度有限，hgt代表转动的单位角度；控制舵机的同时，记得修改rotateDegree和height的实时值
    def upMove(self, hgt):
        if self.hgt_level + hgt < 60:
            self.hgt_level += hgt
            self.moveFun(self.hgt_level)
            time.sleep(0.5)
        else:
            self.hgt_level = 60
            self.moveFun(60)
            time.sleep(0.5)

    def downMove(self, hgt):      # 控制舵机的同时，记得修改rotateDegree和height的实时值
        if self.hgt_level - hgt > 20:
            self.hgt_level -= hgt
            self.moveFun(self.hgt_level)
            time.sleep(0.5)
        else:
            self.hgt_level = 20
            self.moveFun(20)
            time.sleep(0.5)

    def reRotate(self):  # 旋转舵机复位，控制舵机的同时，记得修改rotateDegree和height的实时值
        angle = self.rotateAngle
        self.rotateAngle = 0
        self.rotateEgn.ChangeDutyCycle(CW_ROTATE_SPEED)
        time.sleep(degCalTime(angle))
        self.rotateEgn.ChangeDutyCycle(0)
        time.sleep(0.1)

    def reMove(self):    # 竖直运动舵机复位，控制舵机的同时，记得修改rotateDegree和height的实时值
        self.hgt_level = 20
        self.moveFun(20)


# 测试脚本
# myEngine = engineMove()
# myEngine.upMove(3)
# time.sleep(3)
# myEngine.upMove(5)
# time.sleep(3)
# myEngine.upMove(10)
# time.sleep(3)
# myEngine.upMove(20)
# time.sleep(3)
# myEngine.downMove(3)
# time.sleep(3)
# myEngine.downMove(5)
# time.sleep(3)
# myEngine.downMove(10)
# time.sleep(3)
# myEngine.downMove(20)
# time.sleep(3)
# myEngine.upMove(100)
# time.sleep(5)
# myEngine.reMove()
