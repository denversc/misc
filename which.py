#!/usr/bin/python

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import errno
import fnmatch
import os
import re
import sys

def main():
    config = parse_args()
    executables = config.executable
    warnings_enabled = config.warnings
    run(executables, warnings_enabled)

def run(executables, warnings_enabled):
    path_dirs = get_path_directories()
    exe_suffixes = get_exe_suffixes()

    for executable in executables:
        for path_dir in path_dirs:
            cur_path_matches = path_matches(executable, path_dir, exe_suffixes,
                warnings_enabled)
            for path_match in cur_path_matches:
                print(path_match)

def get_path_directories():
    try:
        path_str = os.environ["PATH"]
    except KeyError:
        path = [os.path.curdir]
    else:
        path = path_str.split(os.path.pathsep)

    return path

def get_exe_suffixes():
    try:
        exe_suffixes_str = os.environ["PATHEXT"]
    except KeyError:
        exe_suffixes = [".exe", ".bat"]
    else:
        exe_suffixes = exe_suffixes_str.split(os.path.pathsep)

    return exe_suffixes

def path_matches(executable, path_dir, exe_suffixes, warnings_enabled):
    try:
        path_dir_entries = os.listdir(path_dir)
    except OSError as e:
        if warnings_enabled:
            if e.errno == errno.ENOENT:
                print("WARNING: directory does not exist: {}"
                    .format(path_dir), file=sys.stderr)
            else:
                print("WARNING: unable to list directory: {} ({})"
                    .format(path_dir, e.strerror), file=sys.stderr)
    else:
        executable_norm = os.path.normcase(executable)
        path_dir_norm = os.path.normcase(path_dir)
        exe_suffixes_norm = [os.path.normcase(x) for x in exe_suffixes]

        for path_dir_entry in path_dir_entries:
            entry_path = os.path.join(path_dir, path_dir_entry)
            if os.path.isfile(entry_path):
                path_dir_entry_norm = os.path.normcase(path_dir_entry)
                if path_dir_entry_norm == executable_norm:
                    match = True
                else:
                    (path_dir_entry_filename, path_dir_entry_suffix) = \
                        os.path.splitext(path_dir_entry)
                    match = (len(path_dir_entry_suffix) > 0
                            and path_dir_entry_suffix in exe_suffixes_norm
                            and path_dir_entry_filename == executable_norm)

                if match:
                    yield entry_path

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("executable",
        nargs="+",
        help="""The name of the executable to search for;
        may be specified more than once to search for multiple executables"""
    )
    parser.add_argument("-w", "--warnings",
        action="store_true",
        default=False,
        help="""Print warnings that occur during the search""",
    )
    parser.add_argument("-W", "--no-warnings",
        action="store_false",
        dest="warnings",
        help="""Reverse the effects of -w if previously specified""",
    )
    parsed_args = parser.parse_args()
    return parsed_args

if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        print("ERROR: application terminated by keyboard interrupt",
            file=sys.stderr)
        exit_code = 1
    sys.exit(exit_code)
