=======
acris
=======

Overview
========

    **acris** is a python library providing useful programming patterns.

threaded
========

    decorator for methods that can be executed as a thread.  

example
-------

    .. code-block:: python

        from acris import threaded
        from time import sleep

        class ThreadedExample(object):
            @threaded
            def proc(self, id_, num, stall):
                s=num
                while num > 0:
                    print("%s: %s" % (id_, s))
                    num -= 1
                    s += stall
                    sleep(stall)
                print("%s: %s" % (id_, s))  
                return s
          
        class RetVal(object):
            def __init__(self, name):
                self.name=name
        
            def __call__(self, retval):
                print(self.name, ':', retval)  

          
example output
--------------

    .. code-block:: python

        te1=ThreadedExample().proc(1, 3, 1)
        te2=ThreadedExample().proc(2, 3, 5)
    
        te1.addCallback(RetVal('te1'))
        te2.addCallback(RetVal('te2'))

    will produce:

    .. code-block:: python

        1: 3
        2: 3
        1: 4
        1: 5
        1: 6
        te1 : 6
        2: 8
        2: 13
        2: 18
        te2 : 18

Singleton and NamedSingleton
============================

    meta class that creates singleton footprint of classes inheriting from it.

Singleton example
-----------------

    .. code-block:: python

        from acris import Singleton

        class Sequence(Singleton):
            step_id=0
    
            def __call__(self):
                step_id=self.step_id
                self.step_id += 1
                return step_id  

example output
--------------

    .. code-block:: python
 
        A=Sequence()
        print('A', A())
        print('A', A())
        B=Sequence()
        print('B', B()) 

    will produce:

    .. code-block:: python

        A 0
        A 1
        B 2
    
NamedSingleton example
-----------------

    .. code-block:: python

        from acris import Singleton

        class Sequence(NamedSingleton):
            step_id=0
            
            def __init__(self, name=''):
                self.name=name
    
            def __call__(self,):
                step_id=self.step_id
                self.step_id += 1
                return step_id  

example output
--------------

    .. code-block:: python
 
        A=Sequence('A')
        print(A.name, A())
        print(A.name, A())
        B=Sequence('B')
        print(B.name, B()) 

    will produce:

    .. code-block:: python

        A 0
        A 1
        B 0
    
Sequence
========

    meta class to produce sequences.  Sequence allows creating different sequences using name tags.

example
-------

    .. code-block:: python

        from acris import Sequence

        A=Sequence('A')
        print('A', A())
        print('A', A())
        B=Sequence('B')
        print('B', B()) 
    
        A=Sequence('A')
        print('A', A())
        print('A', A())
        B=Sequence('B')
        print('B', B()) 

example output
--------------

    .. code-block:: python
     
        A 0
        A 1
        B 0
        A 2
        A 3
        B 1

TimedSizedRotatingHandler
=========================
	
    Use TimedSizedRotatingHandler is combining TimedRotatingFileHandler with RotatingFileHandler.  
    Usage as handler with logging is as defined in Python's logging how-to
	
example
-------

    .. code-block:: python
	
        import logging
	
        # create logger
        logger = logging.getLogger('simple_example')
        logger.setLevel(logging.DEBUG)
	
        # create console handler and set level to debug
        ch = logging.TimedRotatingFileHandler()
        ch.setLevel(logging.DEBUG)
	
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
        # add formatter to ch
        ch.setFormatter(formatter)
	
        # add ch to logger
        logger.addHandler(ch)
	
        # 'application' code
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')	

MpLogger and LevelBasedFormatter
================================

    Multiprocessor logger using QueueListener and QueueHandler
    It uses TimedSizedRotatingHandler as its logging handler

    It also uses acris provided LevelBasedFormatter which facilitate message formats
    based on record level.  LevelBasedFormatter inherent from logging.Formatter and
    can be used as such in customized logging handlers. 
	
example
-------

Within main process
```````````````````

    .. code-block:: python
	
        import logging
        import time

        logger=logging.getLogger(__name__)

        level_formats={logging.DEBUG:"[ %(asctime)s ][ %(levelname)s ][ %(message)s ][ %(module)s.%(funcName)s.%(lineno)d ]",
                        'default':   "[ %(asctime)s ][ %(levelname)s ][ %(message)s ]",
                        }


        mplogger=MpLogger(logging_level=logging.DEBUG, level_formats=level_formats)
        mplogger.start()

        logger.debug("starting sub processes")
        # running processes
        logger.debug("joining sub processes")

        mplogger.stop()
	
Within individual process
`````````````````````````
    .. code-block:: python
	
        import logging
	
        logger=logging.getLogger(__name__)
        logger.debug("logging from sub process")
    
Example output
--------------

    .. code-block:: python

        [ 2016-12-06 13:39:56,196 ][ DEBUG ][ starting sub processes ][ mptest.<module>.178 ]
        [ 2016-12-06 13:39:56,630 ][ INFO ][ proc [2663]: 0/1 - sleep 0.42sec ]
        [ 2016-12-06 13:39:56,802 ][ INFO ][ proc [2664]: 0/1 - sleep  0.6sec ]
        [ 2016-12-06 13:39:56,805 ][ DEBUG ][ sub processes completed ][ mptest.<module>.189 ]
	
Data Types
==========

    varies derivative of Python data types

MergeChainedDict
----------------

    Similar to ChainedDict, but merged the keys and is actually derivative of dict.

    .. code-block:: python

        a={1:11, 2:22}
        b={3:33, 4:44}
        c={1:55, 4:66}
        d=MergedChainedDict(c, b, a)
        print(d) 

    Will output:

    .. code-block:: python

    	{1: 55, 2: 22, 3: 33, 4: 66}

ResourcePool
============

     Resource pool provides program with interface to manager resource pools.  This is used as means to 
     funnel processing.  
     
     ResourcePoolRequestor object can be used to request resource set resides in multiple pools.
     
Sync Example
------------

    .. code-block:: python

        import time
        from acris import resource_pool as rp
        from acris import threaded
        import queue
        from datetime import datetime

        class MyResource1(rp.Resource): pass

        class MyResource2(rp.Resource): pass

        rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
        rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 1, }).load()

        @threaded
        def worker_awaiting(name, rp):
            print('[ %s ] %s getting resource' % (str(datetime.now()), name ) )
            r=rp.get()
            print('[ %s ] %s doing work (%s)' % (str(datetime.now()), name, repr(r)))
            time.sleep(4)
            print('[ %s ] %s returning %s' % (str(datetime.now()), name, repr(r)))
            rp.put(*r)
    

        r1=worker_awaiting('>>> w11-direct', rp1)    
        r2=worker_awaiting('>>> w21-direct', rp2)    
        r3=worker_awaiting('>>> w22-direct', rp2)    
        r4=worker_awaiting('>>> w12-direct', rp1)   
              
Sync Example Output
-------------------

    .. code-block:: python

        [ 2016-12-11 13:06:14.659569 ] >>> w11-direct getting resource
        [ 2016-12-11 13:06:14.659640 ] >>> w11-direct doing work ([Resource(name:MyResource1)])
        [ 2016-12-11 13:06:14.659801 ] >>> w21-direct getting resource
        [ 2016-12-11 13:06:14.659834 ] >>> w21-direct doing work ([Resource(name:MyResource2)])
        [ 2016-12-11 13:06:14.659973 ] >>> w22-direct getting resource
        [ 2016-12-11 13:06:14.660190 ] >>> w12-direct getting resource
        [ 2016-12-11 13:06:14.660260 ] >>> w12-direct doing work ([Resource(name:MyResource1)])
        [ 2016-12-11 13:06:18.662362 ] >>> w11-direct returning [Resource(name:MyResource1)]
        [ 2016-12-11 13:06:18.662653 ] >>> w21-direct returning [Resource(name:MyResource2)]
        [ 2016-12-11 13:06:18.662826 ] >>> w12-direct returning [Resource(name:MyResource1)]
        [ 2016-12-11 13:06:18.662998 ] >>> w22-direct doing work ([Resource(name:MyResource2)])
        [ 2016-12-11 13:06:22.667149 ] >>> w22-direct returning [Resource(name:MyResource2)]
        
Async Example
-------------

    .. code-block:: python

        import time
        from acris import resource_pool as rp
        from acris import threaded
        import queue
        from datetime import datetime

        class MyResource1(rp.Resource): pass
    
        class MyResource2(rp.Resource): pass

        rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
        rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 1, }).load()
   
        class Callback(object):
            def __init__(self, notify_queue):
                self.q=notify_queue
            def __call__(self,resources=None):
                self.q.put(resources)

        @threaded
        def worker_callback(name, rp):
            print('[ %s ] %s getting resource' % (str(datetime.now()), name))
            notify_queue=queue.Queue()
            r=rp.get(callback=Callback(notify_queue))

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
                     
Async Example Output
--------------------

    .. code-block:: python

        [ 2016-12-11 13:08:24.410447 ] >>> w11-callback getting resource
        [ 2016-12-11 13:08:24.410539 ] >>> w11-callback doing work ([Resource(name:MyResource1)])
        [ 2016-12-11 13:08:24.410682 ] >>> w21-callback getting resource
        [ 2016-12-11 13:08:24.410762 ] >>> w21-callback doing work ([Resource(name:MyResource2)])
        [ 2016-12-11 13:08:24.410945 ] >>> w22-callback getting resource
        [ 2016-12-11 13:08:24.411227 ] >>> w22-callback doing work before resource available
        [ 2016-12-11 13:08:24.411273 ] >>> w12-callback getting resource
        [ 2016-12-11 13:08:24.411334 ] >>> w22-callback waiting for resources
        [ 2016-12-11 13:08:24.411452 ] >>> w12-callback doing work ([Resource(name:MyResource1)])
        [ 2016-12-11 13:08:26.411901 ] >>> w11-callback returning ([Resource(name:MyResource1)])
        [ 2016-12-11 13:08:26.412200 ] >>> w21-callback returning ([Resource(name:MyResource2)])
        [ 2016-12-11 13:08:26.412505 ] >>> w22-callback doing work ([Resource(name:MyResource2)])
        [ 2016-12-11 13:08:26.416130 ] >>> w12-callback returning ([Resource(name:MyResource1)])
        [ 2016-12-11 13:08:28.416001 ] >>> w22-callback returning ([Resource(name:MyResource2)])
        
Requestor Example
-------------

    .. code-block:: python

        import time
        from acris import resource_pool as rp
        from acris import threaded
        import queue
        from datetime import datetime

        class MyResource1(rp.Resource): pass
    
        class MyResource2(rp.Resource): pass

        rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
        rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 2, }).load()
   
        class Callback(object):
            def __init__(self, notify_queue, name=''):
                self.q=notify_queue
                self.name=name
            def __call__(self,resources=None):
                self.q.put(resources)

        @threaded
        def worker_callback(name, rps):
            print('[ %s ] %s getting resource' % (str(datetime.now()), name))
            notify_queue=queue.Queue()
            callback=Callback(notify_queue, name=name)
            r=rp.Requestor(request=rps, callback=callback)

            if r.is_reserved():
                resources=r.get()
            else:
                print('[ %s ] %s doing work before resource available' % (str(datetime.now()), name,))
                print('[ %s ] %s waiting for resources' % (str(datetime.now()), name,))
                notify_queue.get()
                resources=r.get()

            print('[ %s ] %s doing work (%s)' % (str(datetime.now()), name, repr(resources)))
            time.sleep(2)
            print('[ %s ] %s returning (%s)' % (str(datetime.now()), name, repr(resources)))
            r.put(*resources)

        r1=worker_callback('>>> w11-callback', [(rp1,1),])    
        r2=worker_callback('>>> w21-callback', [(rp1,1),(rp2,1)])    
        r3=worker_callback('>>> w22-callback', [(rp1,1),(rp2,1)])    
        r4=worker_callback('>>> w12-callback', [(rp1,1),]) 
                     
Requestor Example Output
--------------------

    .. code-block:: python

        [ 2016-12-13 06:27:54.924629 ] >>> w11-callback getting resource
        [ 2016-12-13 06:27:54.925094 ] >>> w21-callback getting resource
        [ 2016-12-13 06:27:54.925453 ] >>> w22-callback getting resource
        [ 2016-12-13 06:27:54.926188 ] >>> w12-callback getting resource
        [ 2016-12-13 06:27:54.932922 ] >>> w11-callback doing work ([Resource(name:MyResource1)])
        [ 2016-12-13 06:27:54.933709 ] >>> w12-callback doing work ([Resource(name:MyResource1)])
        [ 2016-12-13 06:27:54.938425 ] >>> w22-callback doing work before resource available
        [ 2016-12-13 06:27:54.938548 ] >>> w22-callback waiting for resources
        [ 2016-12-13 06:27:54.939256 ] >>> w21-callback doing work before resource available
        [ 2016-12-13 06:27:54.939267 ] >>> w21-callback waiting for resources
        [ 2016-12-13 06:27:56.936881 ] >>> w11-callback returning ([Resource(name:MyResource1)])
        [ 2016-12-13 06:27:56.937543 ] >>> w12-callback returning ([Resource(name:MyResource1)])
        [ 2016-12-13 06:27:56.947615 ] >>> w22-callback doing work ([Resource(name:MyResource2), Resource(name:MyResource1)])
        [ 2016-12-13 06:27:56.948587 ] >>> w21-callback doing work ([Resource(name:MyResource2), Resource(name:MyResource1)])
        [ 2016-12-13 06:27:58.949812 ] >>> w22-callback returning ([Resource(name:MyResource2), Resource(name:MyResource1)])
        [ 2016-12-13 06:27:58.950064 ] >>> w21-callback returning ([Resource(name:MyResource2), Resource(name:MyResource1)])
        
Mediator
========
    
    Class interface to generator allowing query of has_next()
    
Example 
-------

    .. code-block:: python

        from acris import Mediator

        def yrange(n):
            i = 0
            while i < n:
                yield i
                i += 1

        n=10
        m=Mediator(yrange(n))
        for i in range(n):
            print(i, m.has_next(3), next(m))
        print(i, m.has_next(), next(m))

Example Output
--------------

    .. code-block:: python

        0 True 0
        1 True 1
        2 True 2
        3 True 3
        4 True 4
        5 True 5
        6 True 6
        7 True 7
        8 False 8
        9 False 9
        Traceback (most recent call last):
          File "/private/var/acrisel/sand/acris/acris/acris/example/mediator.py", line 19, in <module>
            print(i, m.has_next(), next(m))
          File "/private/var/acrisel/sand/acris/acris/acris/acris/mediator.py", line 38, in __next__
            value=next(self.generator)
        StopIteration       
        