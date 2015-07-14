#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
import argparse
import sys
import time
import urllib2

def main():
    (url, dest_path) = parse_args()
    print("Downloading {} to {}".format(url, dest_path))
    with open(dest_path, "wb") as f:
        con = urllib2.urlopen(url)

        try:
            size_str = con.headers["Content-Length"]
        except KeyError:
            size = None
        else:
            print("File size: {} bytes".format(size_str))
            try:
                size = int(size_str)
            except ValueError:
                size = None

        last_update_time = time.time()
        num_bytes_received = 0
        chunk = con.read(8192)
        while chunk:
            num_bytes_received += len(chunk)
            f.write(chunk)

            cur_time = time.time()
            if cur_time - last_update_time > 5:
                print_percentage_complete_message(num_bytes_received, size)
                last_update_time = cur_time

            chunk = con.read(8192)

        print_percentage_complete_message(num_bytes_received, size)

def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("url")
    arg_parser.add_argument("dest_filename")
    parsed_args = arg_parser.parse_args()
    return (parsed_args.url, parsed_args.dest_filename)

def print_percentage_complete_message(num_bytes_received, total_size):
    message = "{} bytes received".format(num_bytes_received)
    if total_size > 0:
        percent_complete = (num_bytes_received * 100) / total_size
        message += " ({}% complete)".format(percent_complete)
    print(message)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("ERROR application terminated by keyboard interrupt", file=sys.stderr)
        sys.exit(1)

