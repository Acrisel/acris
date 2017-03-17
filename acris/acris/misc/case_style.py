#!/usr/bin/env python3 
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

'''
based on the following links:
    http://stackoverflow.com/questions/4303492/how-can-i-simplify-this-conversion-from-underscore-to-camelcase-in-python
    http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
'''

import re
_first_cap_re = re.compile(r'(.)([A-Z][a-z]+)')
_all_cap_re = re.compile(r'([a-z0-9])([A-Z])')

def camel2snake(name):
    s1 = _first_cap_re.sub(r'\1_\2', name)
    return _all_cap_re.sub(r'\1_\2', s1).lower()

_underscore_re=re.compile(r'(?!^)_([a-zA-Z])')
def snake2camel(name, capitalize=True):
    result=_underscore_re.sub(lambda m: m.group(1).upper(), name)
    if capitalize:
        result=result[0].capitalize() + result[1:]
    return result   

if __name__ == '__main__':
    cnames=['CamelCase', 'CamelCamelCase', 'Camel2Camel2Case', 'getHTTPResponseCode', 'get2HTTPResponseCode', 'HTTPResponseCode', 'HTTPResponseCodeXYZ']
    snames=['camel_case', 'camel_camel_case_1', 'camel2_camel2_case', 'get_HTTP_response_code', 'get2_HTTP_response_code', 'HTTP_response_code', 'HTTP_response_code_XYZ']

    for name in snames:
        v=snake2camel(name)
        V=camel2snake(v)
        print(name, v, V)
    print('-----------------')    
    for name in snames:
        v=camel2snake(name)
        V=snake2camel(v)
        print(name, v, V)
    print('-----------------')  
    a="item_b_1"
    b=snake2camel(a,)
    print(b)
    c=snake2camel(b,)
    print(c)