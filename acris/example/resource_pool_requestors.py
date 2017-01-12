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
#        along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import time
from acris import resource_pool as rp
from acris import Threadit
from acris import create_stream_handler
import queue
from datetime import datetime
import logging

logger=logging.getLogger()
handler=create_stream_handler(logging_level=logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MyResource1(rp.Resource): pass
    
class MyResource2(rp.Resource): pass

rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 1, }).load()
   
class Callback(object):
    def __init__(self, notify_queue, name=''):
        self.q=notify_queue
        self.name=name
    def __call__(self,received=False):
        self.q.put(received)
        
requestors=rp.Requestors()

@Threadit()
def worker_callback(name, rps):
    print('[ %s ] %s getting resource' % (str(datetime.now()), name))
    notify_queue=queue.Queue()
    callback=Callback(notify_queue, name=name)
    #print(type(callback))
    #requestor=rp.Requestor(request=rps, callback=callback,audit=False)
    request_id=requestors.reserve(request=rps, callback=callback)

    if requestors.is_reserved(request_id):
        resources=requestors.get(request_id)
    else:
        print('[ %s ] %s doing work before resource available' % (str(datetime.now()), name,))
        arrived_request_id=notify_queue.get()
        print('[ %s ] %s arrived request Id: %s for request id %s' %(str(datetime.now()), name, request_id, request_id))
        resources=requestors.get(request_id)

    print('[ %s ] %s doing work (%s)' % (str(datetime.now()), name, repr(resources)))
    time.sleep(1)
    print('[ %s ] %s returning (%s)' % (str(datetime.now()), name, repr(resources)))
    requestors.put(*resources)

r2=worker_callback('>>> w21-callback', [(rp1,1), (rp2,1)])    
r1=worker_callback('>>> w11-callback', [(rp1,1),])    
r3=worker_callback('>>> w22-callback', [(rp1,1), (rp2,1)])    
r4=worker_callback('>>> w12-callback', [(rp1,1),]) 
