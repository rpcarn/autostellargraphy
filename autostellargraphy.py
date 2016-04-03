from __future__ import print_function

import cv2
import operator
from scipy import ndimage
import time

# MPL may only be necessary for displaying plots
import numpy as np
from matplotlib import pyplot as plt

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
smallimg = None

###############
# Functions
###############

# Stop writing video if recording, otherwise do nothing
def stopVideo(out):
    if out == None or out.isOpened()==False:
        # print("Video closed")
        x = 1
    else:
        # print("Video out is open: " + str(out.isOpened()))
        out.release()
        print("Video closing")

# Start recording video if not already, otherwise write this frame
def recordVideo(imgframe,out):
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if out==None or out.isOpened()==False:
        millis = int(round(time.time() * 1000))
        out = cv2.VideoWriter('vid-output/output'+str(millis)+'.mp4',fourcc, 10, (imgframe.shape[1],imgframe.shape[0]))
        print("Video out is starting: " + str(out.isOpened()))
        return out
    else:
        out.write(imgframe)
        # print("Video out is writing: " + str(out.isOpened()))
        return out

def process_image(handimage,mht,thval,bgimg,testmf,offset,draw_dots,picture_in_picture,smallimg): #,fgbg):
    imgdc = None

    img_clr = handimage.copy();
    img = handimage.copy();

    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # invert the image.
    # when finding contours object should be white and background black
    img = (255-img);

    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(img,(5,5),0)

    # First output: the algorithm finds the optimal threshold value and
    # returns it. If Otsu thresholding is not used, retVal is same as the
    # threshold value you used.
    # Second output: the thresholded image.
    #ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    ret3, th3 = cv2.threshold(img,thval,255,cv2.THRESH_BINARY)

    # Copy the image/numpy array
    if testmf:
        imgdc = img_clr.copy()
    else:
        imgdc = bgimg.copy()

    # Find the contours in the binary image
    # "findContours modifies the image" verify.
    imgcon, contours, hierarchy = cv2.findContours(th3, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # the contours array contains a sub-array for each "object" found in the
    # image. ideally there is 1 object, the hand or person. but sometimes
    # anomalies or
    # artifacts become other objects. however, the preson should always be the
    # biggest object so loop through contours and extract the sub-array that
    # has the most items.
    # get the max of the len() of each sub-array
    clen = []
    for c in contours:
        clen.append(len(c))

    # if a contour array exists, start processing it
    if len(clen) > 0:
        # get the largest contour array
        max_index = clen.index(max(clen));
        cnt = contours[max_index]

        # Using the contours, find the convex hull (outer points)
        hull_pts = cv2.convexHull(cnt)
        hull = cv2.convexHull(cnt,returnPoints = False)

        # Find the convexity defects (concave points).
        # Return a list of contour
        # convexity defects, each one represented by a tuple
        # (start, end, depthpoints, depth). The start and end
        # points will be the fingertips, and the depthpoints
        # the space between the fingers.
        defects=cv2.convexityDefects(cnt,hull)

        # Convert curves to sharp points
        # Contour approximation
        # Higher pct of arc length returns fewer points
        # http://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html#gsc.tab=0
        # 0.015 is perfect for the hand
        epsilon = 0.015*cv2.arcLength(cnt,True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)

        # When there are too many contours, try using approx_cnt instead of cnt
        # epsilon_cnt = 0.0005*cv2.arcLength(cnt,True)
        # approx_cnt = cv2.approxPolyDP(cnt,epsilon_cnt,True)

        # Conversion
        appx = approx[:,0].tolist()

        # Calculate centroid of these points (not used)
        centroid = np.mean(appx,axis=0).astype(int)

        # Show the contour only if it looks like a hand (not used)
        # cmpr = cv2.matchShapes(cnt,mht,1,0)
        # if cmpr < .7 and cmpr > .05 and len(approx) in (10,11,12):
        # draw dots at approximation points
        # cv2.circle(imgdc,start,10,[255,0,0],-1)

        # Use if too many contours in cnt
        # cv2.drawContours(imgdc, approx_cnt, -1, (175,150,150), 2, lineType=cv2.FILLED, offset=offset)

        # Draw the contours and stars
        if draw_dots:
            cv2.drawContours(imgdc, cnt, -1, (175,150,150), 2, lineType=cv2.FILLED, offset=offset)
        else:
            # Draw polygon instead of contour dots
            pts = []
            for j in cnt[:,0].tolist():
                pts.append([j[0]+offset[0],j[1]+offset[1]])

            pts = np.array(pts, np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(imgdc,[pts],True,(175,150,150))

        if picture_in_picture:
            x_offset=imgdc.shape[1]-smallimg.shape[1]
            y_offset=imgdc.shape[0]-smallimg.shape[0]
            imgdc[y_offset:y_offset+smallimg.shape[0], x_offset:x_offset+smallimg.shape[1]] = smallimg

        # Draw the centroid as a star
        # cv2.circle(imgdc,tuple(map(operator.add,tuple(centroid),offset)),5,[200,200,200],-1)

        for i in range(approx.shape[0]):
            # Draw every 3rd circle (star)
            # if(i%3 == 0):
            start = tuple(approx[i,0])
            cv2.circle(imgdc,tuple(map(operator.add,start,offset)),3,[225,225,225],-1)
            # If doing the shape comparison, tell us when it worked
            # print("Hand! " + str(cmpr) + " : " + str(len(approx)));

        return (imgdc,approx,thval);
    else:
        # if perfectly white and no contours, return the original image
        # with nothing drawn on it
        return (img_clr,"404",thval)
