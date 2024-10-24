import argparse
import logging
import json
import sys

def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("files", nargs="*", help="The files to parse; parses stdin if no files specified")
  args = arg_parser.parse_args()
  del arg_parser
  files = args.files
  del args

  if len(files) == 0:
    logging.info("Reading from stdin...")
    data = json.load(sys.stdin.buffer)
    json.dump(data, sys.stdout, indent=2)
  else:
    for file in files:
      logging.info("Formatting %s", file)
      with open(file, "rb") as f:
        data = json.load(f)
      with open(file, "wt", encoding="utf8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
  main()
