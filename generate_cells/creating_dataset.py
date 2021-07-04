import os
import sys
from cell_generator import cell_generator
import matplotlib.pyplot as plt

# Diretório do script
HERE = sys.path[0]

### CRIANDO ESTRUTURA DOS DIRETORIOS
main_dir = ['cell_dataset']
sub_dir = ['train', 'test', 'validate']
sub_sub_dir = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']

for d1 in main_dir:
    for d2 in sub_dir:
        for d3 in sub_sub_dir:
            try:
                # Volta 1 diretorio do dir do script
                os.makedirs(os.path.join(HERE, '..', d1, d2, d3))
            except OSError:
                print('Erro. Diretório provavelmente já existe.')

###GERANDO O DATASET
# Parametros
piece_scale_range =(0.85, 1)
horizontal_range =(-3, 3)
vertical_range =(-10, 10)

# Train
# n para cada tipo de peça (pawn, bishop,...)
n_train = 1000
for i in range(n_train):
    for piece_kind in sub_sub_dir:
        print(f'Gerando train dataset: {i}/{n_train}')
        # Gera a imagem para aquele tipo de peça
        label, im = next(cell_generator(force_piece=piece_kind,
                                        piece_scale_range=piece_scale_range, 
                                        horizontal_range=horizontal_range, 
                                        vertical_range=vertical_range))

        im.save(os.path.join(HERE, '..', 'cell_dataset', 'train', piece_kind, f'{i}.png'))

# Test
# n para cada tipo de peça (pawn, bishop,...)
n_test = 200
for i in range(n_test):
    for piece_kind in sub_sub_dir:
        print(f'Gerando test dataset: {i}/{n_test}')
        # Gera a imagem para aquele tipo de peça
        label, im = next(cell_generator(force_piece=piece_kind,
                                        piece_scale_range=piece_scale_range, 
                                        horizontal_range=horizontal_range, 
                                        vertical_range=vertical_range))

        im.save(os.path.join(HERE, '..', 'cell_dataset', 'test', piece_kind, f'{i}.png'))

# Validate
# n para cada tipo de peça (pawn, bishop,...)
n_validate = 200
for i in range(n_validate):
    for piece_kind in sub_sub_dir:
        print(f'Gerando validation dataset: {i}/{n_validate}')
        # Gera a imagem para aquele tipo de peça
        label, im = next(cell_generator(force_piece=piece_kind,
                                        piece_scale_range=piece_scale_range, 
                                        horizontal_range=horizontal_range, 
                                        vertical_range=vertical_range))

        im.save(os.path.join(HERE, '..', 'cell_dataset', 'validate', piece_kind, f'{i}.png'))



