import cv2 as cv
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

def make_line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def get_intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False

in_path = os.path.join('chessboard.png')
out_path = os.path.join('houghlines.png')

### LENDO IMAGEM E BUSCANDO LINHAS
#img = cv.imread(os.path.join(HERE, 'split board square','chessboard.png'))
img = cv.imread(in_path)
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

edges = cv.Canny(gray,50,150,apertureSize = 3)
lines = cv.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)


### SEPARANDO ENTRE LINHAS HORIZONTAIS/VERTICAIS
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


### EXTENDENDO LINHAS NA IMAGEM TODA
# Obtendo o X e Y maximos do tamanho da img
X_max, Y_max, _ = img.shape

horizontal_lines = [[0, l[1], X_max, l[3]] for l in horizontal_lines]
vertical_lines = [[l[0], 0, l[2], Y_max] for l in vertical_lines]

# Vou criar uma linha horizontal e vertical nas bordas da imagem
# Primeiro as horizontais no topo e fundo da img
# OBS: Do jeito que o cv.line (pra desenhar) funciona, a linha horizontal no pé da imagem nao vai aparecer
horizontal_lines.append([0, 0 , X_max, 0])
horizontal_lines.append([0, Y_max , X_max, Y_max])
vertical_lines.append([0, 0, 0, Y_max])
vertical_lines.append([X_max, 0, X_max, Y_max])

### SEPARANDO SOMENTE AS LINHAS DO BOARD
# Primeiro eu quero garantir q to ordenando as linhas horizontais e verticais na linha na ordem correta
# Linhas horizontais serão ordenadas da mais ao topo à mais de baixo, assim, dou sort pelo termo de index 1, que é o y1 (o index 3 (y2) daria na mesma)
horizontal_lines = sorted(horizontal_lines, key=lambda x: x[1])
# Linhas verticais dão sort pelo x
vertical_lines = sorted(vertical_lines, key=lambda x: x[0])
# Aqui eu pego só os valores de y das linhas horizontais
hline_ys = [l[1] for l in horizontal_lines]
# Aqui eu vou ter a diferença entre os y de cada linha horizontal, visto que o y vai do menor ao maior (ordenei assim), esses valores são as distancias positivas em y
# entre duas retas horizontais consecutivas
hline_gaps = np.diff(hline_ys)
# Fazendo o mesmo pras verticais
vline_xs = [l[0] for l in vertical_lines]
vline_gaps = np.diff(vline_xs)

print(hline_gaps, vline_gaps)

# TODO: Agora eu queria filtrar esses valores porém aceitando valores parecidos. E dai finalmente conferir se tem 8 gaps desses e pega as 9 linhas do board.
# TODO: Talvez seja uma boa adicionar linhas nas bordas da img


### DESENHANDO LINHAS
# Linhas horizontais em azul
for line in horizontal_lines:
    x1,y1,x2,y2 = line
    cv.line(img,(x1,y1),(x2,y2),(255, 0, 0) ,2)

# Linhas verticais em vermelho
for line in vertical_lines:
    x1,y1,x2,y2 = line
    cv.line(img,(x1,y1),(x2,y2),(0, 0, 255) ,2)


### PROCURANDO INTERSEÇÕES
intersections = []

for hline in horizontal_lines:
    for vline in vertical_lines:
        intersec = get_intersection(make_line(hline[:2], hline[2:]),
                                    make_line(vline[:2], vline[2:]))
        intersections.append(intersec)

#print(intersections)


cv.imwrite(out_path,img)