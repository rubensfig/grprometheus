import matplotlib.pyplot as mp
import numpy as np
import pandas as pd
import time

class DataStats:

    def __init__(self):
        self.filtr = ''
        self.values = {}
        self.switch1 = 'S2902002590b21ace'
        self.switch2 = 'S2902c454449f4c55'

    def __valuesToInt(self,values):
        first_value = values[0][0]
        for value in values:
            value[0] = (value[0] - first_value)/1000*60
            value[1] =  int(value[1])
        return values
         
    def addData(self, filtr, nodeID, portNO, values):
        #self.values.append([nodeID, portNO, pd.DataFrame(values)])
        self.values.setdefault(nodeID, [])#pd.DataFrame(values)
        self.__valuesToInt(values)
        self.values[nodeID].append({'portno' : portNO,  'values' : pd.DataFrame(values, columns=['time', 'values']) })  
    
    def graph(self):
        try:
            portno = '49'
            data1 = ''
            data2 = ''
            for datapnts in self.values:
                if portno not in datapnts[self.switch1]['portno'] or portno not in datapnts[self.switch2]['portno']:
                     continue
                else:
                     data1 = datapnts[self.switch1]['values']
                     data2 = datapnts[self.switch2]['values']
            print(data1.describe()) 
            print(data2.describe()) 

            ax = toplt.plot( x='time', y = 'values')
            toplt = data2
            toplt.plot(ax=ax, x='time', y = 'values')
            #mp.figure(); 

            mp.show()
            return
        except:
            print("Nothing to do")
