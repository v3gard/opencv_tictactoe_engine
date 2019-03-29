import json

class DobotPosition(object):
    def __init__(self, x, y, z, r):
        self.x = x
        self.y = y
        self.z = z
        self.r = r

    def __repr__(self):
        return "X={0}, Y={1}, Z={2}, R={3}".format(self.x, self.y, self.z, self.r)

    def move(self, dobot_manager, zoffset=12, wait=1):
        dm = dobot_manager
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, 0, self.r, 1)
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, self.z+zoffset, self.r, 1)
        dm.dType.SetWAITCmdEx(dm.api, wait, 1)
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, 0, self.r, 1)

    def move_nooffset(self, dobot_manager, wait=5):
        dm = dobot_manager
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, self.z, self.r, 1)
        dm.dType.SetWAITCmdEx(dm.api, wait, 1)

    def pick(self, dobot_manager, zoffset=10, wait=0.5):
        dm = dobot_manager
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, 0, self.r, 1)
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, self.z+zoffset, self.r, 1)
        dm.dType.SetWAITCmdEx(dm.api, wait, 1)
        dm.dType.SetEndEffectorSuctionCupEx(dm.api, 1, 1)
        dm.dType.SetWAITCmdEx(dm.api, wait, 1)
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, 0, self.r, 1)

    def place(self, dobot_manager, zoffset=12, wait=0.5):
        dm = dobot_manager
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, 0, self.r, 1)
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, self.z+zoffset, self.r, 1)
        dm.dType.SetWAITCmdEx(dm.api, wait, 1)
        dm.dType.SetEndEffectorSuctionCupEx(dm.api, 0, 1)
        dm.dType.SetWAITCmdEx(dm.api, wait, 1)
        dm.dType.SetPTPCmdEx(dm.api, 2, self.x,  self.y, 0, self.r, 1)


    @staticmethod
    def deserialize(jsondata):
        c = jsondata["camera"]
        b = jsondata["buffer"]
        s = jsondata["slots"]

        camera = DobotPosition(c["x"], c["y"], c["z"], c["r"])
        buffer = {}
        slot = {}
        for i in b.keys():
            buffer[int(i)] = DobotPosition(b[i]["x"], b[i]["y"], b[i]["z"], b[i]["r"])
        for i in s.keys():
            slot[int(i)] = DobotPosition(s[i]["x"], s[i]["y"], s[i]["z"], s[i]["r"])

        return (camera,buffer,slot)

class DobotManager(object):
    def __init__(self, dType, api):
        self.dType = dType
        self.api = api
        data = None
        with open("calibration.data", "r") as f:
            data = f.read()
        jsondata = json.loads(data)
        self.camera, self.buffer, self.slot = DobotPosition.deserialize(jsondata)
    
    def set_home(self):
        self.dType.SetHOMECmdEx(self.api, 0, 1)