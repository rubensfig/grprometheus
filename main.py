
import services_definition_pb2_grpc as sgrpc
import services_definition_pb2
import grpc
import time
from prometheus_handler import Prometheus as Prom
import traceback

#Define data structure to utilize the statistics, and create a class to parse to prometheus
class Connection:
    
    def __init__(self):
        self.address = '192.168.121.7:5000'

        self.stubStats = sgrpc.NetworkStatisticsStub(grpc.insecure_channel(self.address))
        self.stubTop = sgrpc.NetworkDescriptorStub(grpc.insecure_channel(self.address))

        self.prom = Prom()

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
            for obj in self.__getStats():
                # obj.state.counters.in_broadcast_pkts
                self.prom.addToStatsList(obj)

            self.prom.addToTopoList(self.__getState())

            time.sleep(1)

if __name__ == "__main__":
    conn = Connection()
    conn.run()

