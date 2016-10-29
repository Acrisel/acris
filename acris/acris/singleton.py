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
    __locker=Lock() 
    #__instance = None
    __instance={}
      
    def __call__( self, name='', *args, **kargs):   
        SingletonType.__locker.acquire()
        try:
            instance=self.__instance[name]
        except KeyError:
            instance=super(SingletonType, self).__call__(*args, **kargs)
            self.__instance[name]=instance
        #if not self.__instance:
        #    self.__instance = super(SingletonType, self).__call__(*args, **kargs)
        SingletonType.__locker.release()
        return instance
    
        
class Singleton(metaclass=SingletonType):
    pass