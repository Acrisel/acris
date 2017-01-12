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

''' branched off from https://github.com/pexpect/pexpect/blob/master/examples/hive.py
    
hive -- Hive Shell

Example:
    $ hive.py --sameuser --samepass host1.example.com host2.example.net
    username: myusername
    password:
    connecting to host1.example.com - OK
    connecting to host2.example.net - OK
    targetting hosts: 192.168.1.104 192.168.1.107
    CMD (? for help) > uptime
    =======================================================================
    host1.example.com
    -----------------------------------------------------------------------
    uptime
    23:49:55 up 74 days,  5:14,  2 users,  load average: 0.15, 0.05, 0.01
    =======================================================================
    host2.example.net
    -----------------------------------------------------------------------
    uptime
    23:53:02 up 1 day, 13:36,  2 users,  load average: 0.50, 0.40, 0.46
    =======================================================================
'''

from __future__ import print_function

from __future__ import absolute_import

import sys
import os
import re
import optparse
import time
import getpass
import atexit
try:
    import pexpect
    from pexpect import pxssh
except ImportError:
    sys.stderr.write("You do not have 'pexpect' installed.\n")
    sys.stderr.write("On Ubuntu you need the 'python-pexpect' package.\n")
    sys.stderr.write("    aptitude -y install python-pexpect\n")
    exit(1)


try:
    import readline
except ImportError:
    pass
else:
    histfile = os.path.join(os.environ["HOME"], ".hive_history")
    try:
        readline.read_history_file(histfile)
    except IOError:
        pass
    atexit.register(readline.write_history_file, histfile)

CMD_HELP='''Hive commands are preceded by a colon : (just think of vi).
:target name1 name2 name3 ...
    set list of hosts to target commands
:target all
    reset list of hosts to target all hosts in the hive.
:to name command
    send a command line to the named host. This is similar to :target, but
    sends only one command and does not change the list of targets for future
    commands.
:sync
    set mode to wait for shell prompts after commands are run. This is the
    default. When Hive first logs into a host it sets a special shell prompt
    pattern that it can later look for to synchronize output of the hosts. If
    you 'su' to another user then it can upset the synchronization. If you need
    to run something like 'su' then use the following pattern:
    CMD (? for help) > :async
    CMD (? for help) > sudo su - root
    CMD (? for help) > :prompt
    CMD (? for help) > :sync
:async
    set mode to not expect command line prompts (see :sync). Afterwards
    commands are send to target hosts, but their responses are not read back
    until :sync is run. This is useful to run before commands that will not
    return with the special shell prompt pattern that Hive uses to synchronize.
:refresh
    refresh the display. This shows the last few lines of output from all hosts.
    This is similar to resync, but does not expect the promt. This is useful
    for seeing what hosts are doing during long running commands.
:resync
    This is similar to :sync, but it does not change the mode. It looks for the
    prompt and thus consumes all input from all targetted hosts.
:prompt
    force each host to reset command line prompt to the special pattern used to
    synchronize all the hosts. This is useful if you 'su' to a different user
    where Hive would not know the prompt to match.
:send my text
    This will send the 'my text' wihtout a line feed to the targetted hosts.
    This output of the hosts is not automatically synchronized.
:control X
    This will send the given control character to the targetted hosts.
    For example, ":control c" will send ASCII 3.
:exit
    This will exit the hive shell.
'''

def login (args, cli_username=None, cli_password=None):

    # I have to keep a separate list of host names because Python dicts are not ordered.
    # I want to keep the same order as in the args list.
    host_names = []
    hive_connect_info = {}
    hive = {}
    # build up the list of connection information (hostname, username, password, port)
    for host_connect_string in args:
        hcd = parse_host_connect_string (host_connect_string)
        hostname = hcd['hostname']
        port     = hcd['port']
        if port == '':
            port = None
        if len(hcd['username']) > 0:
            username = hcd['username']
        elif cli_username is not None:
            username = cli_username
        else:
            username = input('%s username: ' % hostname)
        if len(hcd['password']) > 0:
            password = hcd['password']
        elif cli_password is not None:
            password = cli_password
        else:
            password = getpass.getpass('%s password: ' % hostname)
        host_names.append(hostname)
        hive_connect_info[hostname] = (hostname, username, password, port)
    # build up the list of hive connections using the connection information.
    for hostname in host_names:
        print('connecting to', hostname)
        try:
            fout = open("log_"+hostname, "wb")
            hive[hostname] = pxssh.pxssh()
            # Disable host key checking.
            hive[hostname].SSH_OPTS = (hive[hostname].SSH_OPTS
                    + " -o 'StrictHostKeyChecking=no'"
                    + " -o 'UserKnownHostsFile /dev/null' ")
            hive[hostname].force_password = True
            hive[hostname].login(*hive_connect_info[hostname])
            print(hive[hostname].before)
            hive[hostname].logfile = fout
            print('- OK')
        except Exception as e:
            print('- ERROR', end=' ')
            print(str(e))
            print('Skipping', hostname)
            hive[hostname] = None
    return host_names, hive

def main ():

    global options, args, CMD_HELP

    rows = 24
    cols = 80

    if options.sameuser:
        cli_username = input('username: ')
    else:
        cli_username = None

    if options.samepass:
        cli_password = getpass.getpass('password: ')
    else:
        cli_password = None

    host_names, hive = login(args, cli_username, cli_password)

    synchronous_mode = True
    target_hostnames = host_names[:]
    print('targetting hosts:', ' '.join(target_hostnames))
    while True:
        cmd = input('CMD (? for help) > ')
        cmd = cmd.strip()
        if cmd=='?' or cmd==':help' or cmd==':h':
            print(CMD_HELP)
            continue
        elif cmd==':refresh':
            refresh (hive, target_hostnames, timeout=0.5)
            for hostname in target_hostnames:
                print('/' + '=' * (cols - 2))
                print('| ' + hostname)
                print('\\' + '-' * (cols - 2))
                if hive[hostname] is None:
                    print('# DEAD: %s' % hostname)
                else:
                    print(hive[hostname].before)
            print('#' * 79)
            continue
        elif cmd==':resync':
            resync (hive, target_hostnames, timeout=0.5)
            for hostname in target_hostnames:
                print('/' + '=' * (cols - 2))
                print('| ' + hostname)
                print('\\' + '-' * (cols - 2))
                if hive[hostname] is None:
                    print('# DEAD: %s' % hostname)
                else:
                    print(hive[hostname].before)
            print('#' * 79)
            continue
        elif cmd==':sync':
            synchronous_mode = True
            resync (hive, target_hostnames, timeout=0.5)
            continue
        elif cmd==':async':
            synchronous_mode = False
            continue
        elif cmd==':prompt':
            for hostname in target_hostnames:
                try:
                    if hive[hostname] is not None:
                        hive[hostname].set_unique_prompt()
                except Exception as e:
                    print("Had trouble communicating with %s, so removing it from the target list." % hostname)
                    print(str(e))
                    hive[hostname] = None
            continue
        elif cmd[:5] == ':send':
            cmd, txt = cmd.split(None,1)
            for hostname in target_hostnames:
                try:
                    if hive[hostname] is not None:
                        hive[hostname].send(txt)
                except Exception as e:
                    print("Had trouble communicating with %s, so removing it from the target list." % hostname)
                    print(str(e))
                    hive[hostname] = None
            continue
        elif cmd[:3] == ':to':
            cmd, hostname, txt = cmd.split(None,2)
            print('/' + '=' * (cols - 2))
            print('| ' + hostname)
            print('\\' + '-' * (cols - 2))
            if hive[hostname] is None:
                print('# DEAD: %s' % hostname)
                continue
            try:
                hive[hostname].sendline (txt)
                hive[hostname].prompt(timeout=2)
                print(hive[hostname].before)
            except Exception as e:
                print("Had trouble communicating with %s, so removing it from the target list." % hostname)
                print(str(e))
                hive[hostname] = None
            continue
        elif cmd[:7] == ':expect':
            cmd, pattern = cmd.split(None,1)
            print('looking for', pattern)
            try:
                for hostname in target_hostnames:
                    if hive[hostname] is not None:
                        hive[hostname].expect(pattern)
                        print(hive[hostname].before)
            except Exception as e:
                print("Had trouble communicating with %s, so removing it from the target list." % hostname)
                print(str(e))
                hive[hostname] = None
            continue
        elif cmd[:7] == ':target':
            target_hostnames = cmd.split()[1:]
            if len(target_hostnames) == 0 or target_hostnames[0] == all:
                target_hostnames = host_names[:]
            print('targetting hosts:', ' '.join(target_hostnames))
            continue
        elif cmd == ':exit' or cmd == ':q' or cmd == ':quit':
            break
        elif cmd[:8] == ':control' or cmd[:5] == ':ctrl' :
            cmd, c = cmd.split(None,1)
            if ord(c)-96 < 0 or ord(c)-96 > 255:
                print('/' + '=' * (cols - 2))
                print('| Invalid character. Must be [a-zA-Z], @, [, ], \\, ^, _, or ?')
                print('\\' + '-' * (cols - 2))
                continue
            for hostname in target_hostnames:
                try:
                    if hive[hostname] is not None:
                        hive[hostname].sendcontrol(c)
                except Exception as e:
                    print("Had trouble communicating with %s, so removing it from the target list." % hostname)
                    print(str(e))
                    hive[hostname] = None
            continue
        elif cmd == ':esc':
            for hostname in target_hostnames:
                if hive[hostname] is not None:
                    hive[hostname].send(chr(27))
            continue
        #
        # Run the command on all targets in parallel
        #
        for hostname in target_hostnames:
            try:
                if hive[hostname] is not None:
                    hive[hostname].sendline(cmd)
            except Exception as e:
                print("Had trouble communicating with %s, so removing it from the target list." % hostname)
                print(str(e))
                hive[hostname] = None

        #
        # print the response for each targeted host.
        #
        if synchronous_mode:
            for hostname in target_hostnames:
                try:
                    print('/' + '=' * (cols - 2))
                    print('| ' + hostname)
                    print('\\' + '-' * (cols - 2))
                    if hive[hostname] is None:
                        print('# DEAD: %s' % hostname)
                    else:
                        hive[hostname].prompt(timeout=2)
                        print(hive[hostname].before.decode())
                except Exception as e:
                    print("Had trouble communicating with %s, so removing it from the target list." % hostname)
                    print(str(e))
                    hive[hostname] = None
            print('#' * 79)

def refresh (hive, hive_names, timeout=0.5):

    '''This waits for the TIMEOUT on each host.
    '''

    # TODO This is ideal for threading.
    for hostname in hive_names:
        if hive[hostname] is not None:
            hive[hostname].expect([pexpect.TIMEOUT,pexpect.EOF],timeout=timeout)

def resync (hive, hive_names, timeout=2, max_attempts=5):

    '''This waits for the shell prompt for each host in an effort to try to get
    them all to the same state. The timeout is set low so that hosts that are
    already at the prompt will not slow things down too much. If a prompt match
    is made for a hosts then keep asking until it stops matching. This is a
    best effort to consume all input if it printed more than one prompt. It's
    kind of kludgy. Note that this will always introduce a delay equal to the
    timeout for each machine. So for 10 machines with a 2 second delay you will
    get AT LEAST a 20 second delay if not more. '''

    # TODO This is ideal for threading.
    for hostname in hive_names:
        if hive[hostname] is not None:
            for attempts in range(0, max_attempts):
                if not hive[hostname].prompt(timeout=timeout):
                    break

def parse_host_connect_string (hcs):

    '''This parses a host connection string in the form
    username:password@hostname:port. All fields are options expcet hostname. A
    dictionary is returned with all four keys. Keys that were not included are
    set to empty strings ''. Note that if your password has the '@' character
    then you must backslash escape it. '''

    if '@' in hcs:
        p = re.compile (r'(?P<username>[^@:]*)(:?)(?P<password>.*)(?!\\)@(?P<hostname>[^:]*):?(?P<port>[0-9]*)')
    else:
        p = re.compile (r'(?P<username>)(?P<password>)(?P<hostname>[^:]*):?(?P<port>[0-9]*)')
    m = p.search (hcs)
    d = m.groupdict()
    d['password'] = d['password'].replace('\\@','@')
    return d

if __name__ == '__main__':
    start_time = time.time()
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id: hive.py 533 2012-10-20 02:19:33Z noah $',conflict_handler="resolve")
    parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
    parser.add_option ('--samepass', action='store_true', default=False, help='Use same password for each login.')
    parser.add_option ('--sameuser', action='store_true', default=False, help='Use same username for each login.')
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error ('missing argument')
    if options.verbose: print(time.asctime())
    main()
    if options.verbose: print(time.asctime())
    if options.verbose: print('TOTAL TIME IN MINUTES:', end=' ')
    if options.verbose: print((time.time() - start_time) / 60.0)

