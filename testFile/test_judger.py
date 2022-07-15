# import cv2
# imagepath = "./1.jpg"

# img = cv2.imread(imagepath)
# cv2.imshow("image", img)
# cv2.waitKey(0)

import cv2
import numpy as np
import matplotlib.pyplot as plt


# 使用2g-r-b分离土壤与背景

src = cv2.imread("./4.jpeg")

point_size = 1
point_color = (0, 0, 255)  # BGR
thickness = 4  # 可以为 0 、4、8

# # 要画的点的坐标
# points_list = [(10, 10), (10, 790)]

# for point in points_list:
#     cv2.circle(src, point, point_size, point_color, thickness)
cv2.imshow('src', src)

# 转换为浮点数进行计算
fsrc = np.array(src, dtype=np.float32) / 255.0
(b, g, r) = cv2.split(fsrc)
#gray = 2 * g - b - r
gray = g - b

# 求取最大值和最小值
(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

# print(cv2.minMaxLoc(gray))

# 计算直方图
# hist = cv2.calcHist([gray], [0], None, [256], [minVal, maxVal])
# plt.plot(hist)
# plt.show()


# 转换为u8类型，进行otsu二值化
gray_u8 = np.array((gray - minVal) / (maxVal - minVal) * 255, dtype=np.uint8)
(thresh, bin_img) = cv2.threshold(gray_u8, -1.0, 255, cv2.THRESH_OTSU)
cv2.imshow('bin_img', bin_img)
(minVal1, maxVal1, minLoc1, maxLoc1) = cv2.minMaxLoc(bin_img)
print(cv2.minMaxLoc(bin_img))
print(bin_img.shape)
# 得到彩色的图像
(b8, g8, r8) = cv2.split(src)
color_img = cv2.merge([b8 & bin_img, g8 & bin_img, r8 & bin_img])
cv2.imshow('color_img', color_img)

cv2.waitKey()
cv2.destroyAllWindows()
