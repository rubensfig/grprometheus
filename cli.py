from connection import Connection
class CLI(object):

    def __init__(self):
        while True:
            user_input = input("Please enter command (or help): ")
            self.command_choice(user_input)
        conn = Connection()
        conn.run()
    # __init__

    def command_choice(self, argument):
        switcher = {
            'd': self.displayValues,
            'help': self.display_help,
            'h': self.display_help,
        }
        print(switcher)
        return switcher.get(argument, self.default())
    # command_choice

    def default(self, ):
        print("command not recognised, please use 'h' for help")
    # default

    def display_help(self):
        print("d    - display values")
    # display_help
    
    def displayValues(self):
        print "hello"

    def get_input(self, message):
        user_input = input(message)
        return user_input
    # get_input
# CLI
