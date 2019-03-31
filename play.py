import cv2
from optparse import OptionParser
import Dobot.DobotDllType as dType

from tictactoe import *
from tictactoe.Dobot import DobotManager

def main():
    parser = OptionParser()
    parser.add_option("-m", "--manual", dest="dobot",
                  action="store_false", help="Use manual mode (dont access camera or dobot) but use prestored image")
    parser.add_option("-b", "--dobot",
                  action="store_true", dest="dobot", default=True,
                  help="Use Dobot and camera integration (default)")
    parser.add_option("-d", "--debug",
                  action="count", dest="debug", default=0,
                  help="Enable debug mode")

    (options, args) = parser.parse_args()
    dm=None
    if options.dobot == True:
        api = dType.load()
        state = dType.ConnectDobot(api, "", 115200)[0]
        if state != 0:
            print("Unable to access Dobot. It is currently offline, busy or in error mode.")
            print("Verify that Dobot Studio is not connected and try again.")
            exit(1)
        dm = DobotManager(dType, api)
    try:
        ge = GameEngine(dobot_manager=dm, debug=options.debug)
        if options.dobot == True:
            ge.start(use_camera=True, gameboard_file=None)
        else:
            ge.start(use_camera=False, gameboard_file="games/default.jpg")
    except KeyboardInterrupt as e:
        print("\nBye! Thanks for playing!")
    except Exception as e:
        print("Error: " + str(e))
        exit(1)
    exit(0)

if __name__=="__main__":
    main()