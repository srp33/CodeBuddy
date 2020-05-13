import sys
import time

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.file_name = "/tmp/access_{}.log".format(time.strftime("%Y%m%d-%H%M%S"))
        self.log = open(self.file_name, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass
