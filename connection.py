import services_definition_pb2
import services_definition_pb2_grpc as sgrpc
import grpc
import time
from prometheus_handler import Prometheus as Prom
from prometheus_handler import PrometheusThreading as PromT
import traceback
import threading

#Define data structure to utilize the statistics, and create a class to parse to prometheus
class Connection(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "connection"

        self.address = 'bbctrl01.labor:5000'
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
            for obj in self.__getStats().interface:
                if obj.state.counters.in_octets != 0:   
                    self.prom.addToStatsList(obj)
                else:
                    pass 
            time.sleep(1)
    
    def getValues(self):
        promT = PromT('in_octets')
        promT.start()

if __name__ == "__main__":
    conn = Connection()
    conn.run()

