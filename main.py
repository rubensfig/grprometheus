import services_definition_pb2_grpc as sgrpc
import services_definition_pb2
import grpc
import time
from prometheus_handler import Prometheus as Prom
import traceback
from data_statistics import DataStats

#Define data structure to utilize the statistics, and create a class to parse to prometheus
class Connection:
    
    def __init__(self):
        self.address = 'bbctrl01.labor:5000'
        self.stubStats = sgrpc.NetworkStatisticsStub(grpc.insecure_channel(self.address))
        self.stubTop = sgrpc.NetworkDescriptorStub(grpc.insecure_channel(self.address))

        self.prom = Prom()
        self.stats = DataStats()

    def __getState(self):
        try:
            return self.stubTop.GetTopology(services_definition_pb2.Empty())
        except BaseException:
            print "Unexpected error:", traceback.format_exc()

    def __getStats(self):
        try:
            return self.stubStats.GetStatistics(services_definition_pb2.Empty())
        except BaseException:
            print "Unexpected error:", traceback.format_exc()
    
    def run(self):
        self.prom.run()
        while True:
            for obj in self.__getStats().interface:
                if obj.state.counters.in_octets != 0:   
                    self.prom.addToStatsList(obj)
                    self.stats.addPackets(obj.name, obj.state.name, obj.state.counters.in_octets)
                else:
                    pass 

            self.stats.addFlow(self.__getState().network[0])
            time.sleep(1)
                       

if __name__ == "__main__":
    conn = Connection()
    conn.run()

