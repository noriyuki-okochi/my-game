import time
#
# Class mesuring lap-time
#
class LapTime():
    #
    def __init__(self):
        #
        self.start_time = None
        self.elapsed_time = 0.0
        self.lap_time = 0.0
        self.intv_time = 0
    #
    # clear lap-time
    #
    def clear(self):
        self.start_time = None
        self.lap_time = 0.0
        return
    #
    # check if measuring
    #
    def enabled(self):
        return self.start_time != None
    #
    # start to  measure
    # 
    def start(self):
        self.lap_time = 0.0
        self.start_time = time.time()
        return
    #
    # puse to mesure
    #
    def pause(self):
        if self.start_time != None:
            self.elapsed_time = time.time() - self.start_time
            self.lap_time += self.elapsed_time
            self.start_time = None
            self.elapsed_time = 0.0
        return
    #
    # restart to meaure
    #
    def restart(self):
        self.start_time = time.time()
        return
    #
    # return the caluclated lap-time
    #
    def laptime(self):
        if self.start_time != None:
            self.elapsed_time = time.time() - self.start_time
        else:
            self.elapsed_time = 0.0
        return  self.lap_time + self.elapsed_time
    # 
    # return formated lap-time('HH:MM:SS')
    #
    def strlaptime(self):
        time = int(self.laptime())
        h = int(time/3600)
        m = int((time%3600)/60)
        s = int((time%3600)%60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    #
    # check if it is interval-time now
    #
    def interval(self, intval):
        if self.start_time == None:
            bret = False
        else:
            now = int(time.time())
            if now - self.intv_time >= intval:
                self.intv_time = now
                bret = True
            else:
                bret = False
        return bret
#       