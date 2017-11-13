import prometheus_client as pc
import urllib2
import time
import threading 
import json
from data_statistics import DataStats

class Prometheus:
    structureStats = {'ibp' : pc.Gauge('in_unicast_pkts_packets', 'InBroadcastPackets', ['nodeid', 'name']),
                      'obp' : pc.Gauge('out_broadcast_packets', 'OutBroadcastPackets', ['nodeid', 'name']),
                      'ioct' : pc.Gauge('in_octets', 'inOctets', ['nodeid','name']),
                      'ooct' : pc.Gauge('out_octets', 'outOctets', ['nodeid','name']),
                      'idis' : pc.Gauge('in_discards', 'InDiscards', ['nodeid','name']),
                      'odis' : pc.Gauge('out_discards', 'OutDiscards', ['nodeid','name'])                 
                    }
    structureTop = { 'nlinks' : pc.Gauge('number_of_links', 'NumberLinks'),
                     'nnodes' : pc.Gauge('number_of_nodes', 'NumberNodes')            
                    }

    def __init__(self):
        self.inBroadPack = 0
        #Prometheus internal things

    def run(self):
        pc.start_http_server(8001)

    def addToStatsList(self, obj):
        state = obj.state 
        self.structureStats['ibp'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_broadcast_pkts)
        self.structureStats['obp'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_unicast_pkts)
        self.structureStats['idis'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_discards)
        self.structureStats['odis'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_discards)
        self.structureStats['ioct'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_octets)
        self.structureStats['ooct'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_octets)


    def addToTopoList(self, obj):
        self.structureTop['nlinks'].set(len(obj.network[0].link))
        self.structureTop['nnodes'].set(len(obj.network[0].node))


    def getValues(self, name, filtr):
        try:
            end_time = int(time.time())
            start_time = int(time.time() - 1*60*1000)
            step = 30
            query= filtr

            url = 'http://172.17.0.3:9090/api/v1/query_range?query={filtr}&start={start}&end={end}&step={step}'
            
            response = urllib2.urlopen(url.format(filtr=query, start=start_time, end=end_time, step=step))
            return json.loads(response.read().decode())

        except:
            pass 
    
class PrometheusThreading(threading.Thread, Prometheus):

    def __init__(self, filtr):
       threading.Thread.__init__(self)
       self.name = "datastats"
       self.filtr = 'in_octets'
       self.stats  = DataStats()
        
    def run(self):
        try:
            for data in self.getValues(self.name, self.filtr)['data']['result']:
                values = []
                nodeID =  data['metric']['nodeid']
                portNO = data['metric']['name']

                for value in data['values']:
                    values.append(value)

                self.stats.addData(self.filtr, nodeID, portNO, values)

            self.stats.graph()

        except TypeError as type:
            print("Exception " + str(type))
            pass
            
    def exit(self):
        threading.currentThread().join(30)
