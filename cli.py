from connection import Connection
from prometheus_handler import PrometheusThreading as PromT
from prometheus_handler import Prometheus as Prom
import sys, threading

class CLI(object):

    def __init__(self):
        self.conn = Connection()
        self.prom = Prom()
        self.conn.start()
        self.prom.execute()

        while True:
            try:
                user_input = self.get_input("Please enter command (or help): ")
                self.command_choice(user_input)
            except KeyboardInterrupt:
                sys.exit()
    # __init__

    def command_choice(self, argument):
        switcher = {
            'd': self.displayValues,
            'help': self.display_help,
            'h': self.display_help
        }
        return switcher.get(argument, self.displayValues())
    # command_choice

    def default(self, ):
        print("command not recognised, please use 'h' for help")
    # default

    def display_help(self):
        print("d    - display values")
    # display_help
    
    def displayValues(self):
        print("Graphing  values")
        promT = PromT('in_octets')
        promT.start()
        promT.join()

    def get_input(self, message):
        user_input = input(message)
        return user_input
    # get_input
# CLI
