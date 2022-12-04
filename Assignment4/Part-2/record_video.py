#!/usr/bin/env python3

# Script to record video for
# specified amount of time
# Author: Brenton Jackson
# Date: 12/1/22

import argparse
import cv2
import time
import depthai as dai
from RGBPipeline import RGBPipeline
import threading
import subprocess
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
import os

# parse command line arguments
default_duration = 5
parser = argparse.ArgumentParser()
parser.add_argument('duration', nargs='?', help="Video length in seconds", default=default_duration)
parser.add_argument('-n', '--filename', nargs='?', help="Name of file to write to disk", default='test')
parser.add_argument('-a', '--apple', action="store_true", help="If on Apple device (mac), change video codec", default=False)
args = parser.parse_args()

# global variables
duration = int(args.duration)
recording = None
video_filename = ""
startTime = 0
elapsedTime = 0
frameCount = 0
expectedFps = 11.7 # may need to be fine-tuned for your computer, look at stdout for ***video fps***

def record_vid():
    global recording, video_filename, startTime, elapsedTime, frameCount, expectedFps
    rgb_pipeline = RGBPipeline()
    video_filename = args.filename + '.mp4'

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') if args.apple else cv2.VideoWriter_fourcc('M','J','P','G')
    out = cv2.VideoWriter(video_filename, fourcc, expectedFps, (1920, 1080))

    # Connect to device and start pipeline
    with dai.Device(rgb_pipeline.getPipeline()) as device:

        video = device.getOutputQueue(rgb_pipeline.getStreamName(), maxSize=1, blocking=False)
        startTime = time.monotonic()
        print('recording video frames')
        while recording == True or elapsedTime < duration:
            videoIn = video.get()
            vidFrame = videoIn.getCvFrame()
            frameCount += 1
            # Get BGR frame from NV12 encoded video frame to show with opencv
            # Visualizing the frame on slower hosts might have overhead
            
            # write the frame
            out.write(vidFrame)
            # cv2.imshow('frame', vidFrame)
            currTime = time.monotonic()
            elapsedTime = currTime - startTime
        print('video recording done')
        recording = False
        out.release()

def record_audio():
    global recording
    rate = 44100
    channels = 1
    audio_filename = args.filename + '.wav'
    # start stream, at the same time as video starts
    recording = True
    time.sleep(2) # delay to wait for video to start recording
    print('recording audio')
    myrecording = sd.rec(int(duration * rate), samplerate=rate, channels=channels)
    sd.wait()  # Wait until recording is finished
    recording = False
    print('audio recording done')
    write(audio_filename, rate, myrecording)  # Save as WAV file 
    
def start_AVrecording():
    # play 3 beeps
    data, fs = sf.read('beep.wav')
    for i in range(0, 2):
        sd.play(data, fs)
        sd.wait()
        time.sleep(0.9)
    sd.play(data, fs)
    # sd.wait()
    
    print('****  recording starting in 1s  ****')
    threading.Thread(target=record_vid).start()
    threading.Thread(target=record_audio).start()

def file_manager(filename=args.filename):
    # Processing of final files
    print('processing files')
    local_path = os.getcwd()
    # if os.path.exists(str(local_path) + "/" + filename + ".wav"):
    #     os.remove(str(local_path) + "/" + filename + ".wav")

    if os.path.exists(str(local_path) + "/" + filename + "2.mp4"):
        os.remove(str(local_path) + "/" + filename + "2.mp4")

    if os.path.exists(str(local_path) + "/" + filename + "_AV.mp4"):
        os.remove(str(local_path) + "/" + filename + "_AV.mp4")
    print('file processing complete')

def merge_files():
    # merge two files after they're done
    global video_filename, elapsedTime, frameCount, expectedFps
    recordedFps = frameCount/elapsedTime
    print('merging audio and video files')
    print("*********   video fps: " + str(recordedFps) + "   ***********")
    print("fps difference: " + str(abs(recordedFps - expectedFps)))
    if abs(recordedFps - expectedFps) >= 0.01:  # If the fps rate was higher/lower than expected, re-encode it to the expected
        print("Re-encoding")
        tempFilename = args.filename + "2.mp4"
        cmd = "ffmpeg -r " + str(recordedFps) + " -i " + video_filename + " -r " + str(expectedFps) + " -b:v 6000k -vcodec mpeg4 " + tempFilename
        subprocess.call(cmd, shell=True)

        print("Muxing")
        cmd = "ffmpeg -ac 1 -channel_layout stereo -i " + args.filename + ".wav -i " + tempFilename + " -b:v 6000k -vcodec mpeg4 " + args.filename + "_AV.mp4"
        retcode = subprocess.call(cmd, shell=True)

    else:
        print("Muxing")
        cmd = "ffmpeg -ac 1 -channel_layout stereo -i " + args.filename + ".wav -i " + video_filename + " -b:v 6000k -vcodec mpeg4 " + args.filename + "_AV.mp4"
        retcode = subprocess.call(cmd, shell=True)
    
    if not retcode:
        print("done merging the files")
    else:
        print("video and audio merge failed")


if __name__ == '__main__':
    # main control flow
    start_AVrecording()
    time.sleep(duration + 5) # 5s buffer to make sure everything is done
    file_manager()
    time.sleep(5) # time for os to handle files
    merge_files()

    
