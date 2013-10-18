#!/usr/bin/python

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import fnmatch
import os
import re
import sys

def main():
    config = parse_args()

    pattern = config.pattern
    pattern_normcase = os.path.normcase(pattern)
    pattern_regex = fnmatch.translate(pattern_normcase)
    match_expr = re.compile(pattern_regex)

    dir_paths = config.dir_path
    if not dir_paths:
        dir_paths = [os.getcwd()]

    run(match_expr, dir_paths)

def run(match_expr, dir_paths):
    for dir_path in dir_paths:
        for (cur_dir_path, dirnames, filenames) in os.walk(dir_path):
            for filename in filenames:
                filename_normcase = os.path.normcase(filename)
                match = match_expr.match(filename_normcase)
                if match is not None:
                    cur_path = os.path.join(cur_dir_path, filename)
                    print(cur_path)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("pattern",
        help="""The pattern of the filename to search for;
        may contain wildcard characters * and ?"""
    )
    parser.add_argument("dir_path",
        nargs="*",
        help="""The paths of the directories to search for the given path;
        may be specified more than once, in which case each directory will
        be searched in turn; if not specified, the current directory will
        be searched"""
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
