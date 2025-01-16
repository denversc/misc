import argparse
import os

from collections.abc import Sequence
from typing import TextIO

from dconeybe.xonsh.aliases.typing import ExitCode, SubprocessSpec


def abspath(
  args: Sequence[str],
  stdout: TextIO,
  stderr: TextIO,
  spec: SubprocessSpec,
) -> ExitCode | None:
  arg_parser = _AbspathArgumentParser(spec.args[0])
  try:
    parsed_args = arg_parser.parse_args(args)
  except argparse.ArgumentError as e:
    print(f"ERROR: {e}", file=stderr)
    print("Run with -h/--help for help.", file=stderr)
    return 2
  except arg_parser.Exit as e:
    print(e.message, file=stdout if e.status == 0 else stderr)
    return e.status

  paths: tuple[str] = tuple(parsed_args.paths)
  for path in paths:
    print(os.path.abspath(os.path.normpath(os.path.expanduser(path))))


class _AbspathArgumentParser(argparse.ArgumentParser):
  def __init__(self, prog: str) -> None:
    super().__init__(
      prog=prog,
      usage="%(prog)s [options] [paths] [--help]",
      exit_on_error=False,
    )
    self.add_argument(
      "paths",
      nargs="+",
      default=[],
      help="The paths whose absolute path to print."
    )

  def exit(self, status=0, message=None):
    raise self.Exit(status, message)

  class Exit(Exception):
    def __init__(self, status, message):
      super().__init__(message)
      self.message = message
      self.status = status
