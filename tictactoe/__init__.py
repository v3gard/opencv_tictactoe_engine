import cv2
import numpy as np
import math
import imutils
import sys
import pdb
import random

from scipy.spatial import distance as dist

PLAYERS = ["X","O"]

class GameEngine(object):
    def __init__(self):
        self.gameboard = ["?"]*9
        self._gameboard = None # temporary variable for opencv board
        self.moves = []
        self._winning_combinations = (
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6])
        self.player, self.enemy = self._ask_player_letter()
        self.currentplayer = self._decide_initial_player()
    
    def _is_board_empty(self):
        unique = set(self.gameboard)
        if (len(unique) == 1) and unique[0] == "?":
            return True
        return False
    
    def _is_game_won(self):
        for player in PLAYERS:
            for combos in self._winning_combinations:
                if (self.gameboard[combos[0]] == player and self.gameboard[combos[1]] == player and self.gameboard[combos[2]] == player):
                    return player
        if "?" not in self.gameboard:
            return "tie"
        return None

    def _get_free_position(self):
        board = self.gameboard
        free = [i for i,pos in enumerate(board) if pos=="?"]
        return random.choice(free)

    def _decide_initial_player(self):
        return random.choice(PLAYERS)

    def _ask_player_letter(self):
        player = input("Do you want to play as [O] or X? ")
        if (player.lower() == "x"):
            player="X"
            enemy="O"
        else:
            player="O"
            enemy="X"
        return (player, enemy)

    def _is_move_valid(self, move):
        pos = -1
        try:
            pos = int(move)
        except:
            return None
        if self.gameboard[pos] == "?":
            return pos
        return None

    def _update_board(self, pos, player):
        self.gameboard[pos] = player
        self._gameboard.positions[pos].draw_symbol_on_position(player, pos)

    def _ask_player_move(self):
        valid = False
        while (not valid):
            pos = input("Enter position [0-8]: ")
            valid_pos = self._is_move_valid(pos)
            if (valid_pos != None):
                valid=True
                self._update_board(valid_pos, self.player)
                self.currentplayer = self.enemy

    def _make_move(self):
        if self.currentplayer == self.player:
            self._ask_player_move()
        else:
            self._ai_make_move()

    def _ai_make_move(self):
        pos = self._get_free_position()
        self._update_board(pos, self.enemy)
        self.currentplayer = self.player

    def show_gameboard(self):
        t = self.gameboard
        print("{0} {1} {2}".format(t[0], t[1], t[2]))
        print("{0} {1} {2}".format(t[3], t[4], t[5]))
        print("{0} {1} {2}".format(t[6], t[7], t[8]))

    def _parse_gameboard(self, gameboard_file):
        image = cv2.imread(gameboard_file)
        self._gameboard = Gameboard.detect_game_board(image, debug=False)

    def start(self, gameboard_file="games/default.jpg"):
        self.show_gameboard()
        while (not self._is_game_won()):
            self._parse_gameboard(gameboard_file)
            print("your move player {0}".format(self.currentplayer))
            self._make_move()
            self.show_gameboard()
        winner = self._is_game_won()
        self.show_gameboard()
        if (winner == "tie"):
            print("GAME OVER! IT WAS A TIE!")
        elif (winner == self.player):
            print("YOU WON!")
        else:
            print("GAME OVER! YOU LOST!")

