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

