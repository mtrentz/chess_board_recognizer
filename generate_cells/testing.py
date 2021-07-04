from pathlib import Path
import os
import matplotlib.pyplot as plt
from PIL import Image
import random

HERE = os.getcwd()
pieces = list(Path(os.path.join(HERE, 'pieces')).rglob('*.png'))
cells =  list(Path(os.path.join(HERE, 'cells')).rglob('*.png'))

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

#print([p.name for p in pieces])

for i in range(3):
    piece = random.choice(pieces)
    cell = random.choice(cells)
    piece_kind = pieces_dict[piece.name[1]]
    piece_color = colors_dict[piece.name[0]]
    print(piece_color, piece_kind)

    #image = Image.new('RGB', (100, 100))
    #plt.imshow(image)
    piece_im = Image.open(piece)
    cell_im = Image.open(cell)
    cell_im = cell_im.resize((200,200))

    #                                                            left/right  up/down
    #                                                                 v        v
    piece_im = piece_im.transform(piece_im.size, Image.AFFINE, (1, 0, 0, 0, 1, 10))

    cell_im.paste(piece_im, (0, 0), piece_im)
    plt.imshow(cell_im)
    plt.show()
    # plt.imshow(cell_im)
    # plt.imshow(piece_im)
    # plt.show(block=False)
    # plt.pause(0.5)
    # plt.close()


# piece = plt.imread(pieces[12])
# cell = plt.imread(cells[12])
# plt.imshow(cell)
# plt.imshow(piece)
# plt.show()

# for path in Path(os.path.join(HERE, 'pieces')).rglob('*.png'):
#     print(os.path.basename(os.path.dirname(path)))
#     break

