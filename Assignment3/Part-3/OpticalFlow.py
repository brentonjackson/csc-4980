import cv2 as cv
import numpy as np


feature_params = dict(maxCorners = 300, qualityLevel = 0.2, minDistance = 2, blockSize = 7)

lk_params = dict(winSize = (15,15), maxLevel = 2, criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))
cap = cv.VideoCapture("shibuya.mp4")
# cap = cv.VideoCapture("output.mp4")

color = (0, 255, 0)
red = (255,0,0)

ret, first_frame = cap.read()
# Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)

prev = cv.goodFeaturesToTrack(prev_gray, mask = None, **feature_params)

mask = np.zeros_like(first_frame)

while(cap.isOpened()):

    ret, frame = cap.read()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    prev = cv.goodFeaturesToTrack(prev_gray, mask = None, **feature_params)
    next, status, error = cv.calcOpticalFlowPyrLK(prev_gray, gray, prev, None, **lk_params)

    good_old = prev[status == 1].astype(int)

    good_new = next[status == 1].astype(int)

    for i, (new, old) in enumerate(zip(good_new, good_old)):

        a, b = new.ravel()

        c, d = old.ravel()

        mask = cv.line(mask, (a, b), (c, d), color, 2)

        frame = cv.circle(frame, (a, b), 3, red, -1)

    output = cv.add(frame, mask)

    prev_gray = gray.copy()

    prev = good_new.reshape(-1, 1, 2)

    cv.imshow("sparse optical flow", output)

    if cv.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()