from __future__ import annotations

import os

from collections.abc import Sequence
from typing import Protocol, TextIO

from dconeybe.xonsh.aliases.argparse import AliasArgumentParser
from dconeybe.xonsh.typing import ExitCode, SubprocessSpec


def abspath(
    args: Sequence[str],
    stdout: TextIO,
    stderr: TextIO,
    spec: SubprocessSpec,
) -> ExitCode:
  arg_parser = _AbspathArgumentParser(spec.args[0])
  arg_parse_result = arg_parser.parse_alias_args(args, stdout, stderr)
  if isinstance(arg_parse_result, int):
    return ExitCode(arg_parse_result)
  parsed_args: _AbspathParsedArgs = arg_parse_result
  del arg_parser
  del arg_parse_result

  for path in parsed_args.paths:
    print(os.path.abspath(os.path.normpath(os.path.expanduser(path))))

  return ExitCode(0)


class _AbspathParsedArgs(Protocol):
  paths: Sequence[str]


class _AbspathArgumentParser(AliasArgumentParser[_AbspathParsedArgs]):

  def __init__(self, prog: str) -> None:
    super().__init__(
        prog=prog,
        usage="%(prog)s [options] <path> [path2 [path3 [ ... ]]]",
    )
    self.add_argument(
        "paths", nargs="+", default=[], help="The paths whose absolute path to print."
    )
