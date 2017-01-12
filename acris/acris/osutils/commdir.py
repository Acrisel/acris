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

import os
import pprint
import filecmp
import difflib
import sys
import re
import itertools
from collections import namedtuple

DiffContent=namedtuple('DiffShellowContent', ['diff', 'folders_only_in_dir1', 'folders_only_in_dir2', 'files_only_in_dir1', 'files_only_in_dir2', 'diff_files', 'diff_detail'])

def check_match(path, regs=None, on_empty_ignore=True):
    ''' Return True if any of parts of path matches any regexp in ignore_re
    
        if ignore_re is empty, return on_empty_ignore
        
        Args:
            path: path to file or directory
            ignore_re: list of compiled regular expressions
    '''
    result=on_empty_ignore
    if regs:
        result=False
        parts=path.split(os.sep)
        for reg, part in itertools.product(regs, parts):
            matching=reg.match(part)
            matching=matching.group() if matching else None
            result=matching is not None
            if result: break
    return result

def print_block(block, top_sep=None, bottom_sep='-'):
    if not isinstance(block, list): block=[block]
    
    maxsize=max(map(lambda x: len(x), block))
    if top_sep is not None:
        print(top_sep * maxsize)
    for line in block:
        print(line)
    if bottom_sep is not None:
        print(bottom_sep * maxsize)

def get_artifacts(loc, ignore, followlinks):
    files=list()
    dirs=list()
    if not loc.endswith(os.sep): loc+=os.sep
    
    regs=list(map(lambda x: re.compile(x), ignore)) if len(ignore) > 0 else None 
    
    for dirpath, dirnames, filenames in os.walk(loc, followlinks=followlinks):
        relpath=dirpath[len(loc):]
        for dirname in dirnames: 
            name=os.path.join(relpath, dirname)
            ignore=check_match(name, regs, on_empty_ignore=False)
            if not ignore: dirs.append(name)
        for filename in filenames: 
            name=os.path.join(relpath, filename)
            ignore=check_match(name, regs, on_empty_ignore=False)
            if not ignore: files.append(name)
    return dirs, files

def print_file_diff_header(file, file1, file2):
    head=['diff of %s' % file, "file1: %s" % file1, 'file2: %s' % file2]
    print_block(head)

