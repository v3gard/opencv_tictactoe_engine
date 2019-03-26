import cv2

from tictactoe import *

def main():
    try:
        ge = GameEngine(use_keyboard=True, debug=1)
        ge.start(use_camera=False)
    except KeyboardInterrupt as e:
        print("\nBye! Thanks for playing!")
    #except Exception as e:
    #    print("Error: " + str(e))
    #    exit(1)
    exit(0)

if __name__=="__main__":
    main()