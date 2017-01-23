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