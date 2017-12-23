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

from subprocess import run, CompletedProcess, PIPE
import os


def format_complete_process(cwd, status):
    print("{}: {}".format(cwd, status.returncode))
    msg = status.stdout if status.returncode == 0 else status.stderr
    msg = msg.decode()
    msg = '\n'.join(["    {}".format(m) for m in msg.split('\n')])
    return(msg)


def read_cwd_file(rc):
    with open(rc, 'r') as f:
        names = map(lambda x: x.strip(), f.read().split('\n'))
        rcfiles = [f for f in names if f]
    return rcfiles


def mrun(cmd, cwd=None, max_retries=0, exception_tag='', ignore_exception=False, verbose=False):
    ''' perform git command on repositories.

    Args:
        cmd: list of command elements.
        cwd: list of locations to run command in;
            if cwd is a file containing, it assumes it contains 
            list of directories.
            Defaults to $PWD/.mrun or ~/.mrun,  whatever found first.
        max_retries: defines maximum limit for retries. -1: retry forever.
        exception_tag: tag to include in exception message.
        ignore_exception: avoid raise exception on failure.
        verbose: prints detailed information.

    Process:
        issue subprocess to run cmd in eacho of location in cwd.

    Returns:
        dictionary of subprocess.CompletedProcess.
    '''
    results = dict()

    # find default rconfs if one not provided
    if cwd is None:
        rc = os.path.join(os.getcwd(), '.mrun')
        if os.path.isfile(rc):
            cwd = [rc]
        else:
            rc = os.path.join(os.path.expanduser('~'), ".mrun")
            if os.path.isfile(rc):
                cwd = [rc]
    elif isinstance(cwd, str):
        cwd = [cwd]

    # replace file items on cwd with directories they contain
    for item in cwd:
        if os.path.isfile(item):
            cwd.extend(read_cwd_file(item))
            cwd.remove(item)

    if exception_tag is None:
        exception_tag = ''

    if verbose:
        print('Command: {}'.format(cmd))

    for cwd_ in cwd:
        retries = max_retries 
        while True:
            if verbose:
                if retries < max_retries:
                    print("{}: Retrying after failure: {}".format(cwd_, max_retries - retries))

            try:
                proc_complete = run(
                    cmd, shell=False, cwd=cwd_,
                    stdout=PIPE, stderr=PIPE)
            except Exception as e:
                msg = "Failed {}; {}".format(exception_tag, repr(e))
                if not ignore_exception:
                    raise Exception(msg) from e

                # create CompletedProcess for this failure
                proc_complete = CompletedProcess(args=cmd, returncode=1,
                                                 stderr="{}\n".format(msg).encode())

            # if command failed, check max_retries
            if proc_complete.returncode == 0 or retries == 0:
                break

            retries -= 1

        result = proc_complete
        results[cwd_] = result

        if verbose:
            msg = repr(proc_complete)
            # msg = format_complete_process(cwd_, result)
            print(msg)

    return results


def cmdargs():
    import argparse

    parser = argparse.ArgumentParser(
        description='''Run command in multiple directories.

Example:
    mrun --cwd dir1 dir2 -- git add .
    ''')

    parser.add_argument('--cwd', metavar='DIR', type=str, nargs='*',
                        help=('path where command should cd to; or '
                              'file that congaing list of directories '
                              'to operate on.'))
    parser.add_argument('--exception', metavar='TAG', type=str, required=False, dest='exception_tag',
                        help='tag exception message.')
    parser.add_argument('--nostop', action='store_true', dest='ignore_exception', default=False,
                        help='continue even if failed to run in one place.')
    parser.add_argument('--retries', '-r', type=int, dest='max_retries', default=0,
                        help='allows maximum of retries if command failed. value of -1 will retry forever.')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='print messages as it goes.')
    parser.add_argument('cmd', nargs=argparse.REMAINDER,
                        help='command to run.')
    args = parser.parse_args()
    return args


def main(args):
    kwargs = vars(args)

    # need to remove innitial '--' from cmd
    cmd = args.cmd
    if cmd[0] == '--':
        kwargs['cmd'] = cmd[1:]
    result = mrun(**kwargs)
    returncode = 0
    for cwd, status in result.items():
        msg = format_complete_process(cwd, status)
        print(msg)
        returncode += status.returncode
    exit(returncode)


if __name__ == '__main__':
    args = cmdargs()
    main(args)
