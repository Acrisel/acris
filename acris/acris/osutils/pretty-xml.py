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

import xml.dom.minidom
import argparse
import sys

parser = argparse.ArgumentParser(description='Pretty prints XML file that is not pretty.')
parser.add_argument("input_files", metavar='XML', nargs='*', help="XML files to pretty print; if - or none provided, stdin is assumed")
parser.add_argument("-o", "--out", metavar='OUTFILE',help="output filename; defaults to stdout")
args = parser.parse_args()

output_fh=sys.stdout
if args.out:
    output_fh=open(args.out, 'w')

input_files=args.input_files
if not input_files:
    input_files=['-']
    
for input_file in input_files:
    if input_file == '-':
        input_fh=sys.stdin
    else:
        input_fh=open(input_file)

    xml_string=input_fh.read()

    if input_file != '-':
        input_fh.close()
        
    # xml = xml.dom.minidom.parse(xml_fname) # by file name
    xml_data=xml.dom.minidom.parseString(xml_string) # by string
    pretty_xml_as_string = xml_data.toprettyxml(indent='    ')

    output_fh.write(pretty_xml_as_string)

if args.out:
    output_fh.close()
