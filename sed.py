"""
Syntax: %s [options] <search_pattern> <replacement_pattern> [files]

Searches for the leftmost non-overlapping occurrences of a regular expression in a file or files and
replaces them with the given replacement.

By default, the result of the match is printed to standard output. If multiple files are processed
then their filtered results are printed to standard output one after the other. Reading and writing
is always done in UTF-8 encoding.

Positional Arguments:

<search_pattern> is a regular expression that can be parsed by Python's `re` module
  (https://docs.python.org/3/library/re.html#regular-expression-syntax).

<replacement_pattern> is the string with which to replace the found occurrences of the given
  regular expression. Some backslash escapes are processed, such as \n is interpreted as a newline
  and \r is interpreted as a carriage return character. Back references using \1, \2, etc. are also
  recognized.

[files] are zero or more files and/or directories. If zero are specified then the input to process
  is read from standard input. Otherwise, each file is interpreted as a "glob" pattern recognized by
  Python's `glob.glob()` function (https://docs.python.org/3/library/glob.html#glob.glob). That is,
  * matches zero or more characters, ? matches a single character, and [seq] matches any character
  in `seq`. Additionally, ** performs a recursive match.
"""

from __future__ import annotations

from collections.abc import Sequence
import dataclasses
import glob
import pathlib
import re
import sys
from typing import Literal

from absl import app
from absl import flags
from absl import logging


FLAG_IN_PLACE = flags.DEFINE_boolean(
    "i", False, "Modify files in-place rather than printing the results to standard output."
)

FLAG_OUTPUT_FILE = flags.DEFINE_string(
    "o",
    None,
    """
  The file to which to write the filtered results rather that to standard output.
  The directory of this file will _not_ be created automatically.
  The empty string can be specified to explicitly indicate to write to standard output.
  """,
)


@dataclasses.dataclass(frozen=True)
class Symbol:
  name: str


INPLACE = Symbol("INPLACE")
STDOUT = Symbol("STDOUT")


def main(argv: Sequence[str]) -> None:
  try:
    args = parseCommandLineArguments(argv)
  except CommandLineArgumentsParseError as e:
    print(f"ERROR: {e}", file=sys.stderr)
    print("Run with --help for help", file=sys.stderr)
    return 2

  try:
    search_expr = re.compile(args.search_pattern)
  except re.error as e:
    print(f"ERROR: invalid regular expression: {args.search_pattern} ({e})", file=sys.stderr)
    return 2

  if len(args.input_file_patterns) == 0:
    logging.debug("Reading input from standard input")
    input_text = sys.stdin.read()
    output_text = search_expr.sub(args.replacement_pattern, input_text)
    print_output_text(
        text=output_text,
        src=None,
        dest=args.output_dest,
    )
  else:
    for input_file_pattern in args.input_file_patterns:
      for input_file_str in glob.iglob(input_file_pattern, recursive=True):
        input_file = pathlib.Path(input_file_str)
        if not input_file.is_file():
          logging.debug("Skipping non-file: %s", input_file)
          continue

        logging.debug("Reading input from %s", input_file)
        with input_file.open("rt", encoding="utf8") as f:
          input_text = f.read()

        output_text = search_expr.sub(args.replacement_pattern, input_text)
        if output_text == input_text:
          logging.debug("Pattern not found in %s; skipping", input_file)
          continue

        print_output_text(
            text=output_text,
            src=input_file,
            dest=args.output_dest,
        )


@dataclasses.dataclass(frozen=True)
class CommandLineArguments:
  search_pattern: str
  replacement_pattern: str
  input_file_patterns: tuple[str, ...]
  output_dest: pathlib.Path | Literal[INPLACE, STDOUT]


class CommandLineArgumentsParseError(Exception):
  pass


def parseCommandLineArguments(argv: Sequence[str]) -> CommandLineArguments:
  if len(argv) > 1:
    search_pattern = argv[1]
  else:
    raise CommandLineArgumentsParseError("a <search_pattern> must be specified")

  if len(argv) > 2:
    replacement_pattern = argv[2]
  else:
    raise CommandLineArgumentsParseError("a <replacement_pattern> must be specified")

  if FLAG_IN_PLACE.value and FLAG_OUTPUT_FILE.value:
    raise CommandLineArgumentsParseError(
        f"At most one of -{FLAG_IN_PLACE.name} and -{FLAG_OUTPUT_FILE.name} may be specified, "
        "not both."
    )
  if FLAG_IN_PLACE.value:
    output_dest = INPLACE
  elif FLAG_OUTPUT_FILE.value:
    output_dest = pathlib.Path(FLAG_OUTPUT_FILE.value)
  else:
    output_dest = STDOUT

  return CommandLineArguments(
      search_pattern=search_pattern,
      replacement_pattern=replacement_pattern,
      input_file_patterns=tuple(argv[3:]),
      output_dest=output_dest,
  )


def print_output_text(
    text: str, src: pathlib.Path | None, dest: pathlib.Path | Literal[INPLACE, STDOUT]
) -> None:
  if dest is STDOUT or (dest is INPLACE and src is None):
    logging.debug("Writing result to standard output")
    sys.stdout.write(text)
  elif dest is INPLACE:
    logging.debug("Writing result to %s", src)
    with src.open("wt", encoding="utf8") as f:
      f.write(text)
  else:
    logging.debug("Writing result to %s", dest)
    with dest.open("wt", encoding="utf8") as f:
      f.write(text)


if __name__ == "__main__":
  app.run(main)
