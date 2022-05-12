#!/usr/bin/env python3

import os
import sys

def main():
  relative_paths = sys.argv[1:]
  if len(relative_paths) > 0:
    relative_paths_iter = relative_paths
  else:
    relative_paths_iter = (line.rstrip() for line in sys.stdin)

  for path in relative_paths_iter:
    abs_path = os.path.normpath(os.path.abspath(path))
    print(abs_path)

if __name__ == "__main__":
  main()
