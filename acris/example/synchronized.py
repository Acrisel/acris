'''
Created on Dec 9, 2016

@author: arnon
'''

from acris.threaded import threaded
from acris.synchronized import dont_synchronize, SynchronizeAll
import threading
import random
import time

# To use for a method:
class C(SynchronizeAll):
    def __init__(self):
        self.data = 2
        self.names = list()
        
    @dont_synchronize
    def __repr__(self):
        return "%s" % (self.names)
        
    def m(self, name, value):
        self.data += value
        self.names.append((name, self.data))
    
    
    def f(self): 
        #time.sleep(random.random())
        self.m('f', 2)

    def g(self): 
        #time.sleep(random.random())
        self.m('g', 3)

for _ in range(10):
    c=C()
    t1=threading.Thread(target=c.f)
    t2=threading.Thread(target=c.g)
    t3=threading.Thread(target=c.f)
    t4=threading.Thread(target=c.g)
    ts=[t1,t2,t3,t4]
    
    for t in ts:
        t.start()
        
    for t in ts:
        t.join()
    print(c)
