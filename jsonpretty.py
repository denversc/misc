import argparse
import logging
import json
import sys

def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("files", nargs="*", help="The files to parse; parses stdin if no files specified")
  arg_parser.add_argument("--ugly", action="store_true", default=False, help="Use the most compact representation.")
  args = arg_parser.parse_args()
  del arg_parser
  files = args.files
  indent = None if args.ugly else 2
  del args

  if len(files) == 0:
    logging.info("Reading from stdin...")
    data = json.load(sys.stdin.buffer)
    json.dump(data, sys.stdout, indent=indent)
  else:
    for file in files:
      logging.info("Formatting %s", file)
      with open(file, "rb") as f:
        data = json.load(f)
      with open(file, "wt", encoding="utf8") as f:
        json.dump(data, f, indent=indent)

if __name__ == "__main__":
  main()
