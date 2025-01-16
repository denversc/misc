import argparse
import pathlib

from collections.abc import Sequence
from typing import NamedTuple


class AbspathResult(NamedTuple):
  stdout: str | None
  stderr: str | None
  exit_code: int


def abspath(args: Sequence[str]) -> AbspathResult | str:
  arg_parser = _AbspathArgumentParser()
  try:
    parsed_args = arg_parser.parse_args(args)
  except argparse.ArgumentError as e:
    message = textwrap.dedent(f"""
      ERROR: {e}
      Run with -h/--help for help.
    """).strip()
    return (None, message, 2)
  except arg_parser.Exit as e:
    return (None, e.message, e.status)
    
  


class _AbspathArgumentParser(argparse.ArgumentParser):
  def __init__(self):
    super().__init__(
      prog="abspath",
      usage="%(prog)s [options] [--help]",
      exit_on_error=False,
    )
    self.add_argument(
      "paths",
      default=[],
      nargs="*",
      help="The paths to convert to absolute paths"
    )

  def exit(self, status=0, message=None):
    raise self.Exit(status, message)

  class Exit(Exception):
    def __init__(self, status, message):
      super().__init__(message)
      self.message = message
      self.status = status
