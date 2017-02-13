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
# based on Recipe 466302: Sorting big files the Python 2.4 way
# by Nicolas Lehuen
# fixed for python 3.x

@author: arnon
'''

import os
from tempfile import gettempdir
from itertools import islice, cycle
from collections import namedtuple
import heapq

Keyed = namedtuple("Keyed", ["key", "obj"])

def merge(key=None, *iterables):
    # based on code posted by Scott David Daniels in c.l.p.
    # http://groups.google.com/group/comp.lang.python/msg/484f01f1ea3c832d

    if key is None:
        keyed_iterables = iterables
    else:
        keyed_iterables = [(Keyed(key(obj), obj) for obj in iterable)
                            for iterable in iterables]
    for element in heapq.merge(*keyed_iterables):
        yield element.obj


def msort(input_, output, key=None, buffer_size=32000, tempdirs=None):
    if tempdirs is None:
        tempdirs = []
    if not tempdirs:
        tempdirs.append(gettempdir())

    chunks = []
    try:
        with open(input_,'rb',64*1024) as input_file:
            input_iterator = iter(input_file)
            for tempdir in cycle(tempdirs):
                current_chunk = list(islice(input_iterator,buffer_size))
                if not current_chunk:
                    break
                current_chunk.sort(key=key)
                output_chunk = open(os.path.join(tempdir,'%06i'%len(chunks)),'w+b',64*1024)
                chunks.append(output_chunk)
                output_chunk.writelines(current_chunk)
                output_chunk.flush()
                output_chunk.seek(0)
        with open(output,'wb',64*1024) as output_file:
            output_file.writelines(merge(key, *chunks))
    finally:
        for chunk in chunks:
            try:
                chunk.close()
                os.remove(chunk.name)
            except Exception:
                pass


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="""
Sort big data file.
""")
    parser.add_argument('-b', '--buffer', required=True, type=int, metavar='MEMSIZE', default=32000, dest='buffer_size',
                        help="""Size of the line buffer. The file to sort is divided into chunks of that many lines. Default : 32,000 lines.""")
    parser.add_argument('-k', '--key', type=str, required=False, metavar='KEY', dest='key',
                        help="""Python expression used to compute the key for each line, "lambda line:" is prepended. 
                                Example : -k "line[5:10]". By default, the whole line is the key.""")    
    parser.add_argument('-t', '--tempdir', action='append', metavar='DIR', default=[], dest='tempdirs',
                        help="""Temporary directory to use. You might get performance
                                improvements if the temporary directory is not on the same physical
                                disk than the input and output directories. You can even try
                                providing multiples directories on differents physical disks.
                                Use multiple -t options to do that.""")
    parser.add_argument('-p', '--psyco', action='store_true', required=False, default=False, dest='psyco',
                        help="""Use Psyco.""")
    parser.add_argument('input', type=str, metavar='INPUT',
                        help="""File to sort.""")
    parser.add_argument('output', type=str, metavar='OUTPUT',
                        help="""Sorted file to create.""")

    args = parser.parse_args()    
    
    if args.key:
        args.key = eval('lambda line : (%s)'% args.key)

    if args.psyco:
        try:
            import psyco
        except:
            raise Exception("psyco package could not be loaded.  To use -p option, psyco must be installed.")
        psyco.full()

    msort(args.input, args.output, args.key, args.buffer_size, args.tempdirs)
    

