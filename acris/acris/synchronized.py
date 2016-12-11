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


import threading
from functools import wraps
from types import FunctionType

def synchronized(method):
    @wraps(method)
    def f(*args, **kwargs):
        self = args[0]
        self.mutex.acquire();
        # print(method.__name__, 'acquired')
        try:
            return method(*args, **kwargs)
        finally:
            self.mutex.release();
            # print(method.__name__, 'released')
    return f

def dont_synchronize(f):
    #f.synchronize = False
    setattr(f, 'synchronize', False)
    return f

# check if an object should be decorated
def do_synchronize(attr, value):
    # result = ('__' not in attr and
    result = (isinstance(value, FunctionType) and
              getattr(value, 'synchronize', True))
    return result

class SynchronizedType(type):
    def __new__(cls, name, bases, namespace, **kwds):
        #not_synchronize=namespace.get('__not_synchronized__', []) 
        #synchronize=namespace.get('__synchronized__', []) 
        namespace['mutex'] = threading.RLock()
        for (method, val) in namespace.items():
            #synchronize_name=not synchronize or method in synchronize
            #not_synchronize_name=not_synchronize and method in not_synchronize
            if callable(val) and method != '__init__' and do_synchronize(method, val): #and synchronize_name and not  not_synchronize_name:
                #print("synchronizing %s" % method)
                namespace[method] = synchronized(val)
            else:
                #print("skip synchronizing %s" % method)
                pass
        return type.__new__(cls, name, bases, namespace, **kwds)   

class SynchronizeAll(metaclass=SynchronizedType):
    pass

# You can create your own self.mutex, or inherit
# from this class:
class Synchronization:
    def __init__(self):
        self.mutex = threading.RLock()       
