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

"""
About
=========
:synopsis:     threaded provides decorator for class methods to run via a thread
:moduleauthor: Arnon Sela
:date:         2016/10/28
:description:  a method decorated with @threaded would run in a separated thread. this work 
   
:comment: based on http://code.activestate.com/recipes/576684-simple-threading-decorator/



    
"""


from functools import wraps
from threading import Thread, RLock, Event #, current_thread
import logging

logger=logging.getLogger(__name__)

__all__ = ['threaded']

class AsyncResult(object): 
    """Represents an asynchronous operation that may not have completed yet.""" 
    def __init__(self): 
        self.completed = False 
        self.failed = False 
        self.__wait = Event() 
        self.__callbacks = [] 
        self.__errbacks = [] 
        self.__retval = None 
        self.__error = None 
        self.__lock = RLock()

    def complete(self):
        self.__lock.acquire()
        self.completed = True
        self.__wait.set()
        self.__lock.release()
    
    def succeed(self, retval):
        self.__retval = retval
        self.complete()
        for callback in self.__callbacks:
            callback(retval)
        self.clearCallbacks()
    
    def fail(self, error):
        self.__error = error
        self.failed = True
        self.complete()
        for errback in self.__errbacks:
            errback(error)
        self.clearCallbacks()
    
    def clearCallbacks(self):
        self.__callbacks = []
        self.__errbacks = []
    
    def addCallback(self, callback, errback=None):
        self.__lock.acquire()
        try:
            if self.completed:
                if not self.failed:
                    callback(self.__retval)
            else:
                self.__callbacks.append(callback)
            if not errback == None:
                self.addErrback(errback)
        finally:
            self.__lock.release()
    
    def addErrback(self, errback):
        self.__lock.acquire()
        try:
            if self.completed:
                if self.failed:
                    errback(self.__error)
            else:
                self.__errbacks.append(errback)
        finally:
            self.__lock.release()
    
    def __getResult(self):
        self.__wait.wait()
        if not self.failed:
            return self.__retval
        else:
            raise self.__error
    result=property(__getResult)


class RetriveAsycValue(object):
    def __init__(self, name):
        self.name=name
        
    def __call__(self, retval):
        print(self.name, ':', retval)  
    
import inspect

def traces(trace, start=0, end=None):
    '''
     File "/private/var/acrisel/sand/gradior/gradior/gradior/gradior/loop_task.py", line 41, in task_wrapper
    '''
    result=[ "File \"%s\", line %s, in %s\n    %s" % (frame.filename, frame.lineno, frame.function, frame.code_context[0].rstrip()) for frame in trace]
    return result
   
def threaded(method): 
    @wraps(method)
    def wrapper(*args, **kwargs): 
        async_result = AsyncResult() 
        def _method(): 
            try: 
                result=method(*args, **kwargs) 
            except Exception as e: 
                trace=inspect.trace()
                trace=traces(trace, 2)
                async_result.fail(trace)
            else:
                async_result.succeed(result)
        Thread(target = _method).start() 
        return async_result 
    return wrapper


class Threaded(object):
    def __init__(self, log=True):
        self.log=log
        
    def __call__(self,method):
        @wraps(method)
        def wrapper(*args, **kwargs): 
            async_result = AsyncResult() 
            def _method(): 
                try: 
                    result=method(*args, **kwargs) 
                except Exception as e: 
                    trace=inspect.trace()
                    trace=traces(trace,start=0, end=None)
                    if self.log: logger.error("%s\n    %s" % (repr(e), '\n    '.join(trace)))
                    async_result.fail(trace)
                else:
                    async_result.succeed(result)
            Thread(target = _method).start() 
            return async_result 
        return wrapper
        
    
    
    