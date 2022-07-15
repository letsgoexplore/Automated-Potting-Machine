import serial
import time
T4 = 30

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
    print("空气湿度：", am, "%\n湿度：", temp, "摄氏度\n光强：", lgt, "lx\n土壤湿度：", gm, "%")
    time.sleep(T4)
