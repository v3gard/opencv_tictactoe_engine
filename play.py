import cv2
import Dobot.DobotDllType as dType

from tictactoe import *
from tictactoe.Dobot import DobotManager

def main():
    try:
        api = dType.load()
        state = dType.ConnectDobot(api, "", 115200)[0]

        if state != 0:
            print("Unable to access Dobot. It is currently busy or in error mode.")
            print("Verify that Dobot Studio is not connected and try again.")
            exit(1)

        dm = DobotManager(dType, api)
        ge = GameEngine(dobot_manager=dm, use_keyboard=False, debug=0)
        ge.start(use_camera=True, gameboard_file="tests/234505.jpg")
    except KeyboardInterrupt as e:
        print("\nBye! Thanks for playing!")
    #except Exception as e:
    #    print("Error: " + str(e))
    #    exit(1)
    exit(0)

if __name__=="__main__":
    main()