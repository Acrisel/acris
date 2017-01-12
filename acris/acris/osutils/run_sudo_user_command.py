#!/bin/env python3
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

import pexpect as expect

def run_abi_cmd(host, cmd, password,):
  p=expect.spawn("ssh " + host)
  i0=p.expect([r'.+password:.*'])
  if i0 == 0:
    p.sendline(password)
    i1=p.expect([r'Sorry.+', r'.*'])
    if i1==0:
      print('Wrongs password')
      return 1
    else:
      print('inside')
      p.sendline(cmd)
  else:
    print('Not expected')
    
if __name__ == '__main__':
  run_abi_cmd("urh12011", "echo I am", 'Chil0542',)
