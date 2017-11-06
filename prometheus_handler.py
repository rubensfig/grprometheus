import prometheus_client as pc

class Prometheus:
    structureStats = {'ibp' : pc.Gauge('in_broadcast_packets', 'InBroadcastPackets', ['nodeid', 'name']),
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
        self.structureStats['obp'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_broadcast_pkts)
        self.structureStats['idis'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_discards)
        self.structureStats['odis'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_discards)
        self.structureStats['ioct'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_octets)
        self.structureStats['ooct'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_octets)


    def addToTopoList(self, obj):
        self.structureTop['nlinks'].set(len(obj.network[0].link))
        self.structureTop['nnodes'].set(len(obj.network[0].node))
