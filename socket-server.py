import numpy as np
import cv2
from autostellargraphy import process_image

import socket
import sys
from thread import *

thval = 175

HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces
PORT = 5205 # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# Threshold value (0 to 255)
# Lighter background/darker subject ==
#   high contrast == lower thval (~30-65)
# Darker background & lower contrast ==
#   higher thval (~175)

# Background sky image
bgimg = cv2.imread('rsc-img/starry-mountains.jpg')

# Video source
# Webcam:
# cap = cv2.VideoCapture(0)
# File:
cap = cv2.VideoCapture('rsc-vid/vid1.mp4')

w = cap.get(cv2.CAP_PROP_FRAME_WIDTH);
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT);
fr = cap.get(cv2.CAP_PROP_FPS);

mht = np.load('hand_template.npy')

# Define the codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# out = cv2.VideoWriter('output/output.mp4',fourcc, fr, (int(w),int(h)))
# (We rotate the movie 90 degrees below so swap w and h)
# out = cv2.VideoWriter('output/output.mp4',fourcc, fr, (480,640))

appx = None

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

#Start listening on socket
s.listen(10)
print 'Socket now listening'


#Function for handling connections. This will be used to create threads
def client(conn):
    # conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Our operations on the frame come here
        if ret==True:
            # Analyze the frame
            img_analyzed,appx,x = process_image(frame,mht,thval,bgimg,False,(0,0),False,False,None)

            # write the frame to a file
            # out.write(img_analyzed)
            # Display the resulting frame
            cv2.imshow('Image Analysis',img_analyzed)
            # press q to close the video window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                break
        else:
            break

        #Receiving from client
        # data = conn.recv(1024)
        # reply = 'OK...' + data
        # if not data:
        #     break
        # conn.sendall(reply)
        fd = "";
        # print(appx);
        if(appx != "404" and len(appx)>0):
            # appx_sorted = appx[0][np.argsort(appx[0][:,1])];
            for x in appx:
                for y in x:
                    fd = fd + (str(y[0])+","+str(y[1]))+":";
            fd = fd[:-1]
            conn.sendall(fd)

    #came out of loop
    conn.close()


while 1:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cap.isOpened():
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        client(conn)
        # start_new_thread(clientthread2,(conn,))
s.close()
# s.shutdown(socket.SHUT_RDWR)

# Release everything if job is finished
cap.release()
#out.release()
cv2.destroyAllWindows()
