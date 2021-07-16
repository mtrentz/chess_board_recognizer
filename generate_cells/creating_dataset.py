import os
import sys
import shutil
from cell_generator import cell_generator
import matplotlib.pyplot as plt
from glob import glob

# Diretório do script
HERE = sys.path[0]

# Diretório e arquivos de células em branco que vão ser exportados diretamente como dado de treino/teste/validação
CELLS_DIR = os.path.join(HERE, 'cells')
cell_files = glob(os.path.join(CELLS_DIR, '*.png'))

### CRIANDO ESTRUTURA DOS DIRETORIOS
main_dir = ['cell_dataset']
sub_dir = ['train', 'test', 'validate']
sub_sub_dir = ['bP', 'wP', 'bN', 'wN', 'bB', 'wB', 'bR', 'wR', 'bQ', 'wQ', 'bK', 'wK']
#sub_sub_dir = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']

for d1 in main_dir:
    for d2 in sub_dir:
        for d3 in sub_sub_dir:
            try:
                # Volta 1 diretorio do dir do script
                os.makedirs(os.path.join(HERE, '..', d1, d2, d3))
            except OSError:
                print('Erro. Diretório provavelmente já existe.')
        # Cria um diretório para a classe que vai ser a casa sem nenhuma peça
        try:
            os.makedirs(os.path.join(HERE, '..', d1, d2, 'empty'))
        except OSError:
            pass

###GERANDO O DATASET
# Parametros
piece_scale_range =(0.85, 1)
horizontal_range =(-3, 3)
vertical_range =(-10, 10)

# Train
# n para cada tipo de peça (bP, wB,...)
n_train = 10000
for i in range(n_train):
    print(f'Gerando train dataset: {i}/{n_train}')
    for piece in sub_sub_dir:
        piece_color = piece[0]
        piece_kind = piece[1]
        # Gera a imagem para aquele tipo de peça
        label, im = next(cell_generator(force_piece=piece_kind,
                                        force_color=piece_color,
                                        piece_scale_range=piece_scale_range, 
                                        horizontal_range=horizontal_range, 
                                        vertical_range=vertical_range))

        im.save(os.path.join(HERE, '..', 'cell_dataset', 'train', piece, f'{i}.png'))

# Copia as imagens de celulas vazias pra pasta de treino.
for i, empty_cell in enumerate(cell_files):
    shutil.copy(empty_cell, os.path.join(HERE, '..', 'cell_dataset', 'train', 'empty', f'{i}.png'))



# Test
# n para cada tipo de peça (pawn, bishop,...)
n_test = 1000
for i in range(n_test):
    print(f'Gerando test dataset: {i}/{n_test}')
    for piece in sub_sub_dir:
        piece_color = piece[0]
        piece_kind = piece[1]
        # Gera a imagem para aquele tipo de peça
        label, im = next(cell_generator(force_piece=piece_kind,
                                        force_color=piece_color,
                                        piece_scale_range=piece_scale_range, 
                                        horizontal_range=horizontal_range, 
                                        vertical_range=vertical_range))

        im.save(os.path.join(HERE, '..', 'cell_dataset', 'test', piece, f'{i}.png'))

# Copia as imagens de celulas vazias pra pasta de treino.
for i, empty_cell in enumerate(cell_files):
    shutil.copy(empty_cell, os.path.join(HERE, '..', 'cell_dataset', 'test', 'empty', f'{i}.png'))

# Validate
# n para cada tipo de peça (pawn, bishop,...)
n_validate = 1000
for i in range(n_validate):
    print(f'Gerando validation dataset: {i}/{n_validate}')
    for piece in sub_sub_dir:
        piece_color = piece[0]
        piece_kind = piece[1]
        # Gera a imagem para aquele tipo de peça
        label, im = next(cell_generator(force_piece=piece_kind,
                                        force_color=piece_color,
                                        piece_scale_range=piece_scale_range, 
                                        horizontal_range=horizontal_range, 
                                        vertical_range=vertical_range))

        im.save(os.path.join(HERE, '..', 'cell_dataset', 'validate', piece, f'{i}.png'))

# Copia as imagens de celulas vazias pra pasta de treino.
for i, empty_cell in enumerate(cell_files):
    shutil.copy(empty_cell, os.path.join(HERE, '..', 'cell_dataset', 'validate', 'empty', f'{i}.png'))




