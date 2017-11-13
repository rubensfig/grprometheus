from connection import Connection
import sys

class CLI(object):

    def __init__(self):
        self.conn = Connection()
        self.conn.start()
        while True:
            try:
                print "\n"
                user_input = self.get_input("Please enter command (or help): ")
                self.command_choice(user_input)
            except KeyboardInterrupt:
                sys.exit(1)
    # __init__

    def command_choice(self, argument):
        switcher = {
            'd': self.displayValues,
            'help': self.display_help,
            'h': self.display_help,
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
        self.conn.getValues()

    def get_input(self, message):
        user_input = raw_input(message)
        return user_input
    # get_input
# CLI
