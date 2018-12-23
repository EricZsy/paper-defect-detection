import cv2
import numpy as np
import time

def detect(paper, m, sheet):
    defect="无"
    paper1 = paper
    time0 = time.time()
    paper_gray = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY)
    gaus = cv2.GaussianBlur(paper_gray,(5, 5), 0)
    blur = cv2.blur(paper_gray,(5, 5), 0)
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
        defect='有'
        paper = cv2.drawKeypoints(paper_gray, keypoints, np.array([]), (0, 0, 255),
                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        hole_pos = []

        i = 0
        for x1 in keypoints[:]:
            hole_pos.append([int(keypoints[i].pt[0]), int(keypoints[i].pt[1])])
            i = i + 1


        cv2.imwrite("./result/hole/" + str(m) + ".jpg", paper)
        sheet.cell(row=m+1, column=5, value=len(hole_pos))
        sheet.cell(row=m+1, column=6, value=str(hole_pos))

    else:
        sheet.cell(row=m+1, column=5, value=0)
        sheet.cell(row=m+1, column=6, value='NONE')


    #闭操作
    dilated = cv2.dilate(edge, None, iterations=2)  # 膨胀
    eroded = cv2.erode(dilated, None, iterations=1)  # 腐蚀

    lines = cv2.HoughLinesP(eroded,1,np.pi/180,100,minLineLength=80,maxLineGap=20)#100 80 20
    if lines is None:
        #print('No folds!')
        sheet.cell(row=m+1, column=3, value=0)
        sheet.cell(row=m+1, column=4, value='NONE')
        sheet.cell(row=m+1, column=7, value=0)
        sheet.cell(row=m+1, column=8, value='NONE')

    else:
        defect='有'
        lines1 = lines[:, 0, :]  # 提取为二维
        x = lines1.shape[0]
        size = paper.shape

        foldxy = []
        if x>200:
            lines = cv2.HoughLinesP(edge1, 1, np.pi / 180, 20, minLineLength=2, maxLineGap=5)
            lines1 = lines[:, 0, :]  # 提取为二维
            for x1, y1, x2, y2 in lines1[:]:
                if (x1 < size[1] * 0.05 and x2 < size[1] * 0.05) or (x1 > size[1] * 0.95 and x2 > size[1] * 0.95) or (
                        y1 < size[0] * 0.05 and y2 < size[0] * 0.05) or (y1 > size[0] * 0.95 and y2 > size[0] * 0.95):
                    pass
                else:
                    foldxy.append([x1, y1, x2, y2])
            #print(len(foldxy))
            for x1, y1, x2, y2 in foldxy[:]:
                cv2.line(paper1, (x1, y1), (x2, y2), (255, 255, 0), 1)
                cv2.line(paper, (x1, y1), (x2, y2), (255, 255, 0), 1)
            cv2.imwrite("./result/stripe/" + str(m) + ".jpg", paper1)
            sheet.cell(row=m+1, column=3, value=0)
            sheet.cell(row=m+1, column=4, value='NONE')
            sheet.cell(row=m+1, column=7, value=len(foldxy))
            sheet.cell(row=m+1, column=8, value=str(foldxy))
        else:
            for x1, y1, x2, y2 in lines1[:]:
                if (x1 < size[1] * 0.05 and x2 < size[1] * 0.05) or (x1 > size[1] * 0.95 and x2 > size[1] * 0.95) or (
                                y1 < size[0] * 0.05 and y2 < size[0] * 0.05) or (
                        y1 > size[0] * 0.95 and y2 > size[0] * 0.95):
                    pass
                else:
                    foldxy.append([x1, y1, x2, y2])

            for x1, y1, x2, y2 in foldxy[:]:
                cv2.line(paper1, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.line(paper, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imwrite("./result/fold/" + str(m) + ".jpg", paper1)
            sheet.cell(row=m+1, column=3, value=len(foldxy))
            sheet.cell(row=m+1, column=4, value=str(foldxy))
            sheet.cell(row=m+1, column=7, value=0)
            sheet.cell(row=m+1, column=8, value='NONE')
    time1 = time.time()
    print(str(m)+'.time: %.3f' %(time1-time0))
    sheet.cell(row=m+1, column=9, value=defect)
    #cv2.imshow(str(m), paper)
    if defect=='有':
        cv2.imwrite("./result/defect_yes/" + str(m) + ".jpg", paper)
    else:
        cv2.imwrite("./result/defect_no/" + str(m) + ".jpg", paper)
    return paper
