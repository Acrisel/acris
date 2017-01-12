# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from acris import dont_synchronize, SynchronizeAll
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
