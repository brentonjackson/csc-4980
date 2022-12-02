#!/usr/bin/env python3

# Script to recognize and perform actions
# with smart card
# Author: Brenton Jackson
# Date: 11/28/22

# The smart card system is a way to get more
# insightful information about candidates in
# a short amount of time, while also not putting
# the burden of remembering every interaction
# on recruiters.
# It doesn't substitute face-to-face interaction,
# but it adds an additional human element to a
# candidate's resume.
#
# How it works:
# The system will be run on a stand with a camera attached.
# The primary focus of the stand will be to capture digital images
# of resumes/business cards (optional flag to switch between the two)
#
# 1. When a candidate places the card in front of the camera close enough,
# the smart action pipeline will trigger.
# 2. It will let the user know that their elevator pitch will start in 10s
# and do a countdown via a blinking LED.
# When recording begins, the LED will stay on.
# After 20s, the recording will stop, the LED will flash a few times,
# then turn off.
#
# 3. In our software, we save the picture of the card and the video
# with the same name for easy pairing.
#
# 4. (optional) Then, we upload this information into our private web app where
# a nice user interface shows all the candidates that interacted with us
# at the career fair.

# ** due to technical difficulties at the last second, we have to continue this
# without the raspberry pi **

# 1. create app that can identify and track rectangular objects within our bounding box

from math import ceil
from pathlib import Path
import cv2
import depthai as dai
import time
import argparse
import subprocess

labelMap = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

nnPathDefault = str((Path(__file__).parent / Path('../depthai-python/examples/models/mobilenet-ssd_openvino_2021.4_5shave.blob')).resolve().absolute())
parser = argparse.ArgumentParser()
parser.add_argument('nnPath', nargs='?', help="Path to mobilenet detection network blob", default=nnPathDefault)
args = parser.parse_args()


# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
spatialDetectionNetwork = pipeline.create(dai.node.MobileNetSpatialDetectionNetwork)
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
objectTracker = pipeline.create(dai.node.ObjectTracker)

xoutRgb = pipeline.create(dai.node.XLinkOut)
trackerOut = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("preview")
trackerOut.setStreamName("tracklets")

# Properties
camRgb.setPreviewSize(300, 300)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# setting node configs
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
# Align depth map to the perspective of RGB camera, on which inference is done
stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
stereo.setOutputSize(monoLeft.getResolutionWidth(), monoLeft.getResolutionHeight())

spatialDetectionNetwork.setBlobPath(args.nnPath)
spatialDetectionNetwork.setConfidenceThreshold(0.5)
spatialDetectionNetwork.input.setBlocking(False)
spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
spatialDetectionNetwork.setDepthLowerThreshold(100)
spatialDetectionNetwork.setDepthUpperThreshold(5000)


objectTracker.setDetectionLabelsToTrack([5, 15])  # track bottle or person
# possible tracking types: ZERO_TERM_COLOR_HISTOGRAM, ZERO_TERM_IMAGELESS, SHORT_TERM_IMAGELESS, SHORT_TERM_KCF
objectTracker.setTrackerType(dai.TrackerType.ZERO_TERM_COLOR_HISTOGRAM)
# take the smallest ID when new object is tracked, possible options: SMALLEST_ID, UNIQUE_ID
objectTracker.setTrackerIdAssignmentPolicy(dai.TrackerIdAssignmentPolicy.SMALLEST_ID)

# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)

camRgb.preview.link(spatialDetectionNetwork.input)
objectTracker.passthroughTrackerFrame.link(xoutRgb.input)
objectTracker.out.link(trackerOut.input)


spatialDetectionNetwork.passthrough.link(objectTracker.inputTrackerFrame)
spatialDetectionNetwork.passthrough.link(objectTracker.inputDetectionFrame)
spatialDetectionNetwork.out.link(objectTracker.inputDetections)
stereo.depth.link(spatialDetectionNetwork.inputDepth)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    preview = device.getOutputQueue("preview", 4, False)
    tracklets = device.getOutputQueue("tracklets", 4, False)

    startTime = time.monotonic()
    counter = 0
    fps = 0
    color = (255, 255, 255)

    frameNum = 0
    while(True):
        imgFrame = preview.get()
        track = tracklets.get()

        counter+=1
        current_time = time.monotonic()
        if (current_time - startTime) > 1 :
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        frame = imgFrame.getCvFrame()
        frame_orig = frame.copy()
        # make copy of frame to preserve original value without
        # object detection information overlayed
        trackletsData = track.tracklets
        for t in trackletsData:
            # print(labelMap[t.label] == "bottle")
            
            roi = t.roi.denormalize(frame.shape[1], frame.shape[0])
            x1 = int(roi.topLeft().x)
            y1 = int(roi.topLeft().y)
            x2 = int(roi.bottomRight().x)
            y2 = int(roi.bottomRight().y)

            width = abs(x2 - x1)
            height = abs(y2 - y1)
            focal_len = 457

            # if card is close enough is detected, emit green light
            if int(t.spatialCoordinates.z) < 3000 and labelMap[t.label] == "bottle":
                frameNum += 1
                print(frameNum)
                if frameNum > 30:
                    # delay to let user stabilize the camera. upper limit on fps is 30,
                    # so min delay would be 1 second after first detecting object
                    # expected delay is ~2 seconds, since avg fps is ~15-25
        
                    filename = "capture{}".format(t.id)
                    # create video, using -a flag to specify .mov file format
                    # seems I must detach from this device to be able to connect again.
                    device.close()
                    cv2.imwrite(filename + ".png", frame_orig)
                    cv2.destroyWindow("tracker") # close tracking window after capturing last frame
                    time.sleep(1)
                    ret = subprocess.run(['python3', 'record_video.py', '-n', filename], check=True)
                    if ret.returncode != 0:
                        # error
                        print(ret.returncode)
                        print('video was not captured for {}'.format(filename))
                    else:
                        print('saved video successfully')
                        print('quitting...')
                        quit()
            
            try:
                label = labelMap[t.label]
            except:
                label = t.label

            cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, f"ID: {[t.id]}", (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, t.status.name, (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

            cv2.putText(frame, f"X: {int(t.spatialCoordinates.x)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, f"Y: {int(t.spatialCoordinates.y)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, f"Z: {int(t.spatialCoordinates.z)} mm", (x1 + 10, y1 + 95), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)

            cv2.putText(frame, f"Width: {ceil(width * int(t.spatialCoordinates.z) / focal_len) } mm", (x2 - 100, y1 + 110), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, f"Height: {ceil(height * int(t.spatialCoordinates.z) / focal_len)} mm", (x2 - 100, y1 + 125), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)

        cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)

        cv2.imshow("tracker", frame)

        if cv2.waitKey(1) == ord('q'):
            break
