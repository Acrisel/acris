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

from pexpect import pxssh
import getpass
import os
from multiprocessing import Pool
from tempfile import NamedTemporaryFile

def mssh1(commands, host, username, password, sudouser, output):
    out=open(output, "w")
    # open ssh channels
    s = pxssh.pxssh()
    try:
        s.login(host, username, password)
    except pxssh.ExceptionPxssh as e:
        out.write("{}: pxssh failed on login.".format(host))
        out.write("{}: {}".format(host ,e))
        return 

    prefix=''
    if sudouser:
      prefix='sudo -u {} '.format(sudouser)
    
    for command in commands:
        cmd=prefix+command
        #print('send command', cmd)
        s.sendline(cmd)        
        if sudouser:
            try:
                i=s.expect(['.*[pP]assword:.*', s.PROMPT])
            except Exception as e:
                out.write("{}: {}".format(host, s.before))
                out.write("{}: Failed to expect".format(host))
                print("Failed to expect", e)
                out.close()
                s.logout()
                return
            #print("i:", i)
            if i == 0:
                s.sendline(password)
            else:
                pass
        else:
            s.prompt()
        #print("{}: {}".format(host, s.before.decode()))
        out.write("{}: {}".format(host, s.before.decode()))
    out.close()
    s.logout()    

def mssh(commands, parallel, hosts, username, password, sudouser, keeplog):
    with Pool(processes=parallel) as pool: 
        output=[]
        for host in hosts:
            out=NamedTemporaryFile(mode="w", prefix="bee_"+host+"_", suffix=".log", delete=False)
            output.append(out.name)
            out.close()
            if keeplog: print("{} log: {}".format(host, out.name))
            result = pool.apply_async(mssh1, (commands, host, username, password, sudouser, out.name))    
        pool.close()
        pool.join()
        for out in output:
            with open(out, "r") as o:
                print(o.read())
            if not keeplog: os.remove(out)

if __name__ == '__main__':
    from argparse import ArgumentParser 
   
    parser = ArgumentParser(description="""
Sends ssh command to multiple destinations.
""")
    parser.add_argument('-c', '--command', required=True, action='append', metavar='COMMAND', default=[], dest='commands',
                        help="""command to execute over ssh channel""")
    parser.add_argument('-p', '--parallel', type=int, required=False, metavar='PARALLEL', dest='parallel', default=1,
                        help="""number of parallel session to open""")    
    parser.add_argument('-t', '--target', required=True, action='append', metavar='HOST', default=[], dest='hosts',
                        help="""destination host to run against""")
    parser.add_argument('-u', '--user', type=str, required=False, metavar='USERNAME', dest='username', default=os.getenv('USER'),
                        help="""user to use for ssh authentication""")
    parser.add_argument('--sudo-user', type=str, required=False, metavar='USERNAME', dest='sudouser', 
                        help="""sudo user to use to run commands""")
    parser.add_argument('--keep-log', required=False, action='store_true', dest='keeplog',  
                        help="""indicates bee to keep host logs instead of deleting""")

    args = parser.parse_args()
    
    password = getpass.getpass('password: ')
    mssh(commands=args.commands, parallel=args.parallel, hosts=args.hosts, username=args.username, password=password, sudouser=args.sudouser, keeplog=args.keeplog) 
