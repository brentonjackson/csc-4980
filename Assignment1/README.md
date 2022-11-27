# Assignment 1

## Submission in Classroom:

**_Submission: [Here](https://github.com/brentonjackson/csc-4980/blob/master/Assignment1/Assignment%201.ipynb)_**

**_Demo:_**

![Link](./part2_demo.gif)

Camera images of paper worksheets will NOT be accepted

- **Python:** submit a jupyter notebook and the .py files associated

- Manage all your code in a github repo for each assignment.

- Provide a link to the repo in the documentation workspace
  (jupyter notebook or mlx file).

- Create a working demonstration of your application and record a screen-recording or a properly captured footage of the working system.
- Upload the video in the Google classroom submission.

**Hardware**: Unless otherwise specified, CAMERA refers to the OAK-D Lite camera provided to you.

**Software**:
For OAK-D you can implement your solutions in either Python or
C/C++: https://docs.luxonis.com/en/latest/

## PART A: Fundamentals

Python:

1. Go over the camera calibration toolbox demonstration and calibrate the OAK-D camera https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

## PART B: MATLAB/Python Prototyping

2. Write a MATLAB/Python script to find the real world dimensions (e.g. diameter of a ball, side length of a cube) of an object using perspective projection equations. Validate using an experiment where you image an object using your camera from a specific distance (choose any distance but ensure you are able to measure it accurately) between the object and camera.

## PART C: Application development

Familiarize with the Depth AI SDK. Run the tutorials/examples:
https://docs.luxonis.com/projects/sdk/en/latest/ (need not submit this)

3. Setup your application to show a RGB stream from the mono camera and a depth map stream from the stereo camera simultaneously. Is it feasible? What is the maximum frame rate and resolution achievable?

4. Run the camera calibration tutorial. Compare the output with answers from Part A calibration results.
