from __future__ import annotations

import argparse
import typing
from typing import NoReturn, Sequence, TextIO

from dconeybe.xonsh.typing import ExitCode, SubprocessSpec


class AliasArgumentParser[T](argparse.ArgumentParser):

  def __init__(self, spec: SubprocessSpec, usage: str) -> None:
    super().__init__(
        prog=spec.args[0],
        usage=usage,
        exit_on_error=False,
    )
    self.register("type", "positive_int", self._positive_int_type)
    self.register("type", "nonnegative_int", self._nonnegative_int_type)

  def parse_alias_args(self, args: Sequence[str], stdout: TextIO, stderr: TextIO) -> ExitCode | T:
    try:
      parsed_args = super().parse_args(args)
    except argparse.ArgumentError as e:
      print(f"ERROR: {e}", file=stderr)
      print("Run with -h/--help for help.", file=stderr)
      return ExitCode(2)
    except self._Exit as e:
      if e.message:
        print(e.message, file=stdout if e.status == 0 else stderr)
      return ExitCode(e.status)
    else:
      return typing.cast(T, parsed_args)

  def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
    raise self._Exit(status, message)

  class _Exit(Exception):

    def __init__(self, status: int, message: str | None) -> None:
      super().__init__(message)
      self.message = message
      self.status = status

  @staticmethod
  def _positive_int_type(s: str) -> int:
    try:
      int_value = int(s)
    except ValueError:
      raise argparse.ArgumentTypeError(f"not a number: {s}")

    if int_value <= 0:
      raise argparse.ArgumentTypeError(f"must be greater than zero: {s}")

    return int_value

  @staticmethod
  def _nonnegative_int_type(s: str) -> int:
    try:
      int_value = int(s)
    except ValueError:
      raise argparse.ArgumentTypeError(f"not a number: {s}")

    if int_value < 0:
      raise argparse.ArgumentTypeError(f"must be greater than or equal to zero: {s}")

    return int_value
