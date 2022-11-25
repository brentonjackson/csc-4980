#!/usr/bin/env python3

# Script to find real world dimensions of an object from image
# Author: Brenton Jackson
# Date: 11/25/22

# parameters needed (inputs):
# canvas position Cx
# canvas position Cy
# canvas height (image ht) Ch
# canvas width (image width) Cw
# viewport width (real-world) Vw
# viewport height (real-world) Vh
# viewport distance (real-world) from camera d


# desired output:
# viewport coordinates corresponding to canvas position
# viewport position Vx
# viewport position Vy
# viewport position Vz = d

import numpy as np
import cv2 as cv
import depthai as dai


# 1. capture image of object with camera
# Create pipeline
pipeline = dai.Pipeline()

# Define source and output
camRgb = pipeline.create(dai.node.ColorCamera)
xoutRgb = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("rgb")

# Properties
camRgb.setPreviewSize(400, 400)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

# Linking
camRgb.preview.link(xoutRgb.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived

        # Retrieve 'bgr' (opencv format) frame
        frame = inRgb.getCvFrame()
        cv.imshow("rgb", frame)
        
        k = cv.waitKey(1)
        if k%256 == 32:
            # SPACE pressed, save image
            img_name = "opencv_frame1.png"
            cv.imwrite(img_name, frame)
            print("{} written!".format(img_name))

        if k == ord('q'):
            break


cv.destroyAllWindows()