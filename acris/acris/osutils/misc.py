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
Created on Jan 20, 2017

@author: arnon
'''
import os
import pexpect as expect

def sshcmd(cmd, host, password,):
    ''' runs single command on host using ssh
    '''
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


def touch(path, times=None, dirs=False):
    ''' perform UNIX touch with extra
        based on: http://stackoverflow.com/questions/12654772/create-empty-file-using-python
        
    Args:
        path: file path to touch
        times: a 2-tuple of the form (atime, mtime) where each member is an int or float expressing seconds.
            defaults to current time.
        dirs: is set, create folders if not exists 
    '''
    
    if dirs:
        basedir = os.path.dirname(path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
            
    with open(path, 'a'):
        os.utime(path, times=times)

