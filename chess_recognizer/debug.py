import os
import cv2 as cv
from PIL import Image
import numpy as np


HERE = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
im = Image.open(os.path.join(HERE, 'chessboard_3.png'))

img = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

X_max, Y_max, _ = img.shape

##### EDGES #####
edges = cv.Canny(gray, 50, 150, apertureSize = 5)
# edges = cv.Canny(self.img,50,150,apertureSize = 3)

##### LINES #####
min_length = round(min(img.shape[0], img.shape[1])*0.08)
max_gap = round(min(img.shape[0], img.shape[1])*0.01)
lines = cv.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=min_length, maxLineGap=max_gap)

### horizontal/vertical
# Quantos graus a linha pode desviar de completamente reta para ser considerada horizontal/vertical
acceptable_angle_dev = 5

# Vou separar as linhas em horizontais e verticais
horizontal_lines = []
vertical_lines = []

for line in lines:
    x1,y1,x2,y2 = line[0]

    # Do jeito que ta colocado aqui, se for perfeitamente horizontal o angulo vai ser zero e vertical o angulo será -90
    horizontal_angle = 0
    vertical_angle = -90

    # Calcula angulo da linha
    angle = np.rad2deg(np.arctan2(y2 - y1, x2 - x1))

    if (horizontal_angle - acceptable_angle_dev) <= angle <= (horizontal_angle + acceptable_angle_dev):
        horizontal_lines.append([x1,y1,x2,y2])
    elif (vertical_angle - acceptable_angle_dev) <= angle <= (vertical_angle + acceptable_angle_dev):
        vertical_lines.append([x1,y1,x2,y2])

### extend
extended_horizontal_lines = [[0, l[1], X_max, l[3]] for l in horizontal_lines]
extended_vertical_lines = [[l[0], 0, l[2], Y_max] for l in vertical_lines]

# Vou criar uma linha horizontal e vertical nas bordas da imagem
# Primeiro as horizontais no topo e fundo da img
extended_horizontal_lines.append([0, 0 , X_max, 0])
extended_horizontal_lines.append([0, Y_max , X_max, Y_max])
extended_vertical_lines.append([0, 0, 0, Y_max])
extended_vertical_lines.append([X_max, 0, X_max, Y_max])

### remove duplicadas
extended_horizontal_lines = np.unique(np.array(extended_horizontal_lines), axis=0).tolist()
extended_vertical_lines = np.unique(np.array(extended_vertical_lines), axis=0).tolist()

# TODO: Tem duas coisas pra fazer aqui
# 1: considerar como "duplicada" todas as linhas com uma tolerancia
# 2: Pegar aqueles gaps lá entre as linhas. Aqui sei q precisa tolerancia
# Ver dai se da pra nao fazer o passo 1

# ##### CORNERS ######
# corner_src = img.copy()
# dst = cv.cornerHarris(edges, 3, 5, 0.04)
# #result is dilated for marking the corners, not important
# dst = cv.dilate(dst,None)



##### DRAW #####
edge_rgb = cv.cvtColor(gray, cv.COLOR_GRAY2RGB)

# for line in lines:
#     x1,y1,x2,y2 = line[0]
#     cv.line(img,(x1,y1),(x2,y2),(0, 0, 255) ,2)
#     cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 0, 255) ,2)


# for v in vertical_lines:
#     x1,y1,x2,y2 = v
#     cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 255, 0) ,2)

# for h in horizontal_lines:
#     x1,y1,x2,y2 = h
#     cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 0, 255) ,2)

for v in extended_horizontal_lines:
    x1,y1,x2,y2 = v
    cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 255, 0) ,2)

for h in extended_vertical_lines:
    x1,y1,x2,y2 = h
    cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 0, 255) ,2)



# # Threshold for an optimal value, it may vary depending on the image.
# corner_src[dst>0.01*dst.max()]=[0,0,255]
# cv.imshow('corners',corner_src)
# cv.waitKey(0)

cv.imshow('edges_lined', edge_rgb)
cv.waitKey(0)

# cv.imshow('edges', edges)
# cv.waitKey(0)