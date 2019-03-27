import cv2

from tictactoe import *

def main():
    try:
        ge = GameEngine(use_keyboard=False, debug=0)
        ge.start(use_camera=True, gameboard_file="tests/234505.jpg")
    except KeyboardInterrupt as e:
        print("\nBye! Thanks for playing!")
    #except Exception as e:
    #    print("Error: " + str(e))
    #    exit(1)
    exit(0)

if __name__=="__main__":
    main()