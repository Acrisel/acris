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

class  Mediator(object):
    def __init__(self, generator):
        self.generator=generator
        self.__next_values=list()
    
    def __iter__(self):
        return self
        
    def __next__(self):
        if len(self.__next_values) >0:
            value=self.__next_values[0]
            self.__next_values=self.__next_values[1:]
            return value
        else:
            try:
                value=next(self.generator)
            except StopIteration:
                raise
            else:
                return value
        
    def has_next(self, count=1):
        if len(self.__next_values) > count:
            return True
        
        for _ in range(count-len(self.__next_values)):
            try:
                value=next(self.generator)
            except StopIteration:
                break
            else:
                self.__next_values.append(value)

        result=len(self.__next_values) - count >= 0
        return result
    
