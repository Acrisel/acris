=====
acris
=====

----------------------------------------
programming idioms and utilities library
----------------------------------------

.. contents:: Table of Contents
   :depth: 2

Overview
========

    **acris** is a python library providing useful programming patterns and tools.
    
    **acris** started as Acrisel's internal idioms and utilities for programmers.
    
    It included:
        1. programming idioms that are repeatedly used by programmers.
        #. utilities that helps programmers and administrators manage their environments
    
    We decided to contribute this library to Python community as a token of appreciation to
    what this community enables us.
    
    We hope that you will find this library useful and helpful as we find it.
    
    If you have comments or insights, please don't hesitate to contact us at support@acrisel.com
    
Programming Idoms
=================

threadit
--------

    decorator for methods that can be executed as a thread.  

example
~~~~~~~

    .. code-block:: python

        from acris import threadit
        from time import sleep

        class ThreadedExample(object):
            @threadit
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
~~~~~~~~~~~~~~

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
----------------------------

    meta class that creates singleton footprint of classes inheriting from it.

Singleton example
~~~~~~~~~~~~~~~~~

    .. code-block:: python

        from acris import Singleton

        class Sequence(Singleton):
            step_id=0
    
            def __call__(self):
                step_id=self.step_id
                self.step_id += 1
                return step_id  

example output
~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~

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
--------

    meta class to produce sequences.  Sequence allows creating different sequences using name tags.

example
~~~~~~~

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
~~~~~~~~~~~~~~

    .. code-block:: python
     
        A 0
        A 1
        B 0
        A 2
        A 3
        B 1

TimedSizedRotatingHandler
-------------------------
	
    Use TimedSizedRotatingHandler is combining TimedRotatingFileHandler with RotatingFileHandler.  
    Usage as handler with logging is as defined in Python's logging how-to
	
example
~~~~~~~

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
--------------------------------

    Multiprocessor logger using QueueListener and QueueHandler
    It uses TimedSizedRotatingHandler as its logging handler

    It also uses acris provided LevelBasedFormatter which facilitate message formats
    based on record level.  LevelBasedFormatter inherent from logging.Formatter and
    can be used as such in customized logging handlers. 
	
example
~~~~~~~

Within main process
```````````````````

    .. code-block:: python
	
        import time
        import random
        import logging
        from acris import MpLogger
        import os
        import multiprocessing as mp

        logger=logging.getLogger(__name__)

        def subproc(limit=1):
            for i in range(limit):
                sleep_time=3/random.randint(1,10)
                time.sleep(sleep_time)
                logger.info("proc [%s]: %s/%s - sleep %4.4ssec" % (os.getpid(), i, limit, sleep_time))

        level_formats={logging.DEBUG:"[ %(asctime)s ][ %(levelname)s ][ %(message)s ][ %(module)s.%(funcName)s(%(lineno)d) ]",
                        'default':   "[ %(asctime)s ][ %(levelname)s ][ %(message)s ]",
                        }
    
        mplogger=MpLogger(logging_level=logging.DEBUG, level_formats=level_formats, datefmt='%Y-%m-%d,%H:%M:%S.%f')
        mplogger.start()

        logger.debug("starting sub processes")
        procs=list()
        for limit in [1, 1]:
            proc=mp.Process(target=subproc, args=(limit, ))
            procs.append(proc)
            proc.start()
    
        for proc in procs:
            if proc:
                proc.join()
    
        logger.debug("sub processes completed")

        mplogger.stop()	
        
Within individual process
`````````````````````````
    .. code-block:: python
	
        import logging
	
        logger=logging.getLogger(__name__)
        logger.debug("logging from sub process")
    
Example output
~~~~~~~~~~~~~~

    .. code-block:: python

        [ 2016-12-19,11:39:44.953189 ][ DEBUG ][ starting sub processes ][ mplogger.<module>(45) ]
        [ 2016-12-19,11:39:45.258794 ][ INFO ][ proc [932]: 0/1 - sleep  0.3sec ]
        [ 2016-12-19,11:39:45.707914 ][ INFO ][ proc [931]: 0/1 - sleep 0.75sec ]
        [ 2016-12-19,11:39:45.710487 ][ DEBUG ][ sub processes completed ][ mplogger.<module>(56) ]
        
