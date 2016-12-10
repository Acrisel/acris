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


from acris import Singleton
from acris.decorated_class import decorated_class, traced_method

#tracer=traced_method(print)

class Sequence(Singleton):
    __seq=0
    
    def __init__(self, *args, **kwargs):
        pass
    
    #@tracer
    def __call__(self,) :
        seq=self.__seq
        self.__seq += 1
        return seq
    
    def reset(self, initial=0):
        self.__seq=initial
    
    


