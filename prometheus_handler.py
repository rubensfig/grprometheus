import prometheus_client as pc

class Prometheus:
    structure = {'ibp' : pc.Gauge('in_broadcast_packets', 'InBroadcastPackets', ['nodeid', 'name']),
                 'obp' : pc.Gauge('out_broadcast_packets', 'OutBroadcastPackets', ['nodeid', 'name']),
                 'ioct' : pc.Gauge('in_octets', 'inOctets', ['nodeid','name']),
                 'idis' : pc.Gauge('in_discards', 'InDiscards', ['nodeid','name']),
                 'odis' : pc.Gauge('out_discards', 'OutDiscards', ['nodeid','name'])                 
                }

    def __init__(self):
        self.inBroadPack = 0
        
        #Prometheus internal things

    def run(self):
        pc.start_http_server(8001)

    def addToList(self, obj):
        state = obj.state 
        self.structure['ibp'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_broadcast_pkts)
        self.structure['obp'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_broadcast_pkts)
        self.structure['idis'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_discards)
        self.structure['odis'].labels(nodeid=obj.name, name=state.name).set(state.counters.out_discards)
        self.structure['ioct'].labels(nodeid=obj.name, name=state.name).set(state.counters.in_octets)
