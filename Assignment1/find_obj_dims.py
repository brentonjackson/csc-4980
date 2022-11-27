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

import argparse
import subprocess
from dist_between_pts import get_dims_2D
from calibrate_camera import newcameramtx as camera_matrix # import calculated intrinsic and extrinsic parameters of camera

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False, help="Path to the image")
ap.add_argument("-d", "--distance", required=False, help="Distance of object from camera")
args = vars(ap.parse_args())

# 1. Grab image with object in it
# if no image argument specified, capture new image
if (not args["image"]) :
    subprocess.run(['python3', 'capture_img.py'])
imgName = args["image"] or "opencv_frame1.png"
dist = args["distance"] or 15 # distance from camera in inches


# 2. Find height of object (in image) by allowing user to select two points on image
dist_image = get_dims_2D(imgName=imgName)


# 3. Use perspective projection equations to convert our desired dimension to 3D, real world values and units
# equation: real_dist = dist_image * dist_from_camera / focal_len
focal_len = (camera_matrix[0][0] + camera_matrix[1][1]) / 2 # avg of fx and fy
real_dist = dist_image * dist / focal_len

print("real world distance: ", real_dist, '(in dist units)')