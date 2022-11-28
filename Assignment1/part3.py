#!/usr/bin/env python3

# Script to show RGB stream and depth map stream
# from camera simultaneously
# Author: Brenton Jackson
# Date: 11/28/22

import cv2
import depthai as dai
import numpy as np


outRectified = False  # Output and display rectified streams
lrcheck = False  # Better handling for occlusions
extended = False  # Closer-in minimum depth, disparity range is doubled
subpixel = False  # Better accuracy for longer distance, fractional disparity 32-levels
depth = False  # Display depth frames
res = dai.MonoCameraProperties.SensorResolution.THE_720_P
median = dai.StereoDepthProperties.MedianFilter.KERNEL_7x7

def getDisparityFrame(frame):
    maxDisp = stereo.initialConfig.getMaxDisparity()
    disp = (frame * (255.0 / maxDisp)).astype(np.uint8)
    disp = cv2.applyColorMap(disp, cv2.COLORMAP_JET)

    return disp

# Create pipeline with RGB and stereo depth
pipeline = dai.Pipeline()

# Define source and output for RGB
camRgb = pipeline.create(dai.node.ColorCamera)
xoutVideo = pipeline.create(dai.node.XLinkOut)
xoutVideo.setStreamName("video")

# Define source and outputs for stereo depth
camLeft = pipeline.create(dai.node.MonoCamera)
camRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
xoutLeft = pipeline.create(dai.node.XLinkOut)
xoutRight = pipeline.create(dai.node.XLinkOut)
xoutDisparity = pipeline.create(dai.node.XLinkOut)


# RGB Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setVideoSize(1920, 1080)

xoutVideo.input.setBlocking(False)
xoutVideo.input.setQueueSize(1)

# Stereo Depth Properties
camLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
camRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
for monoCam in (camLeft, camRight):  # Common config
    monoCam.setResolution(res)

stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
stereo.initialConfig.setMedianFilter(median)  # KERNEL_7x7 default
stereo.setRectifyEdgeFillColor(0)  # Black, to better see the cutout
stereo.setLeftRightCheck(lrcheck)
stereo.setExtendedDisparity(extended)
stereo.setSubpixel(subpixel)

xoutLeft.setStreamName("left")
xoutRight.setStreamName("right")
xoutDisparity.setStreamName("disparity")


# Linking
camRgb.video.link(xoutVideo.input)


camLeft.out.link(stereo.left)
camRight.out.link(stereo.right)
stereo.syncedLeft.link(xoutLeft.input)
stereo.syncedRight.link(xoutRight.input)
stereo.disparity.link(xoutDisparity.input)


streams = ["left", "right"]
streams.append("disparity")









# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # queue for RGB
    video = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    
    # queues for stereo depth streams
    qList = [device.getOutputQueue(stream, 8, blocking=False) for stream in streams]
    
    while True:
        # show RGB video
        videoIn = video.get()
        # Get BGR frame from NV12 encoded video frame to show with opencv
        # Visualizing the frame on slower hosts might have overhead
        cv2.imshow("video", videoIn.getCvFrame())
        if cv2.waitKey(1) == ord('q'):
            break
        
        
        
        # show depth stream video
        for q in qList:
            name = q.getName()
            frame = q.get().getCvFrame()
            if name == "depth":
                frame = frame.astype(np.uint16)
            elif name == "disparity":
                frame = getDisparityFrame(frame)

            cv2.imshow(name, frame)
        if cv2.waitKey(1) == ord("q"):
            break


        

        