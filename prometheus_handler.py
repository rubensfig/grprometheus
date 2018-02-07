import prometheus_client as pc
import urllib.request
import urllib.error
import urllib.parse
import time
import threading
import traceback
import json
from data_statistics import DataStats
import sys

class Prometheus:
    structureStats = {'ibp': pc.Gauge('in_unicast_pkts_packets', 'InBroadcastPackets', ['nodeid', 'name']),
                      'obp': pc.Gauge('out_broadcast_packets', 'OutBroadcastPackets', ['nodeid', 'name']),
                      'ioct': pc.Gauge('in_octets', 'inOctets', ['nodeid', 'name']),
                      'ooct': pc.Gauge('out_octets', 'outOctets', ['nodeid', 'name']),
                      'idis': pc.Gauge('in_discards', 'InDiscards', ['nodeid', 'name']),
                      'odis': pc.Gauge('out_discards', 'OutDiscards', ['nodeid', 'name'])
                      }

    structureTop = {'nlinks': pc.Gauge('number_of_links', 'NumberLinks'),
                    'nnodes': pc.Gauge('number_of_nodes', 'NumberNodes')
                    }

    flood_flow_count = pc.Gauge('flow_count', 'FlowCount', ['switch'])

    ovsStats = { 'ioct' : pc.Gauge('ovs_in_unicast_pkts', 'OVS_InUnicast', ['nodeid', 'name']),
                 'rpkt' : pc.Gauge('ovs_received_packets', 'OVS_InPackets', ['nodeid', 'name']),
                 'tpkt' : pc.Gauge('ovs_transmitted_packets', 'OVS_OutPackets', ['nodeid', 'name']),
                 'rbytes' : pc.Gauge('ovs_received_bytes', 'OVS_InBytes', ['nodeid', 'name']),
                 'tbytes' : pc.Gauge('ovs_transmitted_bytes', 'OVS_OutBytes', ['nodeid', 'name']),
                 'rerr' : pc.Gauge('ovs_received_errors', 'OVS_InErrors', ['nodeid', 'name']),
                 'terr' : pc.Gauge('ovs_transmitted_errors', 'OVS_OutErrors', ['nodeid', 'name']),
                 'ipsrc' : pc.Gauge('ovs_ip_src_flows', 'OVS_IPSrcFlows', ['name']),
                 'ipdst' : pc.Gauge('ovs_ip_dst_flows', 'OVS_IPDstFlows', ['name']),
                 'bdwth' : pc.Gauge('bandwidth', 'OVS_Bandwidth', ['name']),
                }

    def __init__(self):
        pass

    def addFlowCount(self, mac_add, flow_count):
        self.flood_flow_count.labels(mac_add).set(flow_count)

    def execute(self): 
        print("starting Prometheus : PORT 8001")
        pc.start_http_server(8001)

    def addToStatsList(self, obj):
        state = obj.state
        self.structureStats['ibp'].labels(
            nodeid=obj.name, name=state.name).set(
            state.counters.in_broadcast_pkts)
        self.structureStats['obp'].labels(
            nodeid=obj.name, name=state.name).set(
            state.counters.out_unicast_pkts)
        self.structureStats['idis'].labels(
            nodeid=obj.name, name=state.name).set(
            state.counters.in_discards)
        self.structureStats['odis'].labels(
            nodeid=obj.name, name=state.name).set(
            state.counters.out_discards)
        self.structureStats['ioct'].labels(
            nodeid=obj.name, name=state.name).set(
            state.counters.in_octets)
        self.structureStats['ooct'].labels(
            nodeid=obj.name, name=state.name).set(
            state.counters.out_octets)

    def addOvsIpFlows(self, flows):
        src = flows[0]
        dst = flows[1]

        for item, values in src.items():
            self.ovsStats['ipsrc'].labels(name=item).set(values)

        for item, values in dst.items():
            self.ovsStats['ipdst'].labels(name=item).set(values)

    def addBandwidth(self, bps, portno):
        self.ovsStats['bdwth'].labels(
            nodeid=i, name=portno).set(
            bps)

    def addToOVSList(self, stats):
        dont_pass = ['local']
        switches = list(stats.keys())
        for i in stats:
            total = stats.get(i)
            try:
                print("Normal Exec")
                port_stats =  list(stats.get(i)['port_reply'][0]['port'])
            except:
                print("No Response")
                continue

            for stat in port_stats:
                if stat['port_number'] in dont_pass:
                    continue
                # try:
                self.ovsStats['rpkt'].labels(
                    nodeid=i, name=stat['port_number']).set(
                    stat.get('receive_packets'))
                self.ovsStats['tpkt'].labels(
                    nodeid=i, name=stat['port_number']).set(
                    stat.get('transmit_packets'))

                self.ovsStats['rbytes'].labels(
                    nodeid=i, name=stat['port_number']).set(
                    stat.get('receive_bytes'))
                self.ovsStats['tbytes'].labels(
                    nodeid=i, name=stat['port_number']).set(
                    stat.get('transmit_bytes'))

                self.ovsStats['terr'].labels(
                    nodeid=i, name=stat['port_number']).set(
                    stat.get('transmit_errors'))
                self.ovsStats['rerr'].labels(
                    nodeid=i, name=stat['port_number']).set(
                    stat.get('receive_errors'))
            #     except KeyError:
                    # print("Error", stat.keys())
               #      continue
        # self.ovsStats['ioct'].labels(
            # ).set(
            # state.counters.in_broadcast_pkts)

    def addToTopoList(self, obj):
        self.structureTop['nlinks'].set(len(obj.network[0].link))
        self.structureTop['nnodes'].set(len(obj.network[0].node))

class PrometheusThreading(threading.Thread):

    def __init__(self, filtr, portno, links):
        threading.Thread.__init__(self)
        self.name = "datastats"
        self.filtr = filtr
        self.portno = portno
        self.stats = DataStats()
        self.links = links

    def getValues(self, filtr):
        try:
            end_time = int(time.time())
            start_time = int(time.time() - 1 * 60 * 1000)
            step = 30
            query = filtr

            url = 'http://172.17.0.2:9090/api/v1/query_range?query={filtr}&start={start}&end={end}&step={step}'

            response = urllib.request.urlopen(
                url.format(
                    filtr=query,
                    start=start_time,
                    end=end_time,
                    step=step),
                timeout=2)
            return json.loads(response.read().decode())

        except IOError as type:
            print("getValues " + "Exception " + str(type))
            return -1

    def listStats(self, filtr):
        try:
            for data in self.getValues('in_errors')['data']['result']:
                if not data:
                    return -1
                values = []
                nodeID = data['metric']['nodeid']
                portNO = data['metric']['name']
                print(self.filtr, nodeID, portNO)
            return 0
        except TypeError as type:
            print("run " + "Exception " + 'TypeError')
            return -1

    def run(self):
        try:
            for data in self.getValues(self.filtr)['data']['result']:
                if not data:
                    return -1
                values = []
                nodeID = data['metric']['nodeid']
                portNO = data['metric']['name']

                for value in data['values']:
                    values.append(value)

                self.stats.addData(self.filtr, nodeID, portNO, values)

            self.stats.graph(self.portno)
            return 0
        except TypeError as type:
            print("run " + "Exception " + 'TypeError')
            return -1
