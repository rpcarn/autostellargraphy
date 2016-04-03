import numpy as np
import cv2
from autostellargraphy import process_image, recordVideo, stopVideo

# Initialize this variable
out = None

# Video source
# Webcam:
# cap = cv2.VideoCapture(0)
# File:
cap = cv2.VideoCapture('rsc-vid/vid1.mp4')

# w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
# h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

#################################################
# Settings
#################################################

# Crop the frames
cropImg = True

# Cropping for vid1.mp4
#left side
ws = 100
we = 800
# top
hs = 20
he = 430

# The input video's height and width
# ws = 0
# we = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# hs = 0
# he = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Crop for the hand video, not rotated
# ws = 0
# we = 480
# hs = 0
# he = 120


# Rotate the frames
rotateImg = True
rotangle = 140


# Show the original video instead of the
# constellation
testmf = False


# Record videos while the script is running
recVids = False
# Only record video if the number of appx
# points (stars in the constellation) is
# greater than this number
num_points = 0


# Add a border so that when the image is
# rotated, the corners are not clipped
borderFlag = True
btop = 100
bbot = 150
bleft = 100
bright = 150


# Resize the original video by setting its new width
# so that it fits in the background image
size_of_constellation = 400.0

# Resize the background image by setting its new width:
size_of_background = 900.0


# Threshold value (0 to 255)
# Lighter background/darker subject ==
#   high contrast == lower thval (~30-65)
# Darker background & lower contrast ==
#   higher thval (~175)
thval = 175

# Offset the person's profile and stars by
# a static number of pixels so that it appears
# in a nice place against the background sky
# (left, top)
offset = (-100,-250)

# Draw contour points
# If False, draw polylines to connnect
# contour dots
draw_dots = False

# Show the raw video in a box in the lower right
# corner of the sky background
picture_in_picture = True

#################################################
# End Settings
#################################################

# Get the frame rate
fr = cap.get(cv2.CAP_PROP_FPS)

# Not used: load a hand template so we can
# ask compareShape if the contour looks like a hand
mht = np.load('hand_template.npy')

# Background sky image
bgimg = cv2.imread('rsc-img/starry-mountains.jpg')

# Resize the bgimage
# aspect ratio
width_rsz = size_of_background
r = width_rsz / bgimg.shape[1]
dim = (int(width_rsz), int(bgimg.shape[0] * r))
 # resize
bgimg_rsz = cv2.resize(bgimg, dim, interpolation = cv2.INTER_AREA)


while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret==True:
        img = frame
        # Crop the frame
        if cropImg:
            img = img[hs:he, ws:we]
        # resize
        cam_width_rsz = size_of_constellation
        r = cam_width_rsz / img.shape[1]
        dim = (int(cam_width_rsz), int(img.shape[0] * r))
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        h,w = img.shape[:2]

        if picture_in_picture:
            # create picture-in-picture
            smallimg = img.copy()
            smallimg = cv2.resize(smallimg,(int(smallimg.shape[1]*.75),int(smallimg.shape[0]*.75)), interpolation = cv2.INTER_AREA)
            # rotate
            (w,h) = smallimg.shape[:2]
            center = ((w / 2)+((h-w)/2), h / 2)
            M = cv2.getRotationMatrix2D(center, 90, 1.0)
            smallimg = cv2.warpAffine(smallimg, M, (w,h))

        # Add a white border prior to rotate to make the image bigger so
        # it has space to rotate into
        if borderFlag:
            img_rc = cv2.copyMakeBorder(img,btop,bbot,bleft,bright,cv2.BORDER_CONSTANT,value=(255,255,255))
        else:
            img_rc = img

        if rotateImg == True:
            (w,h) = img_rc.shape[:2]
            center = ((w / 2)+((h-w)/2), h / 2)
            M = cv2.getRotationMatrix2D(center, rotangle, 1.0)
            img_rc = cv2.warpAffine(img_rc, M, (w,h))

        # Crop again (sometimes needed)
        # img_rc = img_rc[200:h, 0:w]

        # Analyze the frame
        img_analyzed, appx, thval = process_image(img_rc,mht,thval,bgimg_rsz,testmf,offset,draw_dots,picture_in_picture,smallimg)

        # Record video
        if len(appx)>num_points:
            # print(str(len(appx)))
            if recVids:
                # constellation video
                out = recordVideo(img_analyzed,out)
                # raw video
                # out = recordVideo(img,out)
        else:
            if recVids:
                stopVideo(out)

        # Display the result
        cv2.imshow('Constellation',img_analyzed)

        # press q to close the video window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()
