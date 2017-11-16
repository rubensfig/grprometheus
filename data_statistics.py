import matplotlib.pyplot as mp
import numpy as np
import pandas as pd
import time

class DataStats:

    def __init__(self):
        self.filtr = ''
        self.values = {}
        self.switch1 = 'S290200182330dff6'
        self.switch2 = 'S290200182330dea2'
        self.link_agg = []

    def __valuesToInt(self, values):
        first_value = values[0][0]
        for value in values:
            value[0] = (value[0] - first_value) / 1000 * 60
            value[1] = int(value[1])
        return values

    def addData(self, filtr, nodeID, portNO, values):
        # self.values.append([nodeID, portNO, pd.DataFrame(values)])
        self.values.setdefault(nodeID, [])  # pd.DataFrame(values)
        self.__valuesToInt(values)
        self.values[nodeID].append(
            {'portno': portNO, 'values': pd.DataFrame(values, columns=['time', 'values'])})

    def linkAgg(self, link_info):
        temp = {}

        node_src = link_info['node_src']
        port_src = link_info['port_src']
        node_dst = link_info['node_src']
        port_dst = link_info['port_src']

        self.values[link_info['node_src']]
        temp.setdefault(link_info)

    def graph(self, portno):
        data1 = ''
        data2 = ''

        try:
            for datapnts in self.values[self.switch1]:
                if portno not in datapnts['portno']:
                    continue
                else:
                    data1 = datapnts['values']

            print(data1.describe())
            toplt = data1


        except KeyError:
            print("No datapoints found")
            pass

        try:
            for datapnts in self.values[self.switch2]:
                if portno not in datapnts['portno']:
                    continue
                else:
                    data2 = datapnts['values']
            print(data2.describe())
            toplt = data1

            ax = toplt.plot(x='time', y='values')
            toplt = data2
            toplt.plot(ax=ax, x='time', y='values')
            # mp.figure();

            mp.show()
            return
        except KeyError:
            print("No datapoints found")