class Gameposition(object):
    def __init__(self, src_image, bin_image, title, rect, debug=False):
        self.source = src_image
        self.image = bin_image
        self.id = str(id(self))
        self.title = title
        self.symbol = "?"
        self.area = None
        self.rect = rect
        self.solidity = None
        self.debug = debug
        self._process_subimage(rect)

    def _process_subimage(self, rect):      
        (tl, tr, bl, br) = tuple(rect)
        self.startpos = list(tl)
        self.endpos = list(br)
        dx = int(round(dist.euclidean(tl, tr),0))
        dy = int(round(dist.euclidean(tl, bl),0))
        if (self.endpos[0] > self.image.shape[0]):
            self.endpos[0] = list(self.image.shape)[0]
        if (self.endpos[1] > self.image.shape[1]):
            self.endpos[1] = list(self.image.shape)[1]
        self.startpos = tuple(self.startpos)
        self.endpos = tuple(self.endpos)
        self.roi = self.image[self.startpos[1]:self.endpos[1], self.startpos[0]:self.endpos[0]]
        #cv2.imshow("roi: " + self.title, self.roi)
        #cv2.waitKey(0)
        self.roi_in_source = self.source[self.startpos[1]:self.endpos[1], self.startpos[0]:self.endpos[0]]
        self.area = dx*dy

    def draw_rectangle_on_image(self, image=None):
        if (type(image) != np.ndarray):
            image = self.image
        cv2.rectangle(image, self.startpos, self.endpos, (255,0,0), 1)
        #if self.debug > 1:
        #    cv2.imshow(self.id, image)
        #    cv2.waitKey(0)

    def draw_symbol_on_position(self, symbol, position):
        coordinate = tuple(self.rect[0])
        font = cv2.FONT_HERSHEY_SIMPLEX
        black = (0,0,0)
        cv2.putText(self.source, symbol, coordinate, font, 4, black, 2, cv2.LINE_AA)
    
    def is_checked(self):
        return False
    
    def detect_symbol(self, avg_area=None):
        """ assumes self.image is binary
        based on:
        * https://gurus.pyimagesearch.com/lesson-sample-advanced-contour-properties/
        * http://qtandopencv.blogspot.com/2015/11/analyze-tic-tac-toe-by-computer-vision.html
        """
        #cv2.imshow(self.title, self.roi)
        #cv2.waitKey(0)
        imgcopy = self.roi.copy()
        #cv2.imshow("blabla", imgcopy)
        #with np.printoptions(threshold=np.inf,linewidth=2000):
        #    with open("roi.txt", "w") as f:
        #        f.write(str(imgcopy))
        #    print("Printed " + self.title)
        #    input("Trykk en tast...")
        cnts = cv2.findContours(imgcopy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        lSolidity = []
        for (i, c) in enumerate(cnts):
            # compute the area of the contour along with the bounding box
            # to compute the aspect ratio
            area = cv2.contourArea(c)
            #print("countor area: {0}, detection area: {1}".format(area, self.area))
            # if there are multiple contours detected, check if the detected contour is at
            # least 10% of total area
            if (len(cnts) > 1 and i>=0 and area < self.area*0.06 ):
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            # compute the convex hull of the contour, then use the area of the
            # original contour and the area of the convex hull to compute the
            # solidity
            hull = cv2.convexHull(c)
            hullArea = cv2.contourArea(hull)
            if (hullArea == 0):
                hullArea = 0.1
            solidity = area / float(hullArea)
            self.solidity = solidity
            lSolidity.append(solidity)
            found = False
            if (self._detect_if_o(solidity)):
                self.symbol = "O"
                found = True
            elif (self._detect_if_x(solidity)):
                found = True
                self.symbol = "X"
            if found:
                if self.debug>0:
                    print("{0}: Contours: {1}, Solidity: {2}".format(self.title, len(cnts), solidity))
                    img = self.roi_in_source.copy()
                    cv2.drawContours(img,[c],0,(0,255,0),-1)
                    cv2.imshow(self.title, img)
                    cv2.waitKey(0)
                break
        if (self.symbol in ("O","X")):
            cv2.putText(self.roi_in_source, self.symbol, (int(x+(w/2)), int(y+(h/2))), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 0, 255), 4)
            return True
        return False
    
    def _detect_if_x(self, solidity):
        if (solidity > 0.3 and solidity < 0.9):
            return True
        return False
    
    def _detect_if_o(self, solidity):
        if (solidity > 0.9):
            return True
        return False
        