Decorators
----------

    Useful decorators for production and debug.
    
traced_method
~~~~~~~~~~~~~

    logs entry and exit of function or method.
    
    .. code-block :: python
    
        from acris import traced_method

        traced=traced_method(print, print_args=True, print_result=True)

        class Oper(object):
            def __init__(self, value):
                self.value=value
        
            def __repr__(self):
                return str(self.value)
        
            @traced
            def mul(self, value):
                self.value*=value 
                return self   
    
            @traced
            def add(self, value):
                self.value+=value
                return self
    
        o=Oper(3)
        print(o.add(2).mul(5).add(7).mul(8))
        
    would result with the following output:
    
    .. code-block :: python
        
        [ add ][ entering][ args: (2) ][ kwargs: {} ][ trace_methods.py.Oper(39) ]
        [ add ][ exiting ] [ time span: 0:00:00.000056][ result: 5 ][ trace_methods.py.Oper(39) ]
        [ mul ][ entering][ args: (5) ][ kwargs: {} ][ trace_methods.py.Oper(34) ]
        [ mul ][ exiting ] [ time span: 0:00:00.000010][ result: 25 ][ trace_methods.py.Oper(34) ]
        [ add ][ entering][ args: (7) ][ kwargs: {} ][ trace_methods.py.Oper(39) ]
        [ add ][ exiting ] [ time span: 0:00:00.000007][ result: 32 ][ trace_methods.py.Oper(39) ]
        [ mul ][ entering][ args: (8) ][ kwargs: {} ][ trace_methods.py.Oper(34) ]
        [ mul ][ exiting ] [ time span: 0:00:00.000008][ result: 256 ][ trace_methods.py.Oper(34) ]
        256
	
Data Types
----------

    varies derivative of Python data types

MergeChainedDict
~~~~~~~~~~~~~~~~

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
------------

     Resource pool provides program with interface to manager resource pools.  This is used as means to 
     funnel processing.  
     
     ResourcePoolRequestor object can be used to request resource set resides in multiple pools.
     
     ResourcePoolRequestors object manages multiple requests for multiple resources. 
     
Sync Example
~~~~~~~~~~~~

    .. code-block:: python

        import time
        from acris import resource_pool as rp
        from acris import Threaded
        import queue
        from datetime import datetime

        class MyResource1(rp.Resource): pass

        class MyResource2(rp.Resource): pass

        rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
        rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 1, }).load()

        @Threaded()
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
~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~

    .. code-block:: python

        import time
        from acris import resource_pool as rp
        from acris import Threaded
        import queue
        from datetime import datetime

        class MyResource1(rp.Resource): pass
    
        class MyResource2(rp.Resource): pass

        rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
        rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 1, }).load()
   
        class Callback(object):
            def __init__(self, notify_queue):
                self.q=notify_queue
            def __call__(self, resources=None):
                self.q.put(resources)

        @Threaded()
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
~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~

    .. code-block:: python

        import time
        from acris import resource_pool as rp
        from acris import Threaded
        import queue
        from datetime import datetime

        class MyResource1(rp.Resource): pass
    
        class MyResource2(rp.Resource): pass

        rp1=rp.ResourcePool('RP1', resource_cls=MyResource1, policy={'resource_limit': 2, }).load()                   
        rp2=rp.ResourcePool('RP2', resource_cls=MyResource2, policy={'resource_limit': 2, }).load()
   
        class Callback(object):
            def __init__(self, notify_queue):
                self.q=notify_queue
            def __call__(self, ready=False):
                self.q.put(ready)

        @Threaded()
        def worker_callback(name, rps):
            print('[ %s ] %s getting resource' % (str(datetime.now()), name))
            notify_queue=queue.Queue()
            callback=Callback(notify_queue, name=name)
            request=rp.Requestor(request=rps, callback=callback)

            if request.is_reserved():
                resources=request.get()
            else:
                print('[ %s ] %s doing work before resource available' % (str(datetime.now()), name,))
                print('[ %s ] %s waiting for resources' % (str(datetime.now()), name,))
                notify_queue.get()
                resources=request.get()

            print('[ %s ] %s doing work (%s)' % (str(datetime.now()), name, repr(resources)))
            time.sleep(2)
            print('[ %s ] %s returning (%s)' % (str(datetime.now()), name, repr(resources)))
            request.put(*resources)

        r1=worker_callback('>>> w11-callback', [(rp1,1),])    
        r2=worker_callback('>>> w21-callback', [(rp1,1),(rp2,1)])    
        r3=worker_callback('>>> w22-callback', [(rp1,1),(rp2,1)])    
        r4=worker_callback('>>> w12-callback', [(rp1,1),]) 
                     
