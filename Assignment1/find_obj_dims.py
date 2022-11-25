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

import cv2 as cv
import depthai as dai
import argparse
import subprocess

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False, help="Path to the image")
args = vars(ap.parse_args())

# 1. Grab image with object in it
print(args)
# if no image argument specified, capture new image
if (not args["image"]) :
    subprocess.run(['python3', 'capture_img.py'])

imgName = args["image"] or "opencv_frame1.png"


# 2. Find height of object (in image) by allowing user to select two points on image

# load the image, clone it, and setup the mouse callback function
image = cv.imread(imgName)
clone = image.copy()
cv.namedWindow("image")
# cv.setMouseCallback("image", capture_height)

cv.imshow("object img", image)

# process two click events by clicking and using spacebar to accept click
k = cv.waitKey(0)
