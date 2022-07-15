import time
import matplotlib.pyplot as plt
import numpy as np


class myHeightData:
    allData = []
    dataPiece = 0

    def __init__(self, time, height):
        self.time = time
        self.height = height
        myHeightData.allData.append(self)
        myHeightData.dataPiece += 1

    def myPrint():
        for data in myHeightData.allData:
            print("time is:", data.time, ",height is:",
                  data.height)

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
                height = int(data[2*i+2])
                myHeightData(time, height)
            f.close

    def saveToFile(src):
        try:
            f = open(src, 'w', encoding='utf-8')
        except IOError:
            print("can't open the file")
        else:
            f.write(str(myHeightData.dataPiece) + '\n')
            for data in myHeightData.allData:
                f.write(str(data.time) + '\n')
                f.write(str(data.height) + '\n')
            f.close

    def drawHeightLineChart():
        x_axis_data = list(range(1, myHeightData.dataPiece + 1))
        y_axis_data = []

        for data in myHeightData.allData:
            y_axis_data.append(data.height)

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


# myHeightData(time.ctime(time.time()), 2)
