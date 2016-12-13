'''
Created on Dec 8, 2016

@author: arnon
'''
import datetime
from types import FunctionType
import inspect

# check if an object should be decorated
def do_decorate(attr, value):
    # result = ('__' not in attr and
    result = (isinstance(value, FunctionType) and
              getattr(value, 'decorate', True))
    return result

# decorate all instance methods (unless excluded) with the same decorator
def decorated_class(decorator):
    class DecorateAll(type):
        def __new__(cls, name, bases, dct):
            for attr, value in dct.items():
                if do_decorate(attr, value):
                    decorated=decorator(name, value)
                    dct[attr] = decorated
                    #print('decorated', attr, decorated)
            return super(DecorateAll, cls).__new__(cls, name, bases, dct)
    return DecorateAll

# decorator to exclude methods
def dont_decorate(f):
    f.decorate = False
    return f

def traced_method(print_func=None, print_args=False):
    def print_method_name(name, f=None):
        (frame, filename, line_number,
         function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        caller="%s.%s(%s)" % (filename, function_name, line_number)
        if f==None :
            text_id='%s' % (name.__name__)
            method=name
        else:
            text_id='%s.%s' % (name, f.__name__, )
            method=f
            
        def wrapper(*args, **kwargs):
            
            start=datetime.datetime.now()
            func_args=''
            if print_args:
                func_args="[ args: %s ][ kwargs: %s ]" % (args, kwargs)
            if print_func:
                print_func('[ %s ][ %s ][ entering]%s[ %s ]' % (str(start), text_id, func_args,caller))
            result=method(*args, **kwargs)
            finish=datetime.datetime.now()
            if print_func:
                print_func('[ %s ][ %s ][ exiting ] [ time span: %s][ %s ]' % (str(finish), text_id, str(finish-start), caller))
            return result
        return wrapper
    return print_method_name