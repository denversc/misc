#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

def paths_from_stdin_iter():
    for line in sys.stdin:
        yield line.rstrip()

def main():
    relative_paths = sys.argv[1:]
    if len(relative_paths) > 0:
        relative_paths_iter = relative_paths
    else:
        relative_paths_iter = paths_from_stdin_iter()

    for path in relative_paths_iter:
        abs_path = os.path.normpath(os.path.abspath(path))
        print(abs_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
