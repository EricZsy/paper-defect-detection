import cv2
import os
import time
import numpy as np
import perspective

def nothing(x):
    pass

def warp(img):

    # 缩小图片,可按照实际图像调整
    size = img.shape
    while size[0]*size[1] > 1000*1000:
        img = cv2.pyrDown(img)
        size = img.shape
    cv2.imshow('original', img)
    # 灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    black = np.zeros(gray.shape, dtype=np.uint8)

    # 创建滑动条a
    cv2.namedWindow('detected')
    # cv2.namedWindow('hough')
    cv2.createTrackbar('max', 'detected', 50, 200, nothing)
    cv2.createTrackbar('GssKrnlSz', 'detected', 3, 10, nothing)
    # cv2.createTrackbar('thrshld', 'hough', 20, 200, nothing)

    while(1):
        if cv2.waitKey(30) & 0xFF== 97:
            break
        # 获取滑动值
        x = img

        maxVal = cv2.getTrackbarPos('max', 'detected')  # canny最大阈值
        kernel_size = 2 * cv2.getTrackbarPos('GssKrnlSz', 'detected') + 1  # 高斯核大小只能是奇数
        #maxVal = 50
        #kernel_size = 7

        # 高斯模糊
        blur = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

        # 边缘检测
        edge = cv2.Canny(blur, int(maxVal / 2), maxVal)
        #cv2.imshow('1.canny', edge)

        # 闭运算
        dilated = cv2.dilate(edge, None, iterations=2)  # 膨胀
        eroded = cv2.erode(dilated, None, iterations=1)  # 腐蚀
        # cv2.imshow('2.closed', eroded)

        # 轮廓检测
        image, contours, hier = cv2.findContours(eroded,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv2.contourArea, reverse=True)[:5]  # sorted(L, key=lambda x:x[1])
        out1 = cv2.drawContours(black.copy(), cnts, -1, 255, 1)

        # 轮廓点
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:  # 表明找到四个轮廓点
                screenCnt = approx
                break
        try:
            # 展示截取区域的拐点和最外4层轮廓
            out4 = cv2.drawContours(out1, screenCnt, -1, 255, 7)
            #cv2.imshow('3.screenCnt', out4)
            # 仿射变换
            warped = perspective.four_point_transform(img.copy(), screenCnt.reshape(4, 2))

            x = warped
            #cv2.imshow("5.origin", img)

        except:
            pass
        #cv2.imshow('corrected', x)
        paper = x
        paper_gray = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY)
        gaus = cv2.GaussianBlur(paper_gray, (5, 5), 0)
        blur = cv2.blur(paper_gray, (5, 5), 0)
        edge = cv2.Canny(gaus, 15, 30)
        edge1 = cv2.Canny(blur, 15, 30)

        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = 3
        params.maxThreshold = 200

        # Filter by Area.
        params.filterByArea = True
        params.minArea = 50

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.1

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.87

        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.01

        # Create a detector with the parameters
        ver = (cv2.__version__).split('.')
        if int(ver[0]) < 3:
            detector = cv2.SimpleBlobDetector(params)
        else:
            detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs.
        keypoints = detector.detect(paper_gray)

        if (len(keypoints)):
            paper = cv2.drawKeypoints(paper_gray, keypoints, np.array([]), (0, 0, 255),
                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            hole_pos = []

            i = 0
            for x1 in keypoints[:]:
                hole_pos.append([int(keypoints[i].pt[0]), int(keypoints[i].pt[1])])
                i = i + 1
        else:
            pass

        # 闭操作
        dilated = cv2.dilate(edge, None, iterations=2)  # 膨胀
        eroded = cv2.erode(dilated, None, iterations=1)  # 腐蚀

        lines = cv2.HoughLinesP(eroded, 1, np.pi / 180, 100, minLineLength=80, maxLineGap=20)  # 100 80 20
        if lines is None:
            pass
        else:
            lines1 = lines[:, 0, :]  # 提取为二维
            x = lines1.shape[0]
            size = paper.shape

            foldxy = []
            if x > 200:
                lines = cv2.HoughLinesP(edge1, 1, np.pi / 180, 20, minLineLength=2, maxLineGap=5)
                lines1 = lines[:, 0, :]  # 提取为二维
                for x1, y1, x2, y2 in lines1[:]:
                    if (x1 < size[1] * 0.05 and x2 < size[1] * 0.05) or (
                            x1 > size[1] * 0.95 and x2 > size[1] * 0.95) or (
                                    y1 < size[0] * 0.05 and y2 < size[0] * 0.05) or (
                                    y1 > size[0] * 0.95 and y2 > size[0] * 0.95):
                        pass
                    else:
                        foldxy.append([x1, y1, x2, y2])
                # print(len(foldxy))
                for x1, y1, x2, y2 in foldxy[:]:
                    cv2.line(paper, (x1, y1), (x2, y2), (255, 255, 0), 1)
            else:
                for x1, y1, x2, y2 in lines1[:]:
                    if (x1 < size[1] * 0.05 and x2 < size[1] * 0.05) or (
                            x1 > size[1] * 0.95 and x2 > size[1] * 0.95) or (
                                    y1 < size[0] * 0.05 and y2 < size[0] * 0.05) or (
                                    y1 > size[0] * 0.95 and y2 > size[0] * 0.95):
                        pass
                    else:
                        # pass
                        foldxy.append([x1, y1, x2, y2])

                for x1, y1, x2, y2 in foldxy[:]:
                    cv2.line(paper, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # cv2.imshow(str(m), paper)
        cv2.imshow('detected', paper)

    return x


test_path = './test/'
#test_path = '../test_1/'
num = len([lists for lists in os.listdir(test_path) if os.path.isfile(os.path.join(test_path, lists))])
for w in range(1, num+1):
    img = cv2.imread(test_path + str(w) + ".jpg")
    a = warp(img)
    cv2.destroyAllWindows()
cv2.destroyAllWindows()
