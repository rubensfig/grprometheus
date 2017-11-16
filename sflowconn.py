import re
import grpc
import time
from prometheus_handler import Prometheus as Prom
import traceback
import threading

# Define data structure to utilize the statistics, and create a class to
# parse to prometheus

class sflowConnection(threading.Thread):

    def __init__(self, prom):
        threading.Thread.__init__(self)
        self.name = "sflowconnection"

        self.prom = prom
        self.running = True

    def removeAllGarbage(self, lst):
        while True:
            try:
                lst.remove('')
                lst.remove(None)
            except ValueError:
                return lst

    # (.*)\s-\s\d\s\d\s\d:\d\s\d:\d\s\d:\d\s(\w*)\s(.*)|(\S.*?)\s.*?([a-z].*)\s(.*)
    # regex to parse the file
    def parseStats(self, lines):
        regex = '(.*)\s-\s\d\s\d\s\d:\d\s\d:\d\s\d:\d\s(\w*)\s(.*)|(\S.*?)\s.*?([a-z].*)\s(.*)'
        regex = re.compile(regex)
        total = []
        for line in lines:
            parsed = regex.split(line)
            total.append(self.removeAllGarbage(parsed))

        return total

    def printGood(self, lines):
        for line in lines:
            print(line)

    def parseAndGetStats(self, lines):
        stats_array = []
        stats_dict = {  'time' : '',
                        'ifname' : '',
                        'stats_array' : [],                       
                     }
        temp = ''
        stats_dict['time'] = lines[0][0]
        for line in lines:
            temp = line[1].split(" ") 
            if len(temp) == 2:
                if (temp[0] == 'ifName'):
                    stats_dict['ifname'] = temp[1]
                if (temp[0] == 'ifInOctets'):
                    stats_dict['stats_array'].append(temp)
                if (temp[0] == 'ifInUcastPkts'):
                    stats_dict['stats_array'].append(temp)
        return stats_dict

    def __getSflowStats(self):
        fileLocation = '/tmp/sflow'

        startLine =  'startDatagram =================================' 
        endLine =  'endDatagram =================================' 

        found = False
        lines = []
        with open(fileLocation, 'r+') as f:
            for line in f.readlines():
                if startLine in line:
                    found = True
                    continue

                if found:
                    if endLine in line:
                        found = False
                        continue
                    lines.append(line)

            lines = self.parseStats(lines)
            #self.printGood(lines)
            self.clear(f)    
            if lines == []:
                return
            return self.parseAndGetStats(lines)

    
    def clear(self, fstream):
        fstream.seek(0)
        fstream.truncate()

    def exit(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                values = self.__getSflowStats()
                self.prom.addSflowStats(values)
                time.sleep(1)
            except AttributeError:
                time.sleep(10)
                continue
