'''
Created on Dec 9, 2016

@author: arnon
'''
from acris.decorated_class import traced_method

traced=traced_method(print)

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