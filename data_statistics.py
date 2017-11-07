import matplotlib.pyplot as mp
import numpy as np

class DataStats:

    def __init__(self):
        self.packetSizeBySwitch = {}
        self.switch1 = []
        self.switch2 = []
        self.diffSwitch1 = []
        self.packetsPerPort = { 'S2902c454449f4c55' : [], 'S2902002590b21ace' : []}

    def addPackets(self, switchname, portname, packetsize):
        if "ace" in switchname:
            self.switch1.append(packetsize)
        else:
            self.switch2.append(packetsize)
        
        if portname not in self.packetsPerPort[switchname]:
            self.packetsPerPort[switchname].append([portname, packetsize])

    def addFlow(self, topology):
        for value in topology.link:
            value
