# Automated-Potting-Machine
In the README, we will first introduce our project, and then we will illustrate the structure of the codes under this folder.

## Part.1 Introduction of project
  The potting method is getting increasing widespread use in both daily life and agricultural research. But they either take lots of time and force to looking after them, to ensure them growing well, or requires lots of effort to measure and record their data. Therefore, we seek to discover a systematic way to automated cultivate and keep log of the plant. This structure can be easily derived to petri dish, insect box and other scenarios. The detailed information is provided in the Report.pdf  

  Then, we will introduce the basic function.(我们来介绍所有的功能:)
线程1：（自动）每t1时间，会自动调整高度到植株最高点位于图像的中心高度、此时记录控制高度的舵机的位置h1,h=h1+Y_LEN/2；在测定的过程中将对于线程上锁  
线程2：（自动）每t2时间，会自动调整高度到植株高度的一半，通过随机选取测量点，测量植株叶绿素的含量 （升级选项：旋转多次并且测定，取平均值）  
线程3：（手动）随时等待键盘响应，并且执行以下的操作  
  不用大写，都是小写  
  A：ccwRotate()：逆时针转动输入的度数  
  D: engineMove.cwRotate ()：顺时针转动输入的度数  
  R: engineMove.reRotate ()：旋转舵机复位  
  W: engineMove.upMove(): 向上舵机转动输入的度数   
  S: engineMove.downMove(): 向下舵机转动输入的度数  
  R: engineMove.reRotate(): 旋转舵机复位  
  C: chlMeasure: 叶绿素测量功能  
  H: hgtMeasure: 高度测量功能  
  B: drawChlLineChart: 显示目前叶绿素数据的折线图  
  N: drawHeightLineChart: 显示目前高度数据的折线图  
  J：FPGA接口1：光照手动自动切换：低电平为自动， 高电平为手动  
  K：FPGA接口2：光照模式调节：按一下发一个20ms脉冲  
  L：FPGA接口3：手动操控水泵的工作状态，低电平不工作，高电平工作；FPGA的水泵在自动工作，但有手动信息时会覆盖自动信息  
  Esc: 退出程序  
线程4：（自动）每t4时间，自动输出盆栽中空气湿度、温度、光照、土壤湿度  



## Part.2 Structure of the Codes
main.py: the main function of the project, with the height-tracing-and-measuring function, chlorophyll-tracing-and-measuring function, keyboard function, multi-threading function in it.  
myHeightData.py & myChlData.py: In these two files, we define the data structure and the functions of the height data and the chl data with the defination of the class.  
engineMove.py: we define the class engineMove, which encompasses the function of the engine used in our project. This part is based on the Raspberry Pi's RPi.GPIO.  
hgtFile.txt & chlFile.txt: after the program ended, the data recorded will be saved in the file. We don't read the history data from the file in our project, and the history data will be covered if new data is saved.  
gpioChart.txt: this file records the gpio we use.  
testFile: This folder contains the basic/simple funtion we used. Therefore, if with any problem, may search somethiing is this folder.  
