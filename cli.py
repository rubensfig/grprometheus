from connection import Connection
from sflowconn import sflowConnection
from prometheus_handler import PrometheusThreading as PromT
from prometheus_handler import Prometheus as Prom
import sys
import threading


class CLI(object):

    def __init__(self):
        self.prom = Prom()
        self.conn = Connection(self.prom)
        self.sfconn = sflowConnection(self.prom)

        self.conn.start()
        self.prom.execute()
        self.sfconn.start()

        user_input = ''
        while user_input != 'e':
            try:
                user_input = self.get_input("Please enter command (or help): ")
                self.command_choice(user_input)
                # print(threading.enumerate())
            except KeyboardInterrupt:
                sys.exit()
    # __init__

    def command_choice(self, argument):
        switcher = {
            'h': self.display_help,
            'd': self.displayValues,
            'l': self.listStats,
            'help': self.display_help,
            'e': self.exit
        }
        switcher[argument]()

    # command_choice

    def default(self, ):
        print("command not recognised, please use 'h' for help")
    # default

    def display_help(self):
        print("d    - display values")
    # display_help

    def displayValues(self):
        print("Graphing  values")

        promT = PromT(
            self.get_input('Statistics to monitor : '),
            self.get_input('Port No : '),
            self.conn.GetTopology()
            )
        if promT.start() == -1:
            print("DUNNO")
        promT.join()

    def listStats(self):
        promT = PromT(None, None, self.conn.GetTopology())
        promT.listStats('in_octets')

    def get_input(self, message):
        user_input = input(message)
        return user_input

    def exit(self):
        self.conn.exit()
        self.sfconn.exit()
    # get_input
# CLI
