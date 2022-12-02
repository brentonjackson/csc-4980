#!/usr/bin/env python3

# Script to record video for
# specified amount of time
# Author: Brenton Jackson
# Date: 12/1/22

import argparse
import cv2
import time
import depthai as dai

# Create pipeline
pipeline = dai.Pipeline()

# Define source and output
camRgb = pipeline.create(dai.node.ColorCamera)
xoutVideo = pipeline.create(dai.node.XLinkOut)

xoutVideo.setStreamName("video")

# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setVideoSize(1920, 1080)

xoutVideo.input.setBlocking(False)
xoutVideo.input.setQueueSize(1)

# Linking
camRgb.video.link(xoutVideo.input)

default_duration = 5
parser = argparse.ArgumentParser()
parser.add_argument('duration', nargs='?', help="Video length in seconds", default=default_duration)
parser.add_argument('-n', '--videoName', nargs='?', help="Name of file to write to disk")
parser.add_argument('-a', '--apple', action="store_true", help="If on Apple device (mac), change video format to .mov", default=False)
args = parser.parse_args()


duration = int(args.duration)
filename = args.videoName + '.mov' if args.apple else args.videoName + '.mp4'

# cap = cv2.VideoCapture(1)
# Define the codec and create VideooWriter object
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') if args.apple else cv2.VideoWriter_fourcc('M','J','P','G')
# frame_width = int(cap.get(3))
# frame_height = int(cap.get(4))
out = cv2.VideoWriter(filename, fourcc, 20.0, (1920, 1080))
# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    video = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    startTime = time.monotonic()
    while True:
        videoIn = video.get()
        vidFrame = videoIn.getCvFrame()
        # Get BGR frame from NV12 encoded video frame to show with opencv
        # Visualizing the frame on slower hosts might have overhead
        
        # write the frame
        out.write(vidFrame)
        cv2.imshow('frame', vidFrame)
        currTime = time.monotonic()
        elapsedTime = currTime - startTime
        if elapsedTime > duration + 1 or cv2.waitKey(1) == ord('q'):
            break

    out.release()