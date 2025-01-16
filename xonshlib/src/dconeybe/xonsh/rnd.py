import argparse
import os
import random
import subprocess
import textwrap

from collections.abc import Sequence
from typing import NamedTuple


class RndResult(NamedTuple):
  stdout: str | None
  stderr: str | None
  exit_code: int


def rnd(args: Sequence[str]) -> RndResult | str:
  arg_parser = _RndArgumentParser()
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
    
  if parsed_args.generate_type in (None, "string"):
    random_characters = random.choices(_ALPHABET, k=parsed_args.length)
    random_characters = list(random_characters)
    if parsed_args.first_char_alpha:
      random_characters[0] = random.choice(_ALPHABET_LETTERS)
    result = "".join(random_characters)
  elif parsed_args.generate_type == "int32":
    result = random.randint(-(2**31), (2**31)-1)
  elif parsed_args.generate_type == "uint32":
    result = random.randint(0, 2**32)
  elif parsed_args.generate_type == "int64":
    result = random.randint(-(2**63), (2**63)-1)
  elif parsed_args.generate_type == "uint64":
    result = random.randint(0, 2**64)
  else:
    raise Exception(
      f"INTERNAL ERROR: unsupported generate_type: {parsed_args.generate_type}"
      + " (error code apd622j9pz)"
    )

  return str(result)


_ALPHABET_LETTERS = "abcdefghjkmnpqrstvwxyz"
_ALPHABET_NUMBERS = "23456789"
_ALPHABET = _ALPHABET_LETTERS + _ALPHABET_NUMBERS


class _RndArgumentParser(argparse.ArgumentParser):
  def __init__(self):
    super().__init__(
      prog="rnd",
      usage="%(prog)s [options] [--help]",
      exit_on_error=False,
    )
    self.register(
      "type",
      "positive_int",
      self._positive_int_type
    )
    self.add_argument(
      "-n", "--length",
      type="positive_int",
      default=10,
      help="The number of characters in the random string (default: %(default)s)"
    )
    first_char_alpha_arg = self.add_argument(
      "--first-char-alpha",
      action="store_true",
      default=True,
      help=textwrap.dedent("""
        Ensure that the first character of the generated string is a letter,
        as opposed to a number. (default: %(default)s)
      """).strip()
    )
    self.add_argument(
      "--no-first-char-alpha",
      dest=first_char_alpha_arg.dest,
      action="store_false",
      help=textwrap.dedent(f"""
        Removes the requirement that the first character of the generated
        string will be a letter, making it possible for the first character
        to be either a letter or a number. This is the opposite of
        {"/".join(first_char_alpha_arg.option_strings)}.
      """).strip()
    )
    self.add_argument(
      "--string",
      dest="generate_type",
      action="store_const",
      const="string",
      help="Generate a string (this is the default)"
    )
    self.add_argument(
      "--uint32", "--u32",
      dest="generate_type",
      action="store_const",
      const="uint32",
      help="Generate a 32-bit unsigned integer"
    )
    self.add_argument(
      "--int32", "--i32",
      dest="generate_type",
      action="store_const",
      const="int32",
      help="Generate a 32-bit signed integer"
    )
    self.add_argument(
      "--uint64", "--u64",
      dest="generate_type",
      action="store_const",
      const="uint64",
      help="Generate a 64-bit unsigned integer"
    )
    self.add_argument(
      "--int64", "--i64",
      dest="generate_type",
      action="store_const",
      const="int32",
      help="Generate a 32-bit signed integer"
    )

  def exit(self, status=0, message=None):
    raise self.Exit(status, message)

  class Exit(Exception):
    def __init__(self, status, message):
      super().__init__(message)
      self.message = message
      self.status = status

  @staticmethod
  def _positive_int_type(s):
    try:
      int_value = int(s)
    except ValueError:
      raise argparse.ArgumentTypeError(f"not a number: {s}")
      
    if int_value <= 0:
      raise argparse.ArgumentTypeError(f"must be greater than zero: {s}")

    return int_value
