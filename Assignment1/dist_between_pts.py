#!/usr/bin/env python3

# Click two points on an image and calculate Euclidean distance
# Author: Brenton Jackson
# Date: 11/27/22

from math import sqrt
import cv2


#define global variables for mouse callback function capture_pts
clickOne = False
clickTwo = False
imgPts = []
clone = []
image = []
circleRadius = 3
circleColor = (0, 255, 0) # green
lineThickness = 4
lineColor = (0, 0, 255) # red




def capture_pts(event, x, y, flags, param):
    """ 
    Callback function that allows user to click two points in image to calculate distance

    @param event The event that took place (left mouse button pressed, left mouse button released, mouse movement, etc)
    @param x The x-coordinate of the event
    @param y The y-coordinate of the event
    @param flags Any relevant flags passed by OpenCV
    @param param Any extra parameters supplied by OpenCV

    return No return value. Modifies global imgPts array
    """

    # grab references to the global variables
    global clickOne, clickTwo, imgPts, clone, image
 
    

	# if the left mouse button was clicked, record the 
	# (x, y) coordinates and indicate that first click is
	# being captured
    if event == cv2.EVENT_LBUTTONUP and clickOne == True:
        imgPts = [(x, y)]
        # draw circle around the region of interest
        cv2.circle(clone, (x, y), circleRadius, circleColor, -1)
        cv2.imshow("image", clone)

        k = cv2.waitKey(0)
        
        # reset points if r is pressed
        if k == ord("r"):
            refresh_image()

        if k%256 == 32:
            # SPACE pressed, break out
            clickOne = False
            clickTwo = True
            print("click second coordinate")
    
    # if the left mouse button was clicked, record the 
	# (x, y) coordinates of the second point and indicate 
    # that the operation is complete
    if event == cv2.EVENT_LBUTTONUP and clickTwo == True:
        # draw circle around the region of interest
        cv2.circle(clone, (x, y), circleRadius, circleColor, -1)
        cv2.imshow("image", clone)

        k = cv2.waitKey(0)
        
        # reset points if r is pressed
        if k == ord("r"):
            refresh_image()

        if k%256 == 32:
            # SPACE pressed, break out
            clickTwo = False
            imgPts.append((x, y))
            print(imgPts)
            print("captured both coordinates")

def refresh_image():
    """ 
    Function that resets the image so it's clear of points
    and resets the array of image points

    return No return value. Modifies global imgPts array,
    clickOne flag, clickTwo flag, and clone image variable
    """
    global imgPts, clickOne, clickTwo, clone, image
    clone = image.copy()
    imgPts = []
    clickOne = True
    clickTwo = False

def calculate_dist(points):
    """
    Function that takes two (x,y) coordinates and calculates
    the euclidean distance between them

    @param points An array containing two tuples
    """
    (x1, y1) = points[0]
    (x2, y2) = points[1]
    return round(sqrt((x1-x2)**2 + (y1-y2)**2))

def get_dims_2D(imgName):
    """
    Function to get allow user to get distance between
    two points on object in an image

    @return Distance between points in pixels

    @param imgName Name of desired image with object

    Instructions:

    Click a point on image, then press SPACE to confirm point.
    
    To refresh the image, press 'R'

    After confirming two points, press 'C' to continue and a
    line connecting the points will be drawn in addition to
    the distance being calculated.

    Press 'Q' to close image windows when done.
    
    """

    global imgPts, clickOne, clickTwo, clone, image

    # load the image, clone it, and setup the mouse callback function
    image = cv2.imread(imgName)
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", capture_pts)
    
    # loop until we've confirmed our two points
    clickOne = True
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", clone)
        key = cv2.waitKey(1)
        
        # if the 'r' key is pressed, reset the points
        if key == ord("r"):
            refresh_image()
        # if the 'c' key is pressed, break from the loop
        elif key == ord("c"):
            break
        elif len(imgPts) >= 2:
            break    
    
    # if there are two reference points, then draw the line
    # between the points on the image clone
    dist = 0
    if len(imgPts) == 2:
        while True:
            cv2.line(clone, imgPts[0], imgPts[1], lineColor, lineThickness)
            cv2.imshow("Distance", clone)
            k = cv2.waitKey(1)
            if k == ord('q'):
                break
        dist = calculate_dist([imgPts[0], imgPts[1]])
    

    print("dist: ", dist, "px")
    return dist