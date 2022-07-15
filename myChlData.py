import time
import matplotlib.pyplot as plt
import numpy as np


class myChlData:
    allData = []
    dataPiece = 0

    def __init__(self, time,  chl):
        self.time = time
        self.chl = chl
        myChlData.allData.append(self)
        myChlData.dataPiece += 1

    def myPrint():
        for data in myChlData.allData:
            print("time is:", data.time, ",chl is:", data.chl)

    def readFromFile(src):
        #src = './trial.txt'
        try:
            f = open(src, "r+", encoding="utf-8")
        except IOError:
            print("can't open the file")
        else:
            data = f.read().splitlines()
            n = int(data[0])
            for i in range(0, n):
                time = data[2*i+1]
                chl = int(data[2*i+2])
                myChlData(time, chl)
            f.close

    def saveToFile(src):
        try:
            f = open(src, 'w', encoding='utf-8')
        except IOError:
            print("can't open the file")
        else:
            f.write(str(myChlData.dataPiece) + '\n')
            for data in myChlData.allData:
                f.write(str(data.time) + '\n')
                f.write(str(data.chl) + '\n')
            f.close

    def drawChlLineChart():
        x_axis_data = list(range(1, myChlData.dataPiece + 1))
        y_axis_data = []

        for data in myChlData.allData:
            y_axis_data.append(data.chl)

        for x, y in zip(x_axis_data, y_axis_data):
            plt.text(x, y+0.3, '%.00f' % y, ha='center',
                     va='bottom', fontsize=7.5)  # y_axis_data1加标签数据

        plt.plot(x_axis_data, y_axis_data, 'b*--', alpha=0.5,
                 linewidth=1, label='acc')  # 'bo-'表示蓝色实线，数据点实心原点标注
        # plot中参数的含义分别是横轴值，纵轴值，线的形状（'s'方块,'o'实心圆点，'*'五角星   ...，颜色，透明度,线的宽度和标签 ，

        plt.legend()  # 显示上面的label
        plt.xlabel('time')  # x_label
        plt.ylabel('number')  # y_label

        # plt.ylim(-1,1)#仅设置y轴坐标范围
        plt.show()
