import services_definition_pb2
import services_definition_pb2_grpc as sgrpc
import grpc
import time
from prometheus_handler import Prometheus as Prom
import traceback
import threading

# Define data structure to utilize the statistics, and create a class to
# parse to prometheus


class Connection(threading.Thread):

    def __init__(self, prom):
        threading.Thread.__init__(self)
        self.name = "connection"

        self.prom = prom
        self.running = True

        self.address = 'bbctrl01.labor:5000'
        self.stubStats = sgrpc.NetworkStatisticsStub(
            grpc.insecure_channel(self.address))
        self.stubTop = sgrpc.NetworkDescriptorStub(
            grpc.insecure_channel(self.address))

    def __getState(self):
        try:
            return self.stubTop.GetTopology(services_definition_pb2.Empty())
        except BaseException:
            print("Unexpected error:", traceback.format_exc())
            return
        except AttributeError:
            print("Unexpected error:", traceback.format_exc())
            return

    def __getStats(self):
        try:
            return self.stubStats.GetStatistics(
                services_definition_pb2.Empty())
        except BaseException:
            print("Unexpected error:", traceback.format_exc())
            return
        except AttributeError:
            print("Unexpected error:", traceback.format_exc())
            return

    def exit(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                stats = self.__getStats()
                for obj in stats.interface:
                    if obj.state.counters.in_octets != 0:
                        self.prom.addToStatsList(obj)
                    else:
                        pass
                time.sleep(1)
            except AttributeError:
                print("\nATTENTION: SERVER PROBS OFF\n")
                time.sleep(10)
                continue


if __name__ == "__main__":
    conn = Connection()
    conn.run()
