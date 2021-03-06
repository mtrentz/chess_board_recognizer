import cv2 as cv
from PIL import Image
import os
import numpy as np
import torch
from torchvision import transforms
import io

class ChessRecognizer:
    def __init__(self, PIL_img):
        self.img = cv.cvtColor(np.array(PIL_img), cv.COLOR_RGB2BGR)
        self.img_gray = cv.cvtColor(self.img,cv.COLOR_BGR2GRAY)
        self.X_max, self.Y_max, _ = self.img.shape
        self.HERE = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
        # self.model = torch.load(os.path.join(self.HERE, 'torch_model.pth'), map_location=torch.device('cpu'))
        # self.board_horizontal_lines, self.board_vertical_lines = self.board_lines(self.img_gray)
        # self.board_squares = self.board_squares(self.board_horizontal_lines, self.board_vertical_lines)
        # self.predicted_board = self.predict_board(self.img, self.model, self.board_squares)
    

    def _get_lines(self, img_gray):
        """Busca as linhas da imagem"""

        edges = cv.Canny(self.img_gray,50,150,apertureSize = 3)
        # edges = cv.Canny(self.img,50,150,apertureSize = 3)
        lines = cv.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)


        # -> desse post https://stackoverflow.com/questions/45322630/how-to-detect-lines-in-opencv
        # kernel_size = 3
        # blur_gray = cv.GaussianBlur(img_gray,(kernel_size, kernel_size),0)

        # low_threshold = 10
        # high_threshold = 100
        # edges = cv.Canny(blur_gray, low_threshold, high_threshold)

        # rho = 1  # distance resolution in pixels of the Hough grid
        # theta = np.pi / 180  # angular resolution in radians of the Hough grid
        # threshold = 15  # minimum number of votes (intersections in Hough grid cell)
        # min_line_length = 50  # minimum number of pixels making up a line
        # max_line_gap = 20  # maximum gap in pixels between connectable line segments
        # line_image = np.copy(self.img) * 0  # creating a blank to draw lines on

        # # Run Hough on edge detected image
        # # Output "lines" is an array containing endpoints of detected line segments
        # lines = cv.HoughLinesP(edges, rho, theta, threshold, np.array([]),
        #                     min_line_length, max_line_gap)

        return lines

    def _get_oriented_lines(self, lines):
        """Separa as linhas horizontais/verticais"""

        # Quantos graus a linha pode desviar de completamente reta para ser considerada horizontal/vertical
        acceptable_angle_dev = 5

        # Vou separar as linhas em horizontais e verticais
        horizontal_lines = []
        vertical_lines = []

        for line in lines:
            x1,y1,x2,y2 = line[0]

            # Do jeito que ta colocado aqui, se for perfeitamente horizontal o angulo vai ser zero e vertical o angulo ser?? -90
            horizontal_angle = 0
            vertical_angle = -90

            # Calcula angulo da linha
            angle = np.rad2deg(np.arctan2(y2 - y1, x2 - x1))

            if (horizontal_angle - acceptable_angle_dev) <= angle <= (horizontal_angle + acceptable_angle_dev):
                horizontal_lines.append([x1,y1,x2,y2])
            elif (vertical_angle - acceptable_angle_dev) <= angle <= (vertical_angle + acceptable_angle_dev):
                vertical_lines.append([x1,y1,x2,y2])

        return horizontal_lines, vertical_lines
    
    def _extend_lines(self, horizontal_lines, vertical_lines):
        """Extende as linhas na imagem toda, cria tamb??m linhas horizontais/verticais nas bordas da img"""
        
        extended_horizontal_lines = [[0, l[1], self.X_max, l[3]] for l in horizontal_lines]
        extended_vertical_lines = [[l[0], 0, l[2], self.Y_max] for l in vertical_lines]

        # Vou criar uma linha horizontal e vertical nas bordas da imagem
        # Primeiro as horizontais no topo e fundo da img
        extended_horizontal_lines.append([0, 0 , self.X_max, 0])
        extended_horizontal_lines.append([0, self.Y_max , self.X_max, self.Y_max])
        extended_vertical_lines.append([0, 0, 0, self.Y_max])
        extended_vertical_lines.append([self.X_max, 0, self.X_max, self.Y_max])

        return extended_horizontal_lines, extended_vertical_lines
    
    def _filter_board_lines(self, horizontal_lines, vertical_lines):
        """Filtra a lista de linhas para tentar ficar s?? com as linhas do board de xadrez"""

        # Primeiro eu quero garantir q to ordenando as linhas horizontais e verticais na linha na ordem correta
        # Linhas horizontais ser??o ordenadas da mais ao topo ?? mais de baixo, assim, dou sort pelo termo de index 1, que ?? o y1 (o index 3 (y2) daria na mesma)
        horizontal_lines = sorted(horizontal_lines, key=lambda x: x[1])
        # Linhas verticais d??o sort pelo x
        vertical_lines = sorted(vertical_lines, key=lambda x: x[0])

        # Aqui eu pego s?? os valores de y das linhas horizontais
        hline_ys = [l[1] for l in horizontal_lines]
        # Aqui eu vou ter a diferen??a entre os y de cada linha horizontal, visto que o y vai do menor ao maior (ordenei assim), esses valores s??o as distancias positivas em y
        # entre duas retas horizontais consecutivas
        hline_gaps = np.diff(hline_ys)

        # Fazendo o mesmo pras verticais
        vline_xs = [l[0] for l in vertical_lines]
        vline_gaps = np.diff(vline_xs)

        # Vou pegar o valor mais popular dos gaps horizontais. Preciso tirar do numpy pra funcionar o count
        h_mode = max(set(hline_gaps), key=list(hline_gaps).count)
        v_mode = max(set(vline_gaps), key=list(vline_gaps).count)

        # O objetivo aqui agora ?? achar os 'indexes' onde esses valores mais populares acontecem, e garantir q eles s??o consecutivos
        hline_indexes = np.argwhere(hline_gaps == h_mode).flatten()
        vline_indexes = np.argwhere(vline_gaps == v_mode).flatten()

        # Definindo uma fun????o (aqui msm pra ficar organizado) que testa se os valores s??o consecutivos
        is_consecutive = lambda ls: sorted(ls) == list(range(min(ls), max(ls) + 1))

        # Caso a lista n??o seja consecutiva ou n??o tenha 8 gaps (ou seja, entre as 9 linhas do board)
        if not is_consecutive(hline_indexes) or len(hline_indexes) < 8:
            print("N??o foi poss??vel detectar o board")
            quit()

        if not is_consecutive(vline_indexes) or len(vline_indexes) < 8:
            print("N??o foi poss??vel detectar o board")
            quit()

        # Agora vou filtrar as linhas horizontais/verticais 
        # Primeiro nos indexes, se eu achei o index 1 isso significa que as linhas q criam aquele gap, s??o a de index 1 e 2 da lista.
        # Ou seja, preciso pegar todos os mesmos indexes e um a mais no final
        hline_indexes = np.append(hline_indexes, [hline_indexes[-1] + 1])
        vline_indexes = np.append(vline_indexes, [vline_indexes[-1] + 1])

        board_horizontal_lines = np.array(horizontal_lines)
        board_horizontal_lines = board_horizontal_lines[hline_indexes]
        board_vertical_lines = np.array(vertical_lines)
        board_vertical_lines = board_vertical_lines[vline_indexes]

        return board_horizontal_lines, board_vertical_lines
    
    def _get_intersections(self, board_horizontal_lines, board_vertical_lines):
        def make_line(p1, p2):
            A = (p1[1] - p2[1])
            B = (p2[0] - p1[0])
            C = (p1[0]*p2[1] - p2[0]*p1[1])
            return A, B, -C

        def get_line_intersection(L1, L2):
            D  = L1[0] * L2[1] - L1[1] * L2[0]
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]
            if D != 0:
                x = Dx / D
                y = Dy / D
                return x,y
            else:
                return False

        intersections = []
        # TODO: Traduzir os pontos pra uma matriz interpretavel

        for hline in board_horizontal_lines:
            for vline in board_vertical_lines:
                intersec = get_line_intersection(make_line(hline[:2], hline[2:]),
                                            make_line(vline[:2], vline[2:]))
                intersections.append(intersec)

        intersections.sort()
        
        return intersections
    
    def _get_board_squares(self, intersections):
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

        # Os quadrados do board s??o definido pelo (x1, y1) e (x2, y2) do topo esquerda e baixo direita
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

        return board_squares
    
    
    def board_lines(self, img_gray):

        lines = self._get_lines(img_gray)
        horizontal_lines, vertical_lines = self._get_oriented_lines(lines)
        horizontal_lines, vertical_lines = self._extend_lines(horizontal_lines, vertical_lines)
        horizontal_lines, vertical_lines = self._filter_board_lines(horizontal_lines, vertical_lines)

        return horizontal_lines, vertical_lines
    
    def board_squares(self, board_horizontal_lines, board_vertical_lines):

        intersections = self._get_intersections(board_horizontal_lines, board_vertical_lines)
        board_squares = self._get_board_squares(intersections)

        return board_squares
    
    def show_board_lines(self):
        img = self.img
        board_horizontal_lines = self.board_horizontal_lines
        board_vertical_lines = self.board_vertical_lines
        # Linhas horizontais em azul
        for line in board_horizontal_lines:
            x1,y1,x2,y2 = line
            cv.line(img,(x1,y1),(x2,y2),(255, 0, 0) ,2)

        # Linhas verticais em vermelho
        for line in board_vertical_lines:
            x1,y1,x2,y2 = line
            cv.line(img,(x1,y1),(x2,y2),(0, 0, 255) ,2)

        cv.imshow('board_lines', img)
        cv.waitKey(0)

        return None

    def predict_board(self, img, model, board_squares):
        # Classes do modelo
        class_map = {
            '0': 'bB',
            '1': 'bK',
            '2': 'bN',
            '3': 'bP',
            '4': 'bQ',
            '5': 'bR',
            '6': 'em',
            '7': 'wB',
            '8': 'wK',
            '9': 'wN',
            '10': 'wP',
            '11': 'wQ',
            '12': 'wR',
        }

        predicted_board = np.zeros((8,8)).astype(str)

        #cv.rectangle(img=img, pt1=tuple(board_squares[0][0][0]), pt2=tuple(board_squares[0][0][1]), color=(0,0,0), thickness=5)
        for col_index, col in enumerate(board_squares):
            for row_index, row in enumerate(col):

                data_transforms = transforms.Compose([
                        transforms.Resize((116, 116)),
                        transforms.ToTensor(),
                        ])

                cv_crop = img[row[0][1]:row[1][1], row[0][0]:row[1][0]]
                crop = Image.fromarray(cv_crop)
                crop = data_transforms(crop).unsqueeze(0)

                pred = model(crop)
                pred = pred.argmax(dim=1).numpy()

                #named_board_pieces[row_index, col_index] = class_map[str(int(pred[0]))]
                predicted_board[row_index, col_index] = class_map[str(int(pred[0]))]
        
        return predicted_board

def translate_pred_to_pt(predicted_board):
    pt_class_map = {
        'bB': 'Bispo - Preto',
        'bK': 'Rei - Preto',
        'bN': 'Cavalo - Preto',
        'bP': 'Peao - Preto',
        'bQ': 'Rainha - Preto',
        'bR': 'Torre - Preto',
        'em': 'Vazio',
        'wB': 'Bispo - Branco',
        'wK': 'Rei - Branco',
        'wN': 'Cavalo - Branco',
        'wP': 'Peao - Branco',
        'wQ': 'Rainha- Branco',
        'wR': 'Torre- Branco',
    }

    translated_board = np.vectorize(pt_class_map.get)(predicted_board)
    
    return translated_board

def translate_pred_to_unicode(predicted_board):

    code_map = {
        'bB': '\u265d',
        'bK': '\u265a',
        'bN': '\u265e',
        'bP': '\u265f',
        'bQ': '\u265b',
        'bR': '\u265c',
        'em': '',
        'wB': '\u2657',
        'wK': '\u2654',
        'wN': '\u2658',
        'wP': '\u2659',
        'wQ': '\u2655',
        'wR': '\u2656',
    }
    translated_board = np.vectorize(code_map.get)(predicted_board)

    return translated_board


def board_to_fen(board):
    # Coloca tudo em lowercase
    board = np.char.lower(board)

    # Use StringIO to build string more efficiently than concatenating
    with io.StringIO() as s:
        for row in board:
            empty = 0
            for cell in row:
                c = cell[0]
                if c in ('w', 'b'):
                    if empty > 0:
                        s.write(str(empty))
                        empty = 0
                    s.write(cell[1].upper() if c == 'w' else cell[1].lower())
                else:
                    empty += 1
            if empty > 0:
                s.write(str(empty))
            s.write('/')
        # Move one position back to overwrite last '/'
        s.seek(s.tell() - 1)
        # If you do not have the additional information choose what to put
        s.write(' w KQkq - 0 1')
        return s.getvalue()


