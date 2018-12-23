import cv2
import numpy as np
import perspective

img = './test/5.jpg'

def nothing(x):
    pass

def warp(path):
    img = cv2.imread(path)
    # 缩小图片,可按照实际图像调整
    size = img.shape
    while size[0] * size[1] > 1000 * 1000:
        img = cv2.pyrDown(img)
        size = img.shape
    x=img
    # 灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    black = np.zeros(gray.shape, dtype=np.uint8)

    # 创建滑动条a
    cv2.namedWindow('1.canny')
    # cv2.namedWindow('hough')
    cv2.createTrackbar('max', '1.canny', 50, 200, nothing)
    cv2.createTrackbar('GssKrnlSz', '1.canny', 3, 10, nothing)
    # cv2.createTrackbar('thrshld', 'hough', 20, 200, nothing)


    # 主循环
    while (1):
        # 键盘检测,按下 a 退出
        if cv2.waitKey(30) & 0xFF== 97:
            break

        # 获取滑动值
        maxVal = cv2.getTrackbarPos('max', '1.canny')	# canny最大阈值
        kernel_size = 2 * cv2.getTrackbarPos('GssKrnlSz','1.canny') + 1 # 高斯核大小只能是奇数
        #maxVal = 50
        #kernel_size = 7

        # 高斯模糊
        blur = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

        # 边缘检测
        edge = cv2.Canny(blur, int(maxVal/2), maxVal)
        cv2.imshow('1.canny', edge)

        # 闭运算
        dilated  = cv2.dilate(edge, None, iterations = 2) # 膨胀
        eroded = cv2.erode(dilated, None, iterations = 1) # 腐蚀
        #cv2.imshow('2.closed', eroded)

        # 轮廓检测
        image, contours, hier = cv2.findContours(eroded,
            cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:5]	# sorted(L, key=lambda x:x[1])
        out1 = cv2.drawContours(black.copy(), cnts, -1, 255, 1)

        # 轮廓点
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02*peri, True)
            if len(approx) == 4: # 表明找到四个轮廓点
                screenCnt = approx
                break
        try:
            # 展示截取区域的拐点和最外4层轮廓
            out4 = cv2.drawContours(out1, screenCnt, -1, 255, 7)
            #cv2.imshow('3.screenCnt', out4)
            # 仿射变换
            warped = perspective.four_point_transform(img.copy(), screenCnt.reshape(4, 2))
            x=warped

        except:
            pass
        cv2.imshow("5.origin", img)
        cv2.imshow("4.corrected", x)
    #cv2.imwrite('paper.png',warped)

    cv2.waitKey()
    cv2.destroyAllWindows()

warp(img)


