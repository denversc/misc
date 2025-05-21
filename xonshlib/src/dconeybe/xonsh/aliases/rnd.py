from __future__ import annotations

import copykitten
import io
import random
import textwrap
import typing

from collections.abc import Callable, Sequence
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

  generate_random_value: Callable[[], object]
  match parsed_args.generate_type:
    case "string":
      random_string_generator = RandomStringGenerator(
          length=parsed_args.length,
          first_char_alpha=parsed_args.first_char_alpha,
      )
      generate_random_value = random_string_generator.generate_random_string
    case "int32":
      generate_random_value = generate_random_int32
    case "uint32":
      generate_random_value = generate_random_uint32
    case "int64":
      generate_random_value = generate_random_int64
    case "uint64":
      generate_random_value = generate_random_uint64
    case _ as generate_type:
      typing.assert_never(parsed_args.generate_type)
      raise Exception(f"unsupported generate_type: {generate_type}" + " (error code apd622j9pz)")

  output_buffer = io.StringIO()
  for _ in range(parsed_args.count):
    print(generate_random_value(), file=output_buffer)

  output = output_buffer.getvalue()
  stdout.write(output)
  if parsed_args.copy_to_clipboard:
    copykitten.copy(output)

  return ExitCode(0)


class RandomStringGenerator:

  _ALPHABET_LETTERS = "abcdefghjkmnpqrstvwxyz"
  _ALPHABET_NUMBERS = "23456789"
  _ALPHABET = _ALPHABET_LETTERS + _ALPHABET_NUMBERS

  def __init__(self, length: int, first_char_alpha: bool) -> None:
    self.length = length
    self.first_char_alpha = first_char_alpha

  def generate_random_string(self) -> str:
    random_characters = random.choices(self._ALPHABET, k=self.length)
    random_characters = list(random_characters)
    if self.first_char_alpha:
      random_characters[0] = random.choice(self._ALPHABET_LETTERS)
    return "".join(random_characters)


def generate_random_int32() -> int:
  return random.randint(-(2**31), (2**31) - 1)


def generate_random_uint32() -> int:
  return random.randint(0, 2**32)


def generate_random_int64() -> int:
  return random.randint(-(2**63), (2**63) - 1)


def generate_random_uint64() -> int:
  return random.randint(0, 2**64)


class _RndParsedArgs(Protocol):
  length: int
  count: int
  first_char_alpha: bool
  copy_to_clipboard: bool
  generate_type: Literal["string", "int32", "int64", "uint32", "uint64"]


class _RndArgumentParser(AliasArgumentParser[_RndParsedArgs]):

  def __init__(self, spec: SubprocessSpec) -> None:
    super().__init__(
        spec=spec,
        usage="%(prog)s [options]",
    )
    self.add_argument(
        "-n",
        "--count",
        type="nonnegative_int",
        default=1,
        help="The number of random values to generate (default: %(default)s)",
    )
    self.add_argument(
        "-l",
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
    copy_to_clipboard_arg = self.add_argument(
        "--copy-to-clipboard",
        "-c",
        dest="copy_to_clipboard",
        action="store_true",
        default=True,
        help="Copy the generated text to the clipboard (this is the default behavior)",
    )
    copy_to_clipboard_option_strings = sorted(copy_to_clipboard_arg.option_strings, key=len)
    self.add_argument(
        "--no-copy-to-clipboard",
        "-C",
        dest="copy_to_clipboard",
        action="store_false",
        help="Do NOT copy the generated text to the clipboard; "
        f"negates the effects of {"/".join(copy_to_clipboard_option_strings)}",
    )
