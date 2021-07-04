import cv2 as cv
from imutils import contours
import numpy as np
import matplotlib.pyplot as plt

# Carrega img e transforma em escala de cinza
image = cv.imread('chessboard.png')
gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

# Cria as edges e as linhas na imagem
edges = cv.Canny(gray,50,150,apertureSize = 3)
lines = cv.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)

# Cria uma nova imagem só com as linhas
isolated_lines = np.zeros(gray.shape)
for line in lines:
    x1,y1,x2,y2 = line[0]
    cv.line(isolated_lines,(x1,y1),(x2,y2),255,2)

# TODO: Extender as linhas até o final da img

invert = 255 - isolated_lines
invert = invert.astype(np.uint8)
cnts = cv.findContours(invert, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
(cnts, _) = contours.sort_contours(cnts, method="top-to-bottom")

chess_cells = []
row = []
for (i, c) in enumerate(cnts, 1):
    area = cv.contourArea(c)
    if area < 50000:
        row.append(c)
        if i % 9 == 0:  
            (cnts, _) = contours.sort_contours(row, method="left-to-right")
            chess_cells.append(cnts)
            row = []

# Iterate through each box
for row in chess_cells:
    for c in row:
        mask = np.zeros(image.shape, dtype=np.uint8)
        cv.drawContours(mask, [c], -1, (255,255,255), -1)
        result = cv.bitwise_and(image, mask)
        result[mask==0] = 255
        cv.imshow('result', result)
        cv.waitKey(175)

# plt.imshow(isolated_lines)
# plt.show()