
import services_definition_pb2_grpc as sgrpc
import services_definition_pb2
import grpc
import time

#Define data structure to utilize the statistics, and create a class to parse to prometheus
class Connection:
    
    def __init__(self):
        self.address = '192.168.121.253:5000'
        self.stub = sgrpc.NetworkStatisticsStub(grpc.insecure_channel(self.address))


    def __getStats(self):
        return self.stub.GetStatistics(services_definition_pb2.Empty())
    
    def run(self):
        while True:
            time.sleep(2)
            for obj in self.__getStats():
                print obj
if __name__ == "__main__":
    conn = Connection()
    conn.run()

