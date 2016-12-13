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

import time
from acris import resource_pool as rp
from acris import threaded
import queue
from datetime import datetime
from acris.decorated_class import traced_method

traced=traced_method(print, True)

class MyResource1(rp.Resource): pass
    
class MyResource2(rp.Resource): pass

rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 1, }).load()
   
class Callback(object):
    def __init__(self, notify_queue):
        self.q=notify_queue
    @traced
    def __call__(self, ticket=None):
        self.q.put(ticket)

@threaded
def worker_callback(name, rp):
    print('[ %s ] %s getting resource' % (str(datetime.now()), name))
    notify_queue=queue.Queue()
    callback=Callback(notify_queue)
    r=rp.get(callback=callback)

    if not r:
        print('[ %s ] %s doing work before resource available' % (str(datetime.now()), name,))
        print('[ %s ] %s waiting for resources' % (str(datetime.now()), name,))
        ticket=notify_queue.get()
        r=rp.get(ticket=ticket)
    
    print('[ %s ] %s doing work (%s)' % (str(datetime.now()), name, repr(r)))
    time.sleep(2)
    print('[ %s ] %s returning (%s)' % (str(datetime.now()), name, repr(r)))
    rp.put(*r)

r1=worker_callback('>>> w11-callback', rp1)    
r2=worker_callback('>>> w21-callback', rp2)    
r3=worker_callback('>>> w22-callback', rp2)    
r4=worker_callback('>>> w12-callback', rp1) 
