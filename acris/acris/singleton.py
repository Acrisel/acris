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


from threading import Lock


class SingletonType(type):
    '''
        Thread friendly Singleton construct
    '''
    __locker=Lock() 
    #__instance = None
    __instance={}
    
    #def __init__(self, name, bases, attrs):
    #    super(SingletonType, self).__init__(name, bases, attrs)
      
    def __call__( self, name, *args, **kwargs):   
        SingletonType.__locker.acquire()
        try:
            instance=self.__instance[name]
        except KeyError:
            instance=super(SingletonType, self).__call__(*args, **kwargs)
            self.__instance[name]=instance
        SingletonType.__locker.release()
        return instance
    
        
class Singleton(metaclass=SingletonType):
    pass

if __name__ == '__main__':

    class SingTest(Singleton):
        __data=None
        
        def __init__(self, mydata=None, *args, **kwargs):
            print('init', mydata, args, kwargs)
            self.__data = mydata
        
        def load(self, mydata=None):
            if not self.__data:
                self.__data = mydata
            return self
                
        def get(self):
            return self.__data
        
    
    s1=SingTest('S1', 55, a=23).load(1)
    print(s1.get())
    
    s2=SingTest('S2')
    print(s2.get())
    s2.load(2)
    print(s2.get())
    s2.load(3)
    print(s2.get())
    
    print(s1.get())
            
    