Requestor Example Output
~~~~~~~~~~~~~~~~~~~~~~~~

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

Virtual ResourcePool
--------------------

    Like ResourcePool, VResourcePool manages resources.  The main difference between the two is that ResourcePool manages physical resource objects.  VResourcePool manages virtual resources (VResource) that only represent physical resources.  VResources can not be activated or deactivated.
    
    One unique property VResourcePool enables is that request could be returned by quantity.
    
Virtual Requestors Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code-block:: python

        import time
        from acris import virtual_resource_pool as rp
        from acris.threaded import Threaded
        from acris.mplogger import create_stream_handler
        import queue
        from datetime import datetime
        
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

        @Threaded()
        def worker_callback(name, rps):
            print('[ %s ] %s getting resource' % (str(datetime.now()), name))
            notify_queue=queue.Queue()
            callback=Callback(notify_queue, name=name)
            request_id=requestors.reserve(request=rps, callback=callback)

            if not requestors.is_reserved(request_id):
                print('[ %s ] %s doing work before resource available' % (str(datetime.now()), name,))
                notify_queue.get()
            resources=requestors.get(request_id)

            print('[ %s ] %s doing work (%s)' % (str(datetime.now()), name, repr(resources)))
            time.sleep(1)
            print('[ %s ] %s returning (%s)' % (str(datetime.now()), name, repr(resources)))
            requestors.put_requested(rps)

        r2=worker_callback('>>> w21-callback', [(rp1,1), (rp2,1)])    
        r1=worker_callback('>>> w11-callback', [(rp1,1),])    
        r3=worker_callback('>>> w22-callback', [(rp1,1), (rp2,1)])    
        r4=worker_callback('>>> w12-callback', [(rp1,1),]) 
 
                     
Virtual Requestor Example Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code-block:: python

        [ 2016-12-16 14:27:53.224110 ] >>> w21-callback getting resource
        [ 2016-12-16 14:27:53.224750 ] >>> w11-callback getting resource
        [ 2016-12-16 14:27:53.225567 ] >>> w22-callback getting resource
        [ 2016-12-16 14:27:53.226220 ] >>> w12-callback getting resource
        [ 2016-12-16 14:27:53.237146 ] >>> w11-callback doing work ([Resource(name:MyResource1)])
        [ 2016-12-16 14:27:53.238361 ] >>> w12-callback doing work before resource available
        [ 2016-12-16 14:27:53.241046 ] >>> w21-callback doing work before resource available
        [ 2016-12-16 14:27:53.242350 ] >>> w22-callback doing work ([Resource(name:MyResource1), Resource(name:MyResource2)])
        [ 2016-12-16 14:27:54.238443 ] >>> w11-callback returning ([Resource(name:MyResource1)])
        [ 2016-12-16 14:27:54.246868 ] >>> w22-callback returning ([Resource(name:MyResource1), Resource(name:MyResource2)])
        [ 2016-12-16 14:27:54.257040 ] >>> w12-callback doing work ([Resource(name:MyResource1)])
        [ 2016-12-16 14:27:54.259858 ] >>> w21-callback doing work ([Resource(name:MyResource1), Resource(name:MyResource2)])
        [ 2016-12-16 14:27:55.258659 ] >>> w12-callback returning ([Resource(name:MyResource1)])
        [ 2016-12-16 14:27:55.262741 ] >>> w21-callback returning ([Resource(name:MyResource1), Resource(name:MyResource2)])
        
