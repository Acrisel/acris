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


from acris import threaded, RetriveAsycValue
from time import sleep

class ThreadedExample(object):
    def proc(self, *args, **kwargs):
        print("starting proc_td")
        t=self.proc_td(*args, **kwargs)
        return t
    
    @threaded
    def proc_td(self, id_, num, stall):
        s=num
        while num > 0:
            print("%s: %s" % (id_, s))
            num -= 1
            s += stall
            sleep(stall)
        print("%s: %s" % (id_, s))  
        return s
 
if __name__ == '__main__':
    
    print("starting workers")
    te1=ThreadedExample().proc('TE1', 3, 1)
    te2=ThreadedExample().proc('TE2', 3, 1)
    
    print("collecting results")
    te1_callback=RetriveAsycValue('te1')
    te1.addCallback(te1_callback)
    te2_callback=RetriveAsycValue('te2')
    te2.addCallback(te2_callback)
    
    
    print('joining t1')
    te1.join()
    print('joined t1')
    print('%s callback result: %s' % (te1_callback.name, te1_callback.result))
    result=te1.syncResult()
    print('te1 syncResult : %s' %result)
    
    result=te2.syncResult()
    print('te2 syncResult : %s' % result)
    te2.join()
    print('%s callback result: %s' % (te2_callback.name, te2_callback.result))
    
    
            
    
    
    