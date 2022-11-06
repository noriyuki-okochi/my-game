#
# Class counter of primitive operation
#
class CmdCounter():
    #
    def __init__(self):
        #
        self.off_counter = None
        self.off_count = 0
        self.cmd_count = 0
    #
    # start to count
    #
    def start(self):
        self.cmd_count = -1
        return
    #
    # disable 
    #
    def off(self, cmdBuffer):
        self.off_counter = len(cmdBuffer)
        return
    #
    # enable
    #
    def on(self, cmdBuffer):
        if self.off_counter != None:
            self.off_count += len(cmdBuffer) - self.off_counter
            self.off_counter = None
        return
    #
    # count-up the effective cmd.
    #  
    def countup(self, cmdBuffer):
        if self.cmd_count == -1:
            self.cmd_count = 0
        else:
            self.cmd_count += len(cmdBuffer) - self.off_count
            self.off_count = 0
        return
    #
    # count-up the invalid cmd. 
    #  
    def offcount(self, count):
        self.off_count += count
        return
    #
    # return the effective cmd-count
    #
    def count(self):
        return  self.cmd_count
#       