def commdir(dir1, dir2, ignore=[], detailed=False, followlinks=False, quiet=False, bool_result=True):
    ''' compares two directory structures and their files.
    
    commdir walks through two directories, dir1 and dir2. While walking, it aggregates information
    on the difference between the two structures and their content.
    
    If bool_result is True, commdir will return True if difference was found. 
    When False, it would return a DiffContent namedtuple with the following fields:
    
        - diff (boolean)
        - folders_only_in_dir1 (list)
        - folders_only_in_dir2 (list) 
        - files_only_in_dir1 (list)
        - files_only_in_dir2 (list) 
        - diff_files (list)
        - diff_detail (list)
     
    Args:
        dir1, dir2: two directories structure to compare.
        ignore: list of regular expression strings to ignore, when directory is ignored, all its sub folders are ignored too.
        detailed: if set, will generate detailed file level comparison.
        followlinks: if set, symbolic links will be followed.
        quiet: if set, information will not be printed to stdio.
        bool_result: instruct how the function would respond to caller (True: boolean or False: DiffContent)
        
    '''
    result=False
    
    # create inventory of object to compare:
    dir1_folders, dir1_files = get_artifacts(dir1, ignore=ignore, followlinks=followlinks)
    dir2_folders, dir2_files = get_artifacts(dir2, ignore=ignore, followlinks=followlinks)
    
    folders_only_in_1=sorted(list(set(dir1_folders) - set(dir2_folders) ) )
    if len(folders_only_in_1) > 0:
        result=True
        if not quiet:
            print_block('folders only in %s' % (dir1,), top_sep='-')
            for x in folders_only_in_1: print("  ", x)
            
    folders_only_in_2=sorted(list(set(dir2_folders) - set(dir1_folders) ))
    if len(folders_only_in_2) > 0:
        result=True
        if not quiet:
            print_block('folders only in %s' % (dir2,), top_sep='-')
            for x in folders_only_in_2: print("  ", x)
    
    files_only_in_1=sorted(list(set(dir1_files) - set(dir2_files) ) )
    if len(files_only_in_1) > 0:
        result=True
        if not quiet:
            print_block('files only in %s' % (dir1,), top_sep='-')
            for x in files_only_in_1: print("  ", x)
            
    files_only_in_2=sorted(list(set(dir2_files) - set(dir1_files) ))
    if len(files_only_in_2) > 0:
        result=True
        if not quiet:
            print_block('files only in %s' % (dir2,), top_sep='-')
            for x in files_only_in_2: print("  ", x)
    
    files_in_both=sorted(list(set(dir1_files) & set(dir2_files) ) )
    files_diff=list()
    for file in files_in_both:
        file1=os.path.join(dir1, file)
        file2=os.path.join(dir2, file)
        cmp=filecmp.cmp(file1, file2)
        if not cmp:
            files_diff.append((file, file1, file2))
    if len(files_diff) > 0:
        result=True
        diff_files=files_diff
        if not quiet:
            print_block('files different:', top_sep='-')
            for x in files_diff: print('  ',x[0])
    
    diff_detail=None
    if detailed:            
        for file, file1, file2 in files_diff:
            if not quiet:
                print_file_diff_header(file, file1, file2)
                with open(file1,'r') as f1, open(file2,'r') as f2:
                    try:
                        diff = difflib.ndiff(f1.readlines(),f2.readlines())  
                    except Exception as e:
                        print('Error: failed to diff: %s' % (repr(e), ))
                        continue
                    for i, line in enumerate(diff):
                        if line.startswith(' '): continue
                        sys.stdout.write(str(i) + ': ' +line)
            
    if bool_result:
        return result
    else:
        content=DiffContent(diff=result,
                            folders_only_in_dir1=folders_only_in_1, 
                            folders_only_in_dir2=folders_only_in_2,
                            files_only_in_dir1=files_only_in_1, 
                            files_only_in_dir2=files_only_in_2,
                            diff_files=[x[0] for x in diff_files], 
                            diff_detail=diff_detail)
        return content

def add_os_sep(x):
    if x.endswith(os.sep):
        return x
    else:
        return x+os.sep
    
def same_path_prefix(path1, path2, top=True):
    p1=add_os_sep(path1)
    p2=add_os_sep(path2)
    if p1.startswith(p2):
        return path2 if top else path1
    elif p2.startswith(p1):
        return path1 if top else path2
    else:
        return None
    
def reduce_folder(folders, top=True):
    '''
    take folders and reduce to the smallest prefix that would remove all
    '''
    to_folders=list()
    current_prefix=folders[0]
    
    for folder in folders:
        prefix=same_path_prefix(current_prefix, folder, top=top)
        if prefix:
            current_prefix=prefix
        else:
            to_folders.append(current_prefix)
            current_prefix=folder
            
    to_folders.append(current_prefix)
    return sorted(set(to_folders))
        
def sync_dirs(loc, missing_folders, cmd="mkdir -fp", msg="Create missing folders", quiet=False, top=True):    
    if len(missing_folders) > 0:
        if not quiet: print_block('%s %s:' % (msg, loc,), top_sep='-')
        missing_folders=reduce_folder(missing_folders, top=top)
        for x in missing_folders: 
            if not quiet: print("  %s %s" % (cmd, os.path.join(loc, x)))

def sync_files(source, target, missing_files, quiet=False):    
    if len(missing_files) > 0:
        if not quiet: print_block('Create missing %s files:' % (target,), top_sep='-')
        for x in missing_files: 
            if not quiet: print("  cp -f %s %s" % (os.path.join(source, x), os.path.join(target, x)))

def rm_files(loc, extra_files, quiet=False):    
    if len(extra_files) > 0:
        if not quiet: print_block('Remove extra %s files:' % (loc,), top_sep='-')
        for x in extra_files: 
            if not quiet: print("  rm -f %s" % (os.path.join(loc, x), ))

def merge_files(source, target, diff_files, merge='cp -f', quiet=False):    
    if len(diff_files) > 0:
        if not quiet: print_block('Merge different files:', top_sep='-')
        for x in diff_files: 
            if not quiet: print("  %s %s %s" % (merge, os.path.join(source, x), os.path.join(target, x)))
    
