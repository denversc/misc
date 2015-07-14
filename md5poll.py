#!/usr/bin/env python

################################################################################
# md5poll.py
# By: Denver Coneybeare
# Jan 08, 2012
#
# Monitors a files and prints when their last-modified times or MD5 changes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from __future__ import print_function
from __future__ import unicode_literals

import hashlib
import os
import sys
import time

################################################################################

def main():
    if len(sys.argv) < 2:
        print("ERROR: expected file path as first argument", file=sys.stderr)
        return 2
    elif len(sys.argv) > 2:
        print("ERROR: unexpected argument: {}".format(sys.argv[2]), file=sys.stderr)
        return 2
    else:
        path = sys.argv[1]

    old_info = None
    last_message = None
    while True:
        new_info = calculate_md5(path)
        if old_info is None or old_info != new_info:
            time_str = time.strftime("%H:%M:%S")
            if new_info is None:
                message = "file does not exist"
            else:
                (md5_str, mtime_str) = new_info
                message = "MD5={} mtime={}".format(md5_str, mtime_str)

            if message != last_message:
                print("{} {} changed: {}".format(time_str, path, message))
                last_message = message

            old_info = new_info

        time.sleep(0.25)

################################################################################

def calculate_md5(path):
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        md5_calculator = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            else:
                md5_calculator.update(data)

    md5str = md5_calculator.hexdigest()

    stat_result = os.stat(path)
    mtime = stat_result.st_mtime
    mtime_t = time.localtime(mtime)
    mtime_str = time.strftime("%H:%M:%S", mtime_t)

    return (md5str, mtime_str)

################################################################################

if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        exit_code = 0

    sys.exit(exit_code)
