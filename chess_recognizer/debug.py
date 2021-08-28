import os
import cv2 as cv
from PIL import Image
import numpy as np
from itertools import combinations
from collections import Counter
import matplotlib.pyplot as plt


def h_line_gap(l1, l2):
    # Aqui se eu tenho duas linhas horizontais, eu vou ver o gap VERTICAL delas,
    # ou seja, o gap em Y
    delta_y1 = abs(l1[1] - l2[1])
    # Faz o mesmo pro y2
    delta_y2 = abs(l1[3] - l2[3])
    # Retorna a média dos dois
    return (delta_y1 + delta_y2)/2


def v_line_gap(l1, l2):
    # Aqui se eu tenho duas linhas verticais, eu vou ver o gap horizontal delas,
    # ou seja, o gap em X
    delta_x1 = abs(l1[0] - l2[0])
    delta_x2 = abs(l1[2] - l2[2])
    return (delta_x1 + delta_x2)/2


HERE = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
im = Image.open(os.path.join(HERE, 'chessboard_4.png'))

img = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

Y_max, X_max, _ = img.shape
print('X max: ', X_max)
print('Y max: ', Y_max)

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

### remove duplicadas
extended_horizontal_lines = np.unique(np.array(extended_horizontal_lines), axis=0).tolist()
extended_vertical_lines = np.unique(np.array(extended_vertical_lines), axis=0).tolist()

print("Extended Horizontal Lines:\n",  extended_horizontal_lines)
print("Extended Vertical Lines:\n", extended_vertical_lines)


### Vendo os gaps entre as linhas
# Começo pegando os indexes (quantidade) de linhas horizontais e verticais
h_line_indexes = [i for i in range(len(extended_horizontal_lines))]
v_line_indexes = [i for i in range(len(extended_vertical_lines))]
# Agora eu pego a combinação entre os indexes, que vou medir os gaps
h_line_combinations = list(combinations(h_line_indexes, 2))
v_line_combinations = list(combinations(v_line_indexes, 2))
# Em cada combinação eu calculo o gap entre as linhas e salvo como (l1_index, l2_index, l1l2_gap)
h_gaps = []
v_gaps = []

for h_comb in h_line_combinations:
    # h_comb[0] é o index de uma linha, h_comb[1] é o index de outra
    l1_index = h_comb[0]
    l2_index = h_comb[1]
    # Pego l1 e l2 em si
    l1 = extended_horizontal_lines[l1_index]
    l2 = extended_horizontal_lines[l2_index]
    # Calculo o gap entre elas
    hgap = h_line_gap(l1, l2)
    # Guardo os index e o gap entre elas
    h_gaps.append((l1_index, l2_index, hgap))

for v_comb in v_line_combinations:
    l1_index = v_comb[0]
    l2_index = v_comb[1]
    l1 = extended_vertical_lines[l1_index]
    l2 = extended_vertical_lines[l2_index]
    vgap = v_line_gap(l1, l2)
    v_gaps.append((l1_index, l2_index, vgap))

### Tendo os gaps, quero achar as linhas que separam as células
# Se a imagem fosse o board com nada de espaço nas bordas
# cada célular ocuparia 1/8 da largura/altura da imagem
# Assim, assumindo que as bordas não sejam muito grande,
# vou assumir 1/7 da largura/altura como o maior gap possível
# Lembrando que o gap entre duas linhas horizontais é o Y
max_allowed_hline_gap = round(Y_max/7)
max_allowed_vline_gap = round(X_max/7)
# O menor gap vou assumir como 1/12 das dimensoes
# caso contrario é pq o board foi muito mal focado na foto
min_allowed_hline_gap = round(Y_max/12)
min_allowed_vline_gap = round(X_max/12)

print("Max Allowed H Gap: ", max_allowed_hline_gap)
print("Max Allowed V Gap: ", max_allowed_vline_gap)
print("Min Allowed H Gap: ", min_allowed_hline_gap)
print("Min Allowed V Gap: ", min_allowed_vline_gap)


# Pros gaps horizontal e vertical eu vou descobrir as frequencias dos gaps
# aqui o g[2] é o valor do gap, visto que h_gaps[0] é [l1_ind, l2_ind, gap]
h_gaps_freq = Counter(g[2] for g in h_gaps).most_common()
v_gaps_freq = Counter(g[2] for g in v_gaps).most_common()
print("Horizontal gaps: ")
print(v_gaps_freq)
print("Vertical gaps: ")
print(v_gaps_freq)
# Agora filtro eles pra estarem dentro dos limites
h_gaps_freq = [g for g in h_gaps_freq if min_allowed_hline_gap < g[0] < max_allowed_hline_gap]
v_gaps_freq = [g for g in v_gaps_freq if min_allowed_vline_gap < g[0] < max_allowed_vline_gap]

print("Horizontal gaps: ")
print(v_gaps_freq)
print("Vertical gaps: ")
print(v_gaps_freq)