def show_sync_cmd(dir1, dir2, content, merge=False, quiet=False):
    folders_only_in_dir1=content.folders_only_in_dir1
    folders_only_in_dir2=content.folders_only_in_dir2
    files_only_in_dir1=content.files_only_in_dir1
    files_only_in_dir2=content.files_only_in_dir2
    diff_files=content.diff_files
    
    sync_dirs(dir2, folders_only_in_dir1, cmd="mkdir -fp", msg="Create missing folders", quiet=quiet, top=False)
    if merge: 
        sync_dirs(dir1, folders_only_in_dir2, cmd="rmdir -fr", msg="Remove extra folders", quiet=quiet, top=True)
    else:
        sync_dirs(dir2, folders_only_in_dir2, cmd="rmdir -fr", msg="Remove extra folders", quiet=quiet, top=True)
    
    sync_files(dir1, dir2, files_only_in_dir1, quiet=quiet)
    if merge: 
        rm_files(dir2, files_only_in_dir2, quiet=quiet)
    else:
        rm_files(dir2, files_only_in_dir2, quiet=quiet)
    
    merge_cmd='cp -f' if not merge else "diffmerge"
    merge_files(dir1, dir2, diff_files, merge=merge_cmd, quiet=quiet)
    
def show_summary(dir1, sir2, content, quiet=False):
    if not quiet:
        print_block('Summary:', top_sep='-')
        print("  Folders only in %s: %s" % (dir1, len(content.folders_only_in_dir1), ) )
        print("  Files only in %s: %s" % (dir1, len(content.files_only_in_dir1), ) )
        print("  Folders only in %s: %s" % (dir2, len(content.folders_only_in_dir2), ) )
        print("  Files only in %s: %s" % (dir2, len(content.files_only_in_dir2), ) )
        print("  Files different files: %s" % (len(content.diff_files), ) )
    

args_description='''
Reports differences in directory structure and content.

commdir.py will exit with 0 if directories found the same.
otherwise, it will exit with 1.
'''
args_epilog='''
example:
    python commdir.py --dir1 my_folder --dir2 other_folder --ignore __pycache__ .*DS_Store
'''

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description=args_description, epilog=args_epilog)
    parser.add_argument('--dir1', metavar='DIR1', type=str, nargs=1,
                    help='source folder for the comparison')
    parser.add_argument('--dir2', metavar='DIR2', type=str, nargs=1, 
                    help='target folder for the comparison')
    parser.add_argument('--quiet', dest='quiet', action='store_true',
                    help='avoid writing any report out, default: False')
    parser.add_argument('--out', metavar='REPORT', dest='out', nargs='?',
                    help='file to write report to, default: stdout')
    parser.add_argument('--follow', action='store_true',
                    help='follow links when walking folders, default: False')
    parser.add_argument('--detailed', action='store_true',
                    help='provide detailed file level diff, default: False')
    parser.add_argument('--sync-cmd', dest='sync_cmd', action='store_true',
                    help='provide commands that would align dirs and files, default: False')
    parser.add_argument('--merge', dest='merge', action='store_true',
                    help='when sync-cmd, set how diff commands would be resolved, default: dir1 is base.')
    parser.add_argument('--total', dest='total', action='store_true',
                    help='outputs summary.')
    parser.add_argument('--ignore', metavar='PATTERN', dest='ignore', type=str, nargs='*',
                    default=list(),
                    help='pattern to ignore')
    
    args = parser.parse_args()
    dir1=args.dir1[0]
    dir2=args.dir2[0]
    quiet=args.quiet
    
    # TODO: handle args.out

    result=commdir(dir1, dir2, ignore=args.ignore, detailed=args.detailed, followlinks=args.follow, quiet=quiet, bool_result=False)
    
    if args.sync_cmd:
        show_sync_cmd(dir1, dir2, result, merge=args.merge, quiet=quiet)
        
    if args.total:
        show_summary(dir1, dir2, result, quiet=quiet)
    
    diff=result.diff
    if not quiet: 
        msg='%s and %s are %s' % (dir1, dir2, 'same' if not diff else 'different')
        print(msg)
    
    exit(0 if not result else 1)
    
    
