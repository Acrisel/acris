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

import unittest
import functools 

class MergedChainedDict(dict):
    def __init__(self, *args, submerge=False):
        ''' Merge list of dicts.  
        Merge is such that significant (left) wins over least significant (right).
        
        Args: 
            args: list of dicts where left most is most significant.
            submerge: if an entity in a dictionary is dictionary, merge-chain that entity.
        '''
        super().__init__()
        args=list(args)
        if not submerge:
            for arg in args[::-1]:
                self.update(arg)
        else:
            keys = functools.reduce(lambda x,y: x+y, [list(arg.keys()) for arg in args], list())
            for key in set(keys):
                values = [arg.get(key) for arg in args]
                values = [value for value in values if value is not None]
                if len(values) < 1: 
                    value = None
                else:
                    value0 = values[0] 
                    if not isinstance(value0, dict):
                        value = value0
                    else: # this is a dict
                        value = MergedChainedDict(*values, submerge=True)
                self[key] = value

class TestMergedChainedDict(unittest.TestCase):

    def test_uni_depth(self):
        a = {1:11, 2:22}
        b = {3:33, 4:44}
        c = {1:55, 4:66}
        d = MergedChainedDict(c, b, a)
        d_expected = {1: 55, 2: 22, 3: 33, 4: 66}
        self.assertEqual(d, d_expected)
            
    def test_two_depth_submerge(self):
        a = {1:11, 2:22, 3:{'a': 1, 'b':2, 'c':5}}
        b = {3:{'a':2, 'c': 7}, 4:44}
        c = {1:55, 4:66, 3:{'a': 3, 'b':2}}
        d = MergedChainedDict(c, b, a, submerge=True)
        d_expected = {1: 55, 2: 22, 3: {'a': 3, 'b': 2, 'c': 7}, 4: 66}
        self.assertEqual(d, d_expected)
            
if __name__ == '__main__':
    
    unittest.main()