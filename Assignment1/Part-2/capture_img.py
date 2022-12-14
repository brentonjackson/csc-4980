#!/usr/bin/env python3

# Helper to capture image from depthai camera and save to disk
# Author: Brenton Jackson
# Date: 11/25/22

import cv2 as cv
import depthai as dai


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