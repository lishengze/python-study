# -*- coding: UTF-8 -*-

import threading, time

class Hider(threading.Thread):
    def __init__(self, cond, name):
        super(Hider, self).__init__()
        self.cond = cond
        self.name = name
    
    def run(self):
        time.sleep(1) 
        print self.name + " is my name! "
        self.cond.acquire() #b    
        print self.name + " I've closed my eyes!"
        self.cond.notify()
        self.cond.wait() #c    
                         #f 
        print self.name + ': I find you ~_~'
        self.cond.notify()
        self.cond.release()
                            #g
        print self.name + ': I win! '   #h
        
class Seeker(threading.Thread):
    def __init__(self, cond, name):
        super(Seeker, self).__init__()
        self.cond = cond
        self.name = name
    def run(self):
        print self.name + " is my name! "
        self.cond.acquire()
        self.cond.wait()    #a   
                            #d
        print self.name + " I've hidden perfectly! "
        self.cond.notify()
        self.cond.wait()    #e
                            #h
        self.cond.release() 
        print self.name + ': Oh , found by you! ~~~'
        
t = threading.Thread()        
cond = threading.Condition()
seeker = Seeker(cond, 'seeker')
hider = Hider(cond, 'hider')
seeker.start()
hider.start()