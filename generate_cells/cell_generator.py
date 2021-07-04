from pathlib import Path
import os
import matplotlib.pyplot as plt
import PIL
from PIL import Image
import random
import sys

def cell_generator(force_color=None, force_piece=None, piece_scale_range=(1,1), vertical_range=(0,0), horizontal_range=(0,0)):
    """
    TODO: add decrição

    Args:
        force_color (str, optional): 'b' for black pieces, 'w' for white. Defaults to None.
        force_piece ([type], optional): 'p' or 'pawn', for pawn, etc... 'Defaults to None.
        piece_scale_range (tuple, optional): (min_scale, max_scale), values between 0 and 1. 
        vertical_range (tuple, optional): (-max_pixels, +max_pixels) for vertical offset. Defaults to (0,0).
        horizontal_range (tuple, optional): (-max_pixels, +max_pixels) for horizontal offset. Defaults to (0,0).

    Yields:
        [str]: Label. For example, 'bB' for black bishop, 'wK' for white king...
        [PIL.Image]: Pillow Image of cell with random background and piece
    """

    #HERE = os.getcwd()
    # Script location
    HERE = sys.path[0]
    pieces = list(Path(os.path.join(HERE, 'pieces')).rglob('*.png'))
    cells =  list(Path(os.path.join(HERE, 'cells')).rglob('*.png'))

    if force_color:
        pieces = [p for p in pieces if p.name[0] == force_color]

    if force_piece:
        # Se passou o nome completo, traduz para o abreviado
        if len(force_piece) > 1:
            force_piece = force_piece.lower()
            pieces_dict = {
                'pawn': 'p',
                'knight': 'n',
                'bishop': 'b',
                'rook': 'r',
                'queen': 'q',
                'king': 'k'
            }
            force_piece = pieces_dict[force_piece]

        # Filtra os modelos das peças
        pieces = [p for p in pieces if p.name[1] == force_piece.upper()]

    while True:

        piece = random.choice(pieces)
        cell = random.choice(cells)

        #image = Image.new('RGB', (100, 100))
        #plt.imshow(image)
        piece_im = Image.open(piece)
        #piece_im.thumbnail((100,100), PIL.Image.ANTIALIAS)
        piece_im = piece_im.resize((100,100), PIL.Image.ANTIALIAS)

        cell_im = Image.open(cell)
        #cell_im.thumbnail((200,200), PIL.Image.ANTIALIAS)
        #cell_im = cell_im.resize((200,200))


        horizontal_offset = random.randint(horizontal_range[0], horizontal_range[1])
        vertical_offset = random.randint(vertical_range[0], vertical_range[1])
        piece_im = piece_im.transform(piece_im.size, Image.AFFINE, (1, 0, horizontal_offset, 0, 1, vertical_offset))

        scale_factor = round(random.uniform(piece_scale_range[0], piece_scale_range[1]), 3)
        maxsize = (piece_im.size[0]*scale_factor, piece_im.size[0]*scale_factor)
        piece_im.thumbnail(maxsize, PIL.Image.ANTIALIAS)

        center_x = cell_im.size[0]//2 - piece_im.size[0]//2
        center_y = cell_im.size[1]//2 - piece_im.size[1]//2

        cell_im.paste(piece_im, (center_x, center_y), piece_im)

        # Converte para escala de cinza
        #cell_im = cell_im.convert('LA')

        yield piece.name[:2], cell_im




if __name__ == "__main__":

    colors_dict = {
    'w': 'White',
    'b': 'Black',
    }

    pieces_dict = {
        'P': 'Pawn',
        'N': 'Knight',
        'B': 'Bishop',
        'R': 'Rook',
        'Q': 'Queen',
        'K': 'King'
    }
    for label, im in cell_generator(force_color=None, force_piece=None, piece_scale_range=(0.85, 1), horizontal_range=(-3, 3), vertical_range=(-10, 10)):
        plt.imshow(im)
        print(colors_dict[label[0]], pieces_dict[label[1]])
        plt.show()