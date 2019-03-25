from tictactoe import *

title = "Tic tac toe board tester"

def print_header():
    print("-"*len(title))
    print(title)
    print("-"*len(title))

def main():
    tests = {"Empty board": {
                "path":"tests/empty_board.jpg",
                "x_count": 0,
                "o_count": 0},
             "One average x":{
                "path":"tests/one_average_x.jpg",
                "x_count": 1,
                "o_count": 0},
            "O=4 and X=3":{
                "path":"tests/4O_and_3X.jpg",
                "x_count": 3,
                "o_count": 4},
            "Two circles":{
                "path":"tests/two_circles.jpg",
                "x_count": 0,
                "o_count": 2},
            "Nine circles":{
                "path":"tests/nine_circles.jpg",
                "x_count": 0,
                "o_count": 9},
            "Nine crosses":{
                "path":"tests/nine_crosses.jpg",
                "x_count": 9,
                "o_count": 0},
            "Small empty board":{
                "path":"tests/small_empty_board.jpg",
                "x_count": 0,
                "o_count": 0},
            "Small, X=1":{
                "path":"tests/small_one_cross.jpg",
                "x_count": 1,
                "o_count": 0},
            "Small, X=6":{
                "path":"tests/small_six_cross.jpg",
                "x_count": 6,
                "o_count": 0},
            "FullHD, small, O=2, X=1":{
                "path":"tests/fullhd_small_2O_1X.jpg",
                "x_count": 1,
                "o_count": 2},
            "FullHD, small, O=3, X=3":{
                "path":"tests/fullhd_small_3O_3X.jpg",
                "x_count": 3,
                "o_count": 3},
            "Narrow lines, O=1, X=2":{
                "path":"tests/narrow_lines_1O_2X.jpg",
                "x_count": 2,
                "o_count": 1},
    }

    print_header()
    count = 0
    for title in tests:
        test = tests[title]
        image = cv2.imread(test["path"])
        gameboard = Gameboard.detect_game_board(image, debug=False)
        status = gameboard.status()
        x_count = len([pos for pos in status if pos == "X"])
        o_count = len([pos for pos in status if pos == "O"])
        result = "FAILED"
        if (x_count == test["x_count"] and o_count == test["o_count"]):
            result = "PASSED"
            count += 1
        print("{0:30} {1:10}(O={2}, X={3})".format(title.upper(), result, o_count, x_count))
        if result == "FAILED":
            for pos in gameboard.positions:
                pass
                #print(" - " + str(pos.solidity))
    print("\nOK! {0}/{1} tests passed".format(count, len(tests)))

if __name__=="__main__":
    main()