# O gap entre minhas celulas deve ser igual ao valor que apareceu com mais frequencia nas listas acima
# ou pelo menos algum valor muito perto disso.
wanted_v_gap = v_gaps_freq[0][0]
wanted_h_gap = h_gaps_freq[0][0]
# Vou agora iterar por todos gaps, se eles estiverem até N pixels de distância do que eu quero, vou separar aquela linha
board_horizontal_lines = []
board_vertical_lines = []
allowed_threshold = 5

# Agora eu itero pelos gaps horizontais, vejo se o gap está no limite aceitavel de 5 pixels
for gap in h_gaps:
    if (wanted_h_gap - allowed_threshold) < gap[2] < (wanted_h_gap + allowed_threshold):
        # Caso esteja, eu dou append na l1 e l2 do gap, caso elas ainda não estejam no board_lines
        l1_index = gap[0]
        l2_index = gap[1]
        l1 = extended_horizontal_lines[l1_index]
        l2 = extended_horizontal_lines[l2_index]

        if l1 not in board_horizontal_lines:
            board_horizontal_lines.append(l1)
        if l2 not in board_horizontal_lines:
            board_horizontal_lines.append(l2)

# Faço a mesma coisa pros verticais
for gap in v_gaps:
    if (wanted_v_gap - allowed_threshold) < gap[2] < (wanted_v_gap + allowed_threshold):
        # Caso esteja, eu dou append na l1 e l2 do gap, caso elas ainda não estejam no board_lines
        l1_index = gap[0]
        l2_index = gap[1]
        l1 = extended_vertical_lines[l1_index]
        l2 = extended_vertical_lines[l2_index]

        if l1 not in board_vertical_lines:
            board_vertical_lines.append(l1)
        if l2 not in board_vertical_lines:
            board_vertical_lines.append(l2)

print("Board Horizontal Lines:\n",  board_horizontal_lines)
print("Board Vertical Lines:\n", board_vertical_lines)

# Tem a chance de eu ter pego mais board lines do que necessário
# Assim, todas menos uma das linhas dentro de um threhshold devem ser removidas
h_idx_to_remove = set()
v_idx_to_remove = set()

# Dps que iterei por todas as outras linhas em relação a uma e gravei as que tão perto dela
# eu adiciono essa linha numa lista especial para não ser removida do board
h_dont_remove = []
v_dont_remove = []

# Itera duas vezes pelas horizontais
for ind1, h1 in enumerate(board_horizontal_lines):
    for ind2, h2 in enumerate(board_horizontal_lines):
        # Confere se as duas linhas tem um Y muito proximo um dos outros
        # Tem que ser maior que 1, pq se não qnd a linha compara com ela mesmo, vai remover
        if allowed_threshold >= abs(h1[1] - h2[1]) >= 1:
            h_idx_to_remove.add(ind2)
        # Faz o mesmo pros Y2
        if allowed_threshold >= abs(h1[3] - h2[3]) >= 1:
            h_idx_to_remove.add(ind2)

    if ind1 not in h_idx_to_remove:
        h_dont_remove.append(ind1)

# Itera duas vezes pelas verticais
for ind1, v1 in enumerate(board_vertical_lines):
    for ind2, v2 in enumerate(board_vertical_lines):
        # Confere se as duas linhas tem um X muito proximo um dos outros
        # Tem que ser maior que 1, pq se não qnd a linha compara com ela mesmo, vai remover
        if allowed_threshold>= abs(v1[0] - v2[0]) >= 1:
            v_idx_to_remove.add(ind2)
        # Faz o mesmo pros X2
        if allowed_threshold>= abs(v1[2] - v2[2]) >= 1:
            v_idx_to_remove.add(ind2)
    
    if ind1 not in v_idx_to_remove:
        v_dont_remove.append(ind1)

h_idx_to_remove = list(h_idx_to_remove)
v_idx_to_remove = list(v_idx_to_remove)

print("Horizontal to remove: ", h_idx_to_remove)
print("Vertical to remove: ", v_idx_to_remove)
print("Horizontal DONT remove: ", h_dont_remove)
print("Vertical DONT remove: ", v_dont_remove)

# Realmente remove as linhas com aquele index do board_lines
board_horizontal_lines = [v for i, v in enumerate(board_horizontal_lines) if i not in h_idx_to_remove or i in h_dont_remove]
board_vertical_lines = [v for i, v in enumerate(board_vertical_lines) if i not in v_idx_to_remove or i in v_dont_remove]

print("Horizontal Board lines: ")
print(len(board_horizontal_lines))
print("Vertical Board Lines: ")
print(len(board_vertical_lines))

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

# for v in extended_horizontal_lines:
#     x1,y1,x2,y2 = v
#     cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 0, 0) ,2)

# for h in extended_vertical_lines:
#     x1,y1,x2,y2 = h
#     cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 0, 255) ,2)

for v in board_horizontal_lines:
    x1,y1,x2,y2 = v
    cv.line(edge_rgb,(x1,y1),(x2,y2),(0, 255, 0) ,2)

for h in board_vertical_lines:
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