if __name__ == "__main__":
    HERE = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    im = Image.open(os.path.join(HERE, 'chessboard_1.png'))

    img = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

    # # -> Desse post: https://stackoverflow.com/questions/57161974/python-opencv-detecting-chessboard
    # ## termination criteria
    # criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # nline = 7
    # ncol = 7

    # # Find the chessboard corners
    # ret, corners = cv.findChessboardCorners(gray, (nline, ncol))
    # print(ret)
    # # corners2 = cv.cornerSubPix(gray, corners, (nline, ncol), (-1, -1), criteria)

    # for corner in corners:
    #     c = corner[0]
    #     cv.circle(img, (int(c[0]), int(c[1])), radius=2, color=(0, 0, 255), thickness=2)
    #     # cv.circle(img, (11,11), radius=2, color=(0, 0, 255), thickness=2)

    # # print(corners)
    # cv.imshow('b_corners', img)
    # cv.waitKey(0)

    

    # rec = ChessRecognizer(im)
    # lines = rec._get_lines(rec.img_gray)

    # img = rec.img

    # for line in lines:
    #     x1,y1,x2,y2 = line[0]
    #     cv.line(img,(x1,y1),(x2,y2),(0, 0, 255) ,2)
    # cv.imshow('board_lines', img)
    # cv.waitKey(0)


    # hlines, vlines = rec._get_oriented_lines(lines)

    # for line in hlines:
    #     x1,y1,x2,y2 = line
    #     cv.line(img,(x1,y1),(x2,y2),(0, 0, 255) ,2)


    # for line in vlines:
    #     x1,y1,x2,y2 = line
    #     cv.line(img,(x1,y1),(x2,y2),(255, 0, 0) ,2)

    # cv.imshow('board_lines', img)
    # cv.waitKey(0)


    # lines = self._get_lines(img_gray)
    # horizontal_lines, vertical_lines = self._get_oriented_lines(lines)
    # horizontal_lines, vertical_lines = self._extend_lines(horizontal_lines, vertical_lines)
    # horizontal_lines, vertical_lines = self._filter_board_lines(horizontal_lines, vertical_lines)


    # img = self.img
    # board_horizontal_lines = self.board_horizontal_lines
    # board_vertical_lines = self.board_vertical_lines
    # # Linhas horizontais em azul
    # for line in board_horizontal_lines:
    #     x1,y1,x2,y2 = line
    #     cv.line(img,(x1,y1),(x2,y2),(255, 0, 0) ,2)

    # # Linhas verticais em vermelho
    # for line in board_vertical_lines:
    #     x1,y1,x2,y2 = line
    #     cv.line(img,(x1,y1),(x2,y2),(0, 0, 255) ,2)

    # cv.imshow('board_lines', img)
    # cv.waitKey(0)








