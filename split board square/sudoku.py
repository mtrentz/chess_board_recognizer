import cv2 as cv
from imutils import contours
import numpy as np
import matplotlib.pyplot as plt

# Load image, grayscale, and adaptive threshold
image = cv.imread('chessboard.png')
gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
thresh = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,57,5)

# Filter out all numbers and noise to isolate only boxes
cnts = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    area = cv.contourArea(c)
    if area < 1000:
        cv.drawContours(thresh, [c], -1, (0,0,0), -1)

# Fix horizontal and vertical lines
vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1,5))
thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, vertical_kernel, iterations=9)
horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,1))
thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, horizontal_kernel, iterations=4)

# Sort by top to bottom and each row by left to right
invert = 255 - thresh
print(type(invert))
cnts = cv.findContours(invert, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
(cnts, _) = contours.sort_contours(cnts, method="top-to-bottom")

sudoku_rows = []
row = []
for (i, c) in enumerate(cnts, 1):
    area = cv.contourArea(c)
    if area < 50000:
        row.append(c)
        if i % 9 == 0:  
            (cnts, _) = contours.sort_contours(row, method="left-to-right")
            sudoku_rows.append(cnts)
            row = []

# # Iterate through each box
# for row in sudoku_rows:
#     for c in row:
#         mask = np.zeros(image.shape, dtype=np.uint8)
#         cv.drawContours(mask, [c], -1, (255,255,255), -1)
#         result = cv.bitwise_and(image, mask)
#         result[mask==0] = 255
#         cv.imshow('result', result)
#         cv.waitKey(175)

# cv.imshow('thresh', thresh)
# cv.imshow('invert', invert)
# cv.waitKey()