class Gameboard(object):
    boardtype = "3x3"
    def __init__(self, img_source, img_binary, intersection_size, intersection_points, debug=False):
        self.source = img_source
        self.binary = img_binary
        self.intersection_size = intersection_size
        self.intersection_points = intersection_points
        self.intersection_mask = None
        self.debug = debug
        self.positions = []
        #cv2.bitwise_not(self.binary, self.binary, self.intersection_mask)
        # create positions, order = bottom left, bottom right, upper left, upper right
        #print(self.binary.shape)
        #np.set_printoptions(edgeitems=3000, linewidth=400000, formatter=dict(float=lambda x: "%.3g" % x))
        #with open("board.txt", "w") as f:
        #    f.write(str(self.binary.reshape(self.binary.shape)))
        self._calculate_positions()
        self._draw_positions()
        self._detect_symbols()

    def __repr__(self):
        jeje = str(self.status())
        return jeje

    def draw_symbol_on_slot(self, symbol, slot):
        pass

    def status(self):
        return np.array([pos.symbol for pos in self.positions], dtype=str)

    def _detect_symbols(self):
        for position in self.positions:
            position.detect_symbol()

    def _draw_positions(self):
        for position in self.positions:
            position.draw_rectangle_on_image(self.source)
        if self.debug>0:
            cv2.imshow("Game positions", self.source)
            cv2.waitKey(0)

    def _order_points(self, unordered_points):
        """ Orders given points from top left, top right, bottom left, bottom right """
        pts = np.array(unordered_points,dtype=int)
        # Sort by X coordinates
        xSorted = pts[np.argsort(pts[:,0]),:]
        # Grab left-most and right-most points from the sorted x-coordinates
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:,:]
        # Sort left-most according to Y-coordinates to find top left and bottom left
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl,bl) = leftMost
        
        # Calculate Euclidian distance from top left anchor to bottom right anchor
        # using the Pythagorean theorem. The point with the largest distance
        # is the bottom right
        D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
        (br, tr) = rightMost[np.argsort(D)[::-1], :]
        return np.array([tl,tr,bl,br], dtype=int)

    def _slope(self, a, b):
        return float((b[1]-a[1])/(b[0]-a[0]))

    def _create_line(self, p1, p2):
        p = [0,0]
        q = list(self.source.shape[0:2])
        if (p1[0] != p2[0]):
            m = self._slope(p1,p2)
            # y = m * x + b
            # b = y - (m*x)
            b = p1[1] - m*p1[0]
            p[1] = int(m * p[0] + b)
            q[1] = int(m * q[0] + b)
        else:
            p[0] = p2[0]
            q[0] = p2[0]
        p = tuple(p)
        q = tuple(q)
        return (p,q)

    def _create_mask(self, ordered_intersection_points):
        pts = ordered_intersection_points
        l1 = self._create_line(list(pts[0]), list(pts[2]))
        l2 = self._create_line(list(pts[1]), list(pts[3]))
        l3 = self._create_line(list(pts[0]), list(pts[1]))
        l4 = self._create_line(list(pts[2]), list(pts[3]))

        mask = np.zeros(self.source.shape, self.source.dtype)

        white = (255,255,255)
        black = (0,0,0)
        cv2.line(mask,l1[0],l1[1],white,int(self.intersection_size*1.1))
        cv2.line(mask,l2[0],l2[1],white,int(self.intersection_size*1.1))
        cv2.line(mask,l3[0],l3[1],white,int(self.intersection_size*1.1))
        cv2.line(mask,l4[0],l4[1],white,int(self.intersection_size*1.1))
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        cv2.bitwise_not(self.binary, self.binary, mask)

    def _calculate_positions(self):
        middle = self._order_points(self.intersection_points)
        mask = self._create_mask(middle)
        #middle = np.floor_divide(middle, 10/9).astype(int)
        dx = int(round(dist.euclidean(middle[0], middle[1]),0))
        dy = int(round(dist.euclidean(middle[0], middle[2]),0))
        
        offset_x_y = np.array([dx,dy])
        offset_nx_y = np.array([-dx,dy])
        offset_x_ny = np.array([dx,-dy])
        offset_x = np.array([dx,0])
        offset_y = np.array([0,dy])

        

        topleft = np.subtract(middle,offset_x_y)
        topright = np.add(middle, offset_x_ny)
        midtop = np.subtract(middle, offset_y)
        midbottom = np.add(middle, offset_y)
        bottomright = np.add(middle,offset_x_y)
        bottomleft = np.subtract(middle, offset_x_ny)
        leftmost = np.subtract(middle, offset_x)
        rightmost = np.add(middle, offset_x)

        self.positions = [
                    Gameposition(self.source, self.binary, "tl", topleft, self.debug),
                    Gameposition(self.source, self.binary, "mt", midtop, self.debug),
                    Gameposition(self.source, self.binary, "tr", topright, self.debug),
                    Gameposition(self.source, self.binary, "ll", leftmost, self.debug),
                    Gameposition(self.source, self.binary, "mm", middle, self.debug),
                    Gameposition(self.source, self.binary, "rr", rightmost, self.debug),
                    Gameposition(self.source, self.binary, "bl", bottomleft, self.debug),
                    Gameposition(self.source, self.binary, "mb", midbottom, self.debug),
                    Gameposition(self.source, self.binary, "br", bottomright, self.debug),
        ]

    @staticmethod
    def _get_center_position_of_rectangle(x1,x2,y1,y2):
        return (x1+int((x2-x1)/2), int(y1+(y2-y1)/2))

    @staticmethod
    def _preprocess_image_to_binary(image, debug=False):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thres, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kernel = np.array((
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]), dtype="int")
        binary = cv2.erode(binary, kernel)
        # Invert the image
        binary = 255-binary
        if debug > 2:
            cv2.imshow("binary",binary)
            cv2.waitKey(0)
        return binary

    @staticmethod
    def detect_game_board(source, debug=False):
        image = Gameboard._preprocess_image_to_binary(source, debug)
        # Defining a kernel length
        kernel_length = np.array(image).shape[1]//8
        # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
        verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
        # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
        hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
        # A kernel of (3 X 3) ones
        kernel = np.array((
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]), dtype="int")
        # Morphological operation to detect vertical lines from an image
        img_temp1 = cv2.erode(image, verticle_kernel, iterations=1)
        verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=1)
        if debug > 3:
            cv2.imshow("vlines", verticle_lines_img)
            cv2.waitKey(0)
        # Morphological operation to detect horizontal lines from an image
        img_temp2 = cv2.erode(image, hori_kernel, iterations=1)
        horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=1)
        if debug > 3:
            cv2.imshow("hlines", horizontal_lines_img)
            cv2.waitKey(0)
        intersections = cv2.bitwise_and(verticle_lines_img, horizontal_lines_img)
        if debug > 2:
            cv2.imshow("intersections", intersections)
            cv2.waitKey(0)
        # Create a mask, combine verticle and horizontal lines
        mask = verticle_lines_img + horizontal_lines_img
        # Find contours
        contours, hierarchy = cv2.findContours(intersections, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Find center positions, order = bottom left, bottom right, upper left, upper right
        positions = []
        red = (0,0,255)
        blue = (255,0,0)

        for i,cnt in enumerate(contours):
            boardweight = 0.1 # decrease this for finer detection
            approx = cv2.approxPolyDP(cnt, boardweight*cv2.arcLength(cnt, True), True)
            cv2.drawContours(source,[cnt],0,red,-1)
            if debug>3:
                cv2.imshow("Showing game board intersection {0}".format(i+1),source)
                cv2.waitKey(0)
            if len(approx) in (4,):
                # get the bounding rect
                x, y, w, h = cv2.boundingRect(cnt)
                #print(x,y,w,x)
                cv2.rectangle(source, (x,y), (x+w,y+h), (255,0,0), 1)
                if debug>1:                   
                    cv2.imshow("rectangle", source)
                    cv2.waitKey(0)
                # find center
                center = Gameboard._get_center_position_of_rectangle(x, x+w, y, y+h)
                positions.append(center)
            else:
                raise Exception("Unable to detect game board intersections. Try to adjust the weight.")
        if (len(positions) != 4):
            raise Exception("Unable to detect 3x3 game board")
        return Gameboard(source, image, w, positions, debug)
