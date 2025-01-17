from __future__ import annotations

import collections
from collections.abc import Callable
import io
import os
import re
from typing import NamedTuple

import hypothesis
import hypothesis.strategies as st
import pytest

from dconeybe.testing.assertions import contains_with_non_abutting_text
from dconeybe.testing.exception_notes import ExceptionNotes
from dconeybe.testing.hypothesis import disable_function_scoped_fixture_health_check as hypothesis_disable_function_scoped_fixture_health_check
from dconeybe.xonsh.aliases import rnd
from dconeybe.xonsh.testing import FakeSubprocessSpec
from dconeybe.xonsh.typing import Stdout, SubprocessSpec

class TestRndWithEmptyArgs:

  def test_should_not_write_to_stderr(self, rnd_args: RndArgs):
    rnd.rnd([], *rnd_args)

    stderr_string = rnd_args.stderr.getvalue()
    assert stderr_string == ""

  def test_should_return_zero(self, rnd_args: RndArgs):
    rnd_return_value = rnd.rnd([], *rnd_args)

    assert rnd_return_value == 0

  def test_stdout_should_end_with_newline(self, rnd_args: RndArgs):
    rnd.rnd([], *rnd_args)

    stdout_string = rnd_args.stdout.getvalue()
    assert stdout_string.endswith("\n")

  def test_should_generate_string_with_default_length(self, rnd_args: RndArgs):
    rnd.rnd([], *rnd_args)

    result = rnd_args.stdout.getvalue().strip()
    assert len(result) == 10

  def test_should_generate_unique_strings(self, rnd_args_factory: RndArgsFactory):
    results: list[Stdout] = []
    for _ in range(100):
      rnd_args = rnd_args_factory()
      rnd.rnd([], *rnd_args)
      results.append(rnd_args.stdout.getvalue().strip())

    counts = collections.defaultdict(lambda: 0)
    for result in results:
      counts[result] += 1
    for (result, count) in counts.items():
      with ExceptionNotes(f"result={result!r}", f"results={results!r}"):
        assert count == 1


class TestRndWithLength:

  @hypothesis.given(length=st.integers(min_value=1, max_value=100))
  @hypothesis_disable_function_scoped_fixture_health_check
  @pytest.mark.parametrize("length_arg", ["-n", "--length"])
  def test_should_write_string_of_given_length(
      self,
      rnd_args_factory: RndArgsFactory,
      length_arg: str,
      length: int,
  ):
    rnd_args = rnd_args_factory()
    rnd.rnd([length_arg, str(length)], *rnd_args)

    generated_string = rnd_args.stdout.getvalue().strip()
    assert len(generated_string) == length

  @hypothesis.given(length=st.integers(min_value=-100000, max_value=0))
  @hypothesis.example(length=0)
  @hypothesis_disable_function_scoped_fixture_health_check
  def test_should_fail_with_non_positive_length(
      self,
      rnd_args_factory: RndArgsFactory,
      length: int,
  ):
    rnd_args = rnd_args_factory()
    exit_code = rnd.rnd([f"--length={length}"], *rnd_args)

    assert exit_code == 2
    stderr_text = rnd_args.stderr.getvalue()
    assert contains_with_non_abutting_text(stderr_text, "must be greater than zero")
    assert contains_with_non_abutting_text(stderr_text, str(length))


class RndArgs(NamedTuple):
  stdout: io.StringIO()
  stderr: io.StringIO()
  spec: SubprocessSpec

  @staticmethod
  def new_test_instance() -> RndArgs:
    return RndArgs(
        stdout = io.StringIO(),
        stderr = io.StringIO(),
        spec = FakeSubprocessSpec("cg8xk8mkkb"),
    )


@pytest.fixture
def rnd_args() -> RndArgs:
  return RndArgs.new_test_instance()


@pytest.fixture
def rnd_args_factory() -> RndArgsFactory:
  return RndArgs.new_test_instance


RndArgsFactory = Callable[[], RndArgs]


ALPHABET_LETTERS = "abcdefghjkmnpqrstvwxyz"
ALPHABET_NUMBERS = "23456789"
ALPHABET = ALPHABET_LETTERS + ALPHABET_NUMBERS
