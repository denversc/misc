from __future__ import annotations

import random
import textwrap
import typing

from collections.abc import Sequence
from typing import Literal, Protocol, TextIO

from dconeybe.xonsh.aliases.argparse import AliasArgumentParser
from dconeybe.xonsh.typing import ExitCode, SubprocessSpec


def rnd(
    args: Sequence[str],
    stdout: TextIO,
    stderr: TextIO,
    spec: SubprocessSpec,
) -> ExitCode:
  arg_parser = _RndArgumentParser(spec)
  arg_parse_result = arg_parser.parse_alias_args(args, stdout, stderr)
  if isinstance(arg_parse_result, int):
    return ExitCode(arg_parse_result)
  parsed_args: _RndParsedArgs = arg_parse_result
  del arg_parser
  del arg_parse_result

  match parsed_args.generate_type:
    case "string":
      random_characters = random.choices(_ALPHABET, k=parsed_args.length)
      random_characters = list(random_characters)
      if parsed_args.first_char_alpha:
        random_characters[0] = random.choice(_ALPHABET_LETTERS)
      result = "".join(random_characters)
    case "int32":
      result = random.randint(-(2**31), (2**31) - 1)
    case "uint32":
      result = random.randint(0, 2**32)
    case "int64":
      result = random.randint(-(2**63), (2**63) - 1)
    case "uint64":
      result = random.randint(0, 2**64)
    case _ as generate_type:
      typing.assert_never(parsed_args.generate_type)
      raise Exception(f"unsupported generate_type: {generate_type}" + " (error code apd622j9pz)")

  print(result, file=stdout)
  return ExitCode(0)


_ALPHABET_LETTERS = "abcdefghjkmnpqrstvwxyz"
_ALPHABET_NUMBERS = "23456789"
_ALPHABET = _ALPHABET_LETTERS + _ALPHABET_NUMBERS


class _RndParsedArgs(Protocol):
  length: int
  first_char_alpha: bool
  generate_type: Literal["string", "int32", "int64", "uint32", "uint64"]


class _RndArgumentParser(AliasArgumentParser[_RndParsedArgs]):

  def __init__(self, spec: SubprocessSpec) -> None:
    super().__init__(
        spec=spec,
        usage="%(prog)s [options]",
    )
    self.add_argument(
        "-n",
        "--length",
        type="positive_int",
        default=10,
        help="The number of characters in the random string (default: %(default)s)",
    )
    first_char_alpha_arg = self.add_argument(
        "--first-char-alpha",
        action="store_true",
        default=True,
        help=textwrap.dedent(
            """
        Ensure that the first character of the generated string is a letter,
        as opposed to a number. (default: %(default)s)
      """
        ).strip(),
    )
    self.add_argument(
        "--no-first-char-alpha",
        dest=first_char_alpha_arg.dest,
        action="store_false",
        help=textwrap.dedent(
            f"""
        Removes the requirement that the first character of the generated
        string will be a letter, making it possible for the first character
        to be either a letter or a number. This is the opposite of
        {"/".join(first_char_alpha_arg.option_strings)}.
      """
        ).strip(),
    )
    self.add_argument(
        "--string",
        dest="generate_type",
        action="store_const",
        const="string",
        default="string",
        help="Generate a string (this is the default)",
    )
    self.add_argument(
        "--uint32",
        "--u32",
        dest="generate_type",
        action="store_const",
        const="uint32",
        help="Generate a 32-bit unsigned integer",
    )
    self.add_argument(
        "--int32",
        "--i32",
        dest="generate_type",
        action="store_const",
        const="int32",
        help="Generate a 32-bit signed integer",
    )
    self.add_argument(
        "--uint64",
        "--u64",
        dest="generate_type",
        action="store_const",
        const="uint64",
        help="Generate a 64-bit unsigned integer",
    )
    self.add_argument(
        "--int64",
        "--i64",
        dest="generate_type",
        action="store_const",
        const="int32",
        help="Generate a 32-bit signed integer",
    )
