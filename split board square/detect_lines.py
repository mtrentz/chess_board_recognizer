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

# Vou pegar o valor mais popular dos gaps horizontais. Preciso tirar do numpy pra funcionar o count
h_mode = max(set(hline_gaps), key=list(hline_gaps).count)
v_mode = max(set(vline_gaps), key=list(vline_gaps).count)

# O objetivo aqui agora é achar os 'indexes' onde esses valores mais populares acontecem, e garantir q eles são consecutivos
hline_indexes = np.argwhere(hline_gaps == h_mode).flatten()
vline_indexes = np.argwhere(vline_gaps == v_mode).flatten()

# Definindo uma função (aqui msm pra ficar organizado) que testa se os valores são consecutivos
is_consecutive = lambda ls: sorted(ls) == list(range(min(ls), max(ls) + 1))

# Caso a lista não seja consecutiva ou não tenha 8 gaps (ou seja, entre as 9 linhas do board)
if not is_consecutive(hline_indexes) or len(hline_indexes) < 8:
    print("Não foi possível detectar o board")
    quit()

if not is_consecutive(vline_indexes) or len(vline_indexes) < 8:
    print("Não foi possível detectar o board")
    quit()

# Agora vou filtrar as linhas horizontais/verticais 
# Primeiro nos indexes, se eu achei o index 1 isso significa que as linhas q criam aquele gap, são a de index 1 e 2 da lista.
# Ou seja, preciso pegar todos os mesmos indexes e um a mais no final
hline_indexes = np.append(hline_indexes, [hline_indexes[-1] + 1])
vline_indexes = np.append(vline_indexes, [vline_indexes[-1] + 1])

board_horizontal_lines = np.array(horizontal_lines)
board_horizontal_lines = board_horizontal_lines[hline_indexes]
board_vertical_lines = np.array(vertical_lines)
board_vertical_lines = board_vertical_lines[vline_indexes]


### DESENHANDO LINHAS (Somente as do board)
# Linhas horizontais em azul
for line in board_horizontal_lines:
    x1,y1,x2,y2 = line
    cv.line(img,(x1,y1),(x2,y2),(255, 0, 0) ,2)

# Linhas verticais em vermelho
for line in board_vertical_lines:
    x1,y1,x2,y2 = line
    cv.line(img,(x1,y1),(x2,y2),(0, 0, 255) ,2)


### PROCURANDO INTERSEÇÕES
intersections = []
# TODO: Traduzir os pontos pra uma matriz interpretavel

for hline in board_horizontal_lines:
    for vline in board_vertical_lines:
        intersec = get_intersection(make_line(hline[:2], hline[2:]),
                                    make_line(vline[:2], vline[2:]))
        intersections.append(intersec)

intersections.sort()

board_points = np.array([
    [intersections[i] for i in range(0,9)],
    [intersections[i] for i in range(9,18)],
    [intersections[i] for i in range(18,27)],
    [intersections[i] for i in range(27,36)],
    [intersections[i] for i in range(36,45)],
    [intersections[i] for i in range(45,54)],
    [intersections[i] for i in range(54,63)],
    [intersections[i] for i in range(63,72)],
    [intersections[i] for i in range(72,81)],
])

# Os quadrados do board são definido pelo (x1, y1) e (x2, y2) do topo esquerda e baixo direita
board_squares = np.array([
    [(board_points[0][i], board_points[1][i+1])  for i in range(0,8)],
    [(board_points[1][i], board_points[2][i+1])  for i in range(0,8)],
    [(board_points[2][i], board_points[3][i+1])  for i in range(0,8)],
    [(board_points[3][i], board_points[4][i+1])  for i in range(0,8)],
    [(board_points[4][i], board_points[5][i+1])  for i in range(0,8)],
    [(board_points[5][i], board_points[6][i+1])  for i in range(0,8)],
    [(board_points[6][i], board_points[7][i+1])  for i in range(0,8)],
    [(board_points[7][i], board_points[8][i+1])  for i in range(0,8)],
])
board_squares = board_squares.astype(int)

#cv.rectangle(img=img, pt1=tuple(board_squares[0][0][0]), pt2=tuple(board_squares[0][0][1]), color=(0,0,0), thickness=5)
for col in board_squares:
    for row in col:
        crop = img[row[0][1]:row[1][1], row[0][0]:row[1][0]]
        cv.imshow('crop', crop)
        cv.waitKey(300)


# board_points = [
#     [i for i ]
# ]

#cv.imwrite(out_path,img)