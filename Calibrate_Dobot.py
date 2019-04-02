import Dobot.DobotDllType as dType
import json
from tictactoe.Dobot import DobotManager, DobotPosition

api = dType.load()
state = dType.ConnectDobot(api, "", 115200)[0]

if state != 0:
    print("Unable to access Dobot. It is currently busy or in error mode.")
    print("Verify that Dobot Studio is not connected and try again.")
    exit(1)

def show_position():
    done = False
    while not done:
        cont = input("Move arm. Press [enter] to show position. Press [x] to quit")
        if cont.lower() == "x":
            break
        p = dType.GetPose(api)
        pos = DobotPosition(p[0], p[1], p[2], p[3])
        print("Current position: {0}\n".format(pos))


def calibrate(exists=False):
    if exists:
        print("WARNING!")
        print("Calibration data already exists!")
        print("If you continue, the existing data will be deleted.")
        cont = input("Continue? [y/N] ")
        if (cont.lower() != "y"):
            print("Cancelled.")
            return
      
    dType.SetHOMECmdEx(api, 0, 1)
    print("Home position set. Press [enter] to continue.")
    
    slot = {}
    buffer = {}
    
    print("""
    Board Position Calibration
            +-------+
            | 1 2 3 | 
            | 4 5 6 |   O1
            | 7 8 9 |   O2
            |       |   O3
            |   D   |   O4
            +-------+   O5
    """)
    
    for i in range(9):
        print("BOARD POSITION {0}\n----------------".format(i+1))
        print("1. Press and hold position button on Dobot.")
        print("2. Move arm manually to board position {0}. ".format(i+1))
        cont = input("3. Press [enter] to continue.")
        p = dType.GetPose(api)
        slot[i] = DobotPosition(p[0], p[1], p[2], p[3])
        print("Learned position {0}: {1}\n".format(i+1, slot[i]))

    for i in range(5):
        print("BUFFER POSITION O{0}\n----------------".format(i+1))
        print("1. Press and hold position button on Dobot.")
        print("2. Move arm manually to buffer  position {0}. ".format(i+1))
        cont = input("3. Press [enter] to continue.")
        p = dType.GetPose(api)
        buffer[i] = DobotPosition(p[0], p[1], p[2], p[3])
        print("Learned position {0}: {1}\n".format(i+1, buffer[i]))
    
    print("CAMERA POSITION\n---------------")
    print("1. Enable the camera on your PC.")
    print("2. Move the arm so that so that the game board is fully visible to the camera")
    print("   IMPORTANT! Use an A3 paper. Make sure the field of view covers the paper only!")
    cont = input("3. Press [enter] to continue.")
    p = dType.GetPose(api)
    camera = DobotPosition(p[0], p[1], p[2], p[3])

    print("POSE POSITION\n---------------")
    print("1. Enable the camera on your PC.")
    print("2. Given the previous camera position, move the arm to a new position that will")
    print("   be used for 'posing' whenever the robot wins or looses.")
    cont = input("3. Press [enter] to continue.")
    p = dType.GetPose(api)
    pose = DobotPosition(p[0], p[1], p[2], p[3])

    
    positions = {}
    positions["slots"] = {key:slot[key].__dict__ for key in slot.keys()}
    positions["buffer"] = {key:buffer[key].__dict__ for key in buffer.keys()}
    positions["camera"] = camera.__dict__
    positions["pose"] = pose.__dict__
    
    with open("calibration.data", "w") as f:
        f.write(json.dumps(positions))
    
    print("Dobot calibrated for Tic Tac Toe!")
    return (camera,buffer,slot, pose)

def test(dobot_manager, camera, buffer, slot):
    dm = dobot_manager
    dm.set_speed()
    print("Going to camera position...")
    camera.movej_nooffset(dm)
    print("Testing all board positions...")
    for i in sorted(slot.keys()):
        print("Going to position {0}...".format(i+1))
        slot[i].move(dm, jumpspeed=50)
        dm.set_speed(velocity=100)
    print("Done")
    print("Testing all buffer positions...")
    for i in sorted(buffer.keys()):
        print("Going to buffer position {0}...".format(i+1))
        buffer[i].move(dm)
    print("Done. Returning to camera position...")
    camera.movej_nooffset(dm)
    print("Test complete.")

def pick_and_place(dobot_manager, camera, buffer, slot):
    dm = dobot_manager
    for i in range(5):
        p1 = buffer[i]
        p2 = slot[i]
        p1.pick(dm)
        p2.place(dm)

    for i in range(5):
        p1 = buffer[i]
        p2 = slot[i]
        p2.pick(dm)
        p1.place(dm)

def set_home(dobot_manager):
    dobot_manager.set_home()

def main():
    exists = False
    slot = {}
    buffer = {}
    camera = None
    jsondata = None
    dm = DobotManager(dType, api)
    try:
        with open("calibration.data", "r") as f:
            data = f.read()
            jsondata = json.loads(data)
            exists = True
    except Exception:
        pass
    camera,buffer,slot,pose = DobotPosition.deserialize(jsondata)

    print("\n---------------------------------------------")
    print("OpenCV Tic Tac Toe Engine - Dobot Calibration")
    print("---------------------------------------------\n")
    print("Calibration data available: {0}\n".format("yes" if exists else "no"))

    done = False
    while not done:
        print("1. Calibrate Dobot for Tic Tac Toe board")
        print("2. Show Dobot arm position")
        print("3. Reinitialize home position")
        if exists:
            print("4. Test calibration (without tokens)")
            print("5. Pick and place token")
        print ("X. Exit")
        choice = input("Select task: ")
        if choice == "1":
            camera,buffer,slot,pose = calibrate(exists)
        elif choice == "2":
            show_position()
        elif choice == "3":
            set_home(dm)
        elif exists and choice == "4":
            test(dm, camera, buffer, slot)
        elif exists and choice == "5":
            pick_and_place(dm, camera, buffer, slot)
        else:
            done = True

if __name__ == "__main__":
    main()