Mediator
--------
    
    Class interface to generator allowing query of has_next()
    
Example 
~~~~~~~

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
~~~~~~~~~~~~~~

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
        
Utilities
=========

commdir.py
----------

    .. code-block:: python

        usage: commdir.py [-h] [--dir1 DIR1] [--dir2 DIR2] [--quiet] [--out [REPORT]]
                          [--follow] [--detailed] [--sync-cmd] [--merge] [--total]
                          [--ignore [PATTERN [PATTERN ...]]]

        Reports differences in directory structure and content. commdir.py will exit
        with 0 if directories found the same. otherwise, it will exit with 1.

        optional arguments:
          -h, --help            show this help message and exit
          --dir1 DIR1           source folder for the comparison
          --dir2 DIR2           target folder for the comparison
          --quiet               avoid writing any report out, default: False
          --out [REPORT]        file to write report to, default: stdout
          --follow              follow links when walking folders, default: False
          --detailed            provide detailed file level diff, default: False
          --sync-cmd            provide commands that would align dirs and files,
                                default: False
          --merge               when sync-cmd, set how diff commands would be
                                resolved, default: dir1 is base.
          --total               outputs summary.
          --ignore [PATTERN [PATTERN ...]]
                                pattern to ignore

        example: python commdir.py --dir1 my_folder --dir2 other_folder --ignore __pycache__ .*DS_Store
        
    commdir.py also provides access to its underlined function commdir:

    .. code-block:: python
    
        commdir(dir1, dir2, ignore=[], detailed=False, followlinks=False, quiet=False, bool_result=True)
    
    compares two directory structures and their files.
    
        commdir walks through two directories, dir1 and dir2. While walking, it aggregates information
        on the difference between the two structures and their content.
    
        If bool_result is True, commdir will return True if difference was found. 
        When False, it would return a DiffContent namedtuple with the following fields:
        
            - diff (boolean)
            - folders_only_in_dir1 (list)
            - folders_only_in_dir2 (list) 
            - files_only_in_dir1 (list)
            - files_only_in_dir2 (list) 
            - diff_files (list)
            - diff_detail (list)
     
        Args:
            dir1, dir2: two directories structure to compare.
            ignore: list of regular expression strings to ignore, when directory is ignored, all its sub folders are ignored too.
            detailed: if set, will generate detailed file level comparison.
            followlinks: if set, symbolic links will be followed.
            quiet: if set, information will not be printed to stdio.
            bool_result: instruct how the function would respond to caller (True: boolean or False: DiffContent)

commdir example output
~~~~~~~~~~~~~~~~~~~~~~

    .. code-block:: python

        ----------------------------
        folders only in other_folder
        ----------------------------
           static/admin/fonts
           static/admin/js/vendor
           static/admin/js/vendor/jquery
           static/admin/js/vendor/xregexp
        -----------------------
        files only in my_folder
        -----------------------
           docs/._example.rst
           docs/._user_guide.rst
        --------------------------
        files only in other_folder
        --------------------------
           static/admin/css/fonts.css
           static/admin/fonts/LICENSE.txt
           static/admin/fonts/README.txtff
           static/admin/img/LICENSE
           static/admin/js/vendor/jquery/jquery.js
           static/admin/js/vendor/jquery/jquery.min.js
           static/admin/js/vendor/xregexp/xregexp.min.js
        ----------------
        files different:
        ----------------
           .pydevproject
           ui/settings/prod.py
           ui/wsgi.py
           personalenv.xml
        --------
        Summary:
        --------
          Folders only in my_folder: 0
          Files only in my_folder: 2
          Folders only in other_folder: 4
          Files only in other_folder: 7
          Files different: 4
          
bee.py
------

    utility to run commands on multiple hosts and collect responses.

    .. code-block :: python

        usage: bee.py [-h] -c COMMAND [-p PARALLEL] -t HOST [-u USERNAME]
                      [--sudo-user USERNAME] [--keep-log]

        Sends ssh command to multiple destinations.

        optional arguments:
          -h, --help            show this help message and exit
          -c COMMAND, --command COMMAND
                                command to execute over ssh channel
          -p PARALLEL, --parallel PARALLEL
                                number of parallel session to open
          -t HOST, --target HOST
                                destination host to run against
          -u USERNAME, --user USERNAME
                                user to use for ssh authentication
          --sudo-user USERNAME  sudo user to use to run commands
          --keep-log            indicates bee to keep host logs instead of deleting
    
csv2xlsx.py
-----------
    
    converts multiple CSV file to XLSX file. Each CSV file will end on its own sheet.
    
    .. code-block :: python
    
        usage: csv2xlsx.py [-h] [-d DELIMITER] [-o OUTFILE] CSV [CSV ...]

        Creates Excel file from one or more CSV files. If multiple CSV are provided,
        they wiull be mapped to separated sheets. If "-" is provided, input will be
        acquire from stdin.

        positional arguments:
          CSV                   csv files to merge in xlsx; if -, stdin is assumed

        optional arguments:
          -h, --help            show this help message and exit
          -d DELIMITER, --delimiter DELIMITER
                                select delimiter character
          -o OUTFILE, --out OUTFILE
                                output xlsx filename
                                
mail.py
-------

    send mail utility and function API

    .. code-block :: python

        usage: mail.py [-h] [-a ATTACHMENT] [-o FILE] -s SUBJECT [-b BODY]
                       [-f MAILFROM] [-c CC] -t RECIPIENT

        Send the contents of a directory as a MIME message. Unless the -o option is
        given, the email is sent by forwarding to your local SMTP server, which then
        does the normal delivery process. Your local machine must be running an SMTP
        server.

        optional arguments:
          -h, --help            show this help message and exit
          -a ATTACHMENT, --attach ATTACHMENT
                                Mail the contents of the specified directory or file,
                                Only the regular files in the directory are sent, and
                                we don't recurse to subdirectories.
          -o FILE, --output FILE
                                Print the composed message to FILE instead of sending
                                the message to the SMTP server.
          -s SUBJECT, --subject SUBJECT
                                Subject for email message (required).
          -b BODY, --body BODY  Boby text for the message (optional).
          -f MAILFROM, --mailfrom MAILFROM
                                The value of the From: header (optional); if not
                                provided $USER@$HOSTNAME will be use as sender
          -c CC, --malicc CC    The value of the CC: header (optional)
          -t RECIPIENT, --mailto RECIPIENT
                                A To: header value (at least one required)
                                
prettyxml.py
------------

    Reformat XML in hierarchical structure.

    .. code-block :: python
    
        usage: pretty-xml.py [-h] [-o OUTFILE] [XML [XML ...]]

        Pretty prints XML file that is not pretty.

        positional arguments:
          XML                   XML files to pretty print; if - or none provided,
                                stdin is assumed

        optional arguments:
          -h, --help            show this help message and exit
          -o OUTFILE, --out OUTFILE
                                output filename; defaults to stdout

sshcmd
------

    Runs single shh command on remote host

    .. code-block :: python
    
        def sshcmd(cmd, host, password,)
        
        Args:
            cmd: command to execute
            host: remote host to run on
            password: user's password on remote host
        
touch
-----

    UNIX like touch with ability to create missing folders.

    .. code-block :: python

        touch(path, times=None, dirs=False)
        
        Args:
            path: to touch
            times: a 2-tuple of the form (atime, mtime) where each member is an int or float expressing seconds.
                   defaults to current time.
            dirs: if set, create missing folders


Misc
====

camel2snake and snake2camel
---------------------------

    camel2snake(name) and snake2camel(name) will convert name from camel to snake and from snake to camel respectively.
     
     
Change History
==============

Version 2.2
-----------

    1. MpLogger was change to have single log instead of two (error and debug)
    #. MpLogger add new arguments: name, console, force_global, etc.
    