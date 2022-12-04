import cv2

aruco = cv2.aruco

def computeDisparity(img, markerSize =4, totalMarkers=50, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    bboxs, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
    return (bboxs)

img0 = cv2.imread('frame1.png')
img1 = cv2.imread('frame2.png')

baseline = 11.5
focal_length = 1.636331765375964e+03
bbox1= computeDisparity(img0)
bbox2 = computeDisparity(img1)

d = (baseline * focal_length)/(bbox1[0][0][3][0]-bbox2[0][0][3][0])
print('Disparity: ', d)
