'''
Created on Dec 9, 2016

@author: arnon
'''
import time
from acris import resource_pool as rp
from acris import threaded

class MyResource(rp.Resource):
    pass

rp1=rp.ResourcePool('RP1', resource_cls=MyResource, policy={'resource_limit': 2, }).load()                   
rp2=rp.ResourcePool('RP2', resource_cls=MyResource, policy={'resource_limit': 1, }).load()

@threaded
def worker(name, rp):
    print('%s getting resource' % name)
    r=rp.get()
    print('%s doing work (%s)' % (name, repr(r)))
    time.sleep(4)
    print('%s returning %s' % (name, repr(r)))
    rp.put(*r)

print("Starting workers")
r1=worker('w11', rp1)    
r2=worker('w21', rp2)    
r3=worker('w22', rp2)    
r4=worker('w12', rp1) 

