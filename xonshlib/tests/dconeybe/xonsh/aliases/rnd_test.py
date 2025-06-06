from __future__ import annotations

import collections
from collections.abc import Callable, Iterable
import dataclasses
import io
import re
from typing import NamedTuple, Self, Sequence
from unittest import mock

import hypothesis
import hypothesis.strategies as st
import pytest

from dconeybe.testing.assertions import contains_with_non_abutting_text
from dconeybe.testing.hypothesis import disable_function_scoped_fixture_health_check as hypothesis_disable_function_scoped_fixture_health_check  # noqa: E501
from dconeybe.xonsh.aliases import rnd
from dconeybe.xonsh.testing import FakeSubprocessSpec
from dconeybe.xonsh.typing import SubprocessSpec


class TestRndStringGeneratedType:

  string_generating_args = ((), ("--string",))

  @pytest.mark.parametrize("args", string_generating_args)
  def test_should_generate_string_with_default_length(self, rnd_args: RndArgs, args: Sequence[str]):
    rnd.rnd(args, *rnd_args)

    result = rnd_args.stdout.getvalue().strip()
    assert len(result) == 10

  @pytest.mark.parametrize("args", string_generating_args)
  def test_should_generate_unique_values(
      self, rnd_args_factory: RndArgsFactory, args: Sequence[str]
  ):
    outputs: list[str] = []
    for _ in range(100):
      rnd_args = rnd_args_factory()
      rnd.rnd(args, *rnd_args)
      outputs.append(rnd_args.stdout.getvalue().strip())

    counts: dict[str, int] = collections.defaultdict(lambda: 0)
    for output in outputs:
      counts[output] += 1
    for output, count in counts.items():
      assert count == 1, f"output={output!r}, outputs={outputs!r}"

  @pytest.mark.parametrize("args", string_generating_args)
  def test_should_not_write_to_stderr(self, rnd_args: RndArgs, args: Sequence[str]):
    rnd.rnd(args, *rnd_args)

    stderr_string = rnd_args.stderr.getvalue()
    assert stderr_string == ""

  @pytest.mark.parametrize("args", string_generating_args)
  def test_should_return_zero(self, rnd_args: RndArgs, args: Sequence[str]):
    exit_code = rnd.rnd(args, *rnd_args)

    assert exit_code == 0

  @pytest.mark.parametrize("args", string_generating_args)
  def test_stdout_should_end_with_newline(self, rnd_args: RndArgs, args: Sequence[str]):
    rnd.rnd(args, *rnd_args)

    stdout_string = rnd_args.stdout.getvalue()
    assert stdout_string.endswith("\n")


class TestRndIntGeneratedTypes:

  @dataclasses.dataclass(frozen=True)
  class TypeArgInfo:
    arg: str
    min_value: int
    max_value: int

    @classmethod
    def all(cls) -> Iterable[Self]:
      for arg in ["--int32", "--i32"]:
        yield cls(
            arg=arg,
            min_value=-(2**31),
            max_value=(2**31) - 1,
        )
      for arg in ["--int64", "--i64"]:
        yield cls(
            arg=arg,
            min_value=-(2**63),
            max_value=(2**63) - 1,
        )
      for arg in ["--uint32", "--u32"]:
        yield cls(
            arg=arg,
            min_value=0,
            max_value=2**32,
        )
      for arg in ["--uint64", "--u64"]:
        yield cls(
            arg=arg,
            min_value=0,
            max_value=2**64,
        )

  type_arg_infos = tuple(TypeArgInfo.all())

  @pytest.mark.parametrize("type_arg", type_arg_infos)
  def test_should_produce_int_within_its_valid_range(
      self,
      rnd_args: RndArgs,
      type_arg: TypeArgInfo,
  ):
    rnd.rnd([type_arg.arg], *rnd_args)

    output = rnd_args.stdout.getvalue().strip()
    assert int(output) >= type_arg.min_value
    assert int(output) <= type_arg.max_value

  @pytest.mark.parametrize("type_arg", type_arg_infos)
  def test_should_generate_unique_values(
      self,
      rnd_args_factory: RndArgsFactory,
      type_arg: TypeArgInfo,
  ):
    outputs: list[str] = []
    for _ in range(100):
      rnd_args = rnd_args_factory()
      rnd.rnd([type_arg.arg], *rnd_args)
      outputs.append(rnd_args.stdout.getvalue().strip())

    counts: dict[str, int] = collections.defaultdict(lambda: 0)
    for output in outputs:
      counts[output] += 1
    for output, count in counts.items():
      assert count == 1, f"output={output!r}, outputs={outputs!r}"

  @pytest.mark.parametrize("type_arg", type_arg_infos)
  def test_should_not_write_to_stderr(
      self,
      rnd_args: RndArgs,
      type_arg: TypeArgInfo,
  ):
    rnd.rnd([type_arg.arg], *rnd_args)

    assert len(rnd_args.stderr.getvalue()) == 0

  @pytest.mark.parametrize("type_arg", type_arg_infos)
  def test_should_return_zero(
      self,
      rnd_args: RndArgs,
      type_arg: TypeArgInfo,
  ):
    exit_code = rnd.rnd([type_arg.arg], *rnd_args)

    assert exit_code == 0

  @pytest.mark.parametrize("type_arg", type_arg_infos)
  def test_stdout_should_end_with_newline(
      self,
      rnd_args: RndArgs,
      type_arg: TypeArgInfo,
  ):
    rnd.rnd([type_arg.arg], *rnd_args)

    stdout_string = rnd_args.stdout.getvalue()
    assert stdout_string.endswith("\n")


class TestRndLengthArgument:

  @hypothesis.given(length=st.integers(min_value=1, max_value=100))
  @hypothesis_disable_function_scoped_fixture_health_check
  @pytest.mark.parametrize("length_arg", ["-l", "--length"])
  def test_should_write_string_of_given_length(
      self,
      rnd_args_factory: RndArgsFactory,
      length_arg: str,
      length: int,
  ):
    rnd_args = rnd_args_factory()
    exit_code = rnd.rnd([length_arg, str(length)], *rnd_args)

    generated_string = rnd_args.stdout.getvalue().strip()
    assert len(generated_string) == length
    assert exit_code == 0

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

    stderr_text = rnd_args.stderr.getvalue()
    assert contains_with_non_abutting_text(stderr_text, "must be greater than zero")
    assert contains_with_non_abutting_text(stderr_text, str(length))
    assert exit_code == 2

  @hypothesis.given(length=st.text())
  @hypothesis.example(length="")
  @hypothesis_disable_function_scoped_fixture_health_check
  def test_should_fail_with_non_integer_length(
      self,
      rnd_args_factory: RndArgsFactory,
      length: str,
  ):
    hypothesis.assume(not can_be_parsed_as_int(length))
    rnd_args = rnd_args_factory()
    exit_code = rnd.rnd([f"--length={length}"], *rnd_args)

    stderr_text = rnd_args.stderr.getvalue()
    assert contains_with_non_abutting_text(stderr_text, "not a number")
    assert contains_with_non_abutting_text(stderr_text, length)
    assert exit_code == 2

  @hypothesis.given(length=st.integers(min_value=1, max_value=100))
  @hypothesis_disable_function_scoped_fixture_health_check
  @pytest.mark.parametrize("generated_type_arg", ["--int32", "--int64", "--uint32", "--uint64"])
  def test_should_ignore_length_when_non_string_values_are_generated(
      self,
      rnd_args_factory: RndArgsFactory,
      length: int,
      generated_type_arg: str,
  ):
    rnd_args_with_length = rnd_args_factory()
    exit_code_with_length = rnd.rnd(
        [generated_type_arg, f"--length={length}"], *rnd_args_with_length
    )
    rnd_args_without_length = rnd_args_factory()
    exit_code_without_length = rnd.rnd([generated_type_arg], *rnd_args_without_length)

    assert exit_code_with_length == exit_code_without_length
    assert rnd_args_with_length.stderr.getvalue() == rnd_args_without_length.stderr.getvalue()
    assert re.match(r"-?\d+", rnd_args_with_length.stdout.getvalue().strip())
    assert re.match(r"-?\d+", rnd_args_without_length.stdout.getvalue().strip())


class TestRndFirstCharAlphaArgument:

  @pytest.mark.parametrize("args", [(), ("--first-char-alpha",)])
  def test_none_of_the_first_char_alpha_arguments_specified(
      self,
      rnd_args_factory: RndArgsFactory,
      args: Sequence[str],
  ):
    for i in range(100):
      rnd_args = rnd_args_factory()
      rnd.rnd(args, *rnd_args)
      stdout_string = rnd_args.stdout.getvalue().strip()
      assert stdout_string[0].isalpha(), f"i={i}, stdout_string={stdout_string!r}"

  def test_no_first_char_alpha_specified(self, rnd_args_factory: RndArgsFactory):
    generated_strings: list[str] = []
    for _ in range(100):
      rnd_args = rnd_args_factory()
      rnd.rnd(["--no-first-char-alpha"], *rnd_args)
      generated_strings.append(rnd_args.stdout.getvalue().strip())

    count_with_first_char_alpha = sum(
        (1 if generated_string[0].isalpha() else 0) for generated_string in generated_strings
    )
    assert count_with_first_char_alpha < 90, f"generated_strings={generated_strings!r}"


class TestRndCountArgument:

  @hypothesis.given(count=st.integers(min_value=0, max_value=100))
  @hypothesis_disable_function_scoped_fixture_health_check
  @pytest.mark.parametrize("count_arg", ["-n", "--count"])
  def test_should_write_requested_number_of_strings(
      self,
      rnd_args_factory: RndArgsFactory,
      count_arg: str,
      count: int,
  ):
    rnd_args = rnd_args_factory()
    exit_code = rnd.rnd([count_arg, str(count)], *rnd_args)

    generated_string = rnd_args.stdout.getvalue().strip()
    generated_lines = generated_string.splitlines()
    assert len(generated_lines) == count
    assert exit_code == 0

  @hypothesis.given(count=st.integers(min_value=-100000, max_value=-1))
  @hypothesis.example(count=-1)
  @hypothesis_disable_function_scoped_fixture_health_check
  def test_should_fail_with_non_negative_count(
      self,
      rnd_args_factory: RndArgsFactory,
      count: int,
  ):
    rnd_args = rnd_args_factory()
    exit_code = rnd.rnd([f"--count={count}"], *rnd_args)

    stderr_text = rnd_args.stderr.getvalue()
    assert contains_with_non_abutting_text(stderr_text, "must be greater than or equal to zero")
    assert contains_with_non_abutting_text(stderr_text, str(count))
    assert exit_code == 2

  @hypothesis.given(count=st.text())
  @hypothesis.example(count="")
  @hypothesis_disable_function_scoped_fixture_health_check
  def test_should_fail_with_non_integer_count(
      self,
      rnd_args_factory: RndArgsFactory,
      count: str,
  ):
    hypothesis.assume(not can_be_parsed_as_int(count))
    rnd_args = rnd_args_factory()
    exit_code = rnd.rnd([f"--count={count}"], *rnd_args)

    stderr_text = rnd_args.stderr.getvalue()
    assert contains_with_non_abutting_text(stderr_text, "not a number")
    assert contains_with_non_abutting_text(stderr_text, count)
    assert exit_code == 2


class TestRndCopyToClipboardArgument:

  COPY_ARGS = ("-c", "--copy-to-clipboard")
  NOCOPY_ARGS = ("-C", "--no-copy-to-clipboard")

  def test_should_copy_to_clipboard_by_default(
      self,
      rnd_args_factory: RndArgsFactory,
      mock_copykitten: mock.Mock,
  ):
    self.assert_copies_to_clipboard(
        args=[],
        expect_copy=True,
        rnd_args_factory=rnd_args_factory,
        mock_copykitten=mock_copykitten,
    )

  @pytest.mark.parametrize("copy_arg", COPY_ARGS)
  def test_should_copy_to_clipboard_if_specified(
      self,
      rnd_args_factory: RndArgsFactory,
      mock_copykitten: mock.Mock,
      copy_arg: str,
  ):
    self.assert_copies_to_clipboard(
        args=[copy_arg],
        expect_copy=True,
        rnd_args_factory=rnd_args_factory,
        mock_copykitten=mock_copykitten,
    )

  @pytest.mark.parametrize("nocopy_arg", NOCOPY_ARGS)
  def test_should_not_copy_to_clipboard_if_specified(
      self,
      rnd_args_factory: RndArgsFactory,
      mock_copykitten: mock.Mock,
      nocopy_arg: str,
  ):
    self.assert_copies_to_clipboard(
        args=[nocopy_arg],
        expect_copy=False,
        rnd_args_factory=rnd_args_factory,
        mock_copykitten=mock_copykitten,
    )

  @pytest.mark.parametrize("copy_arg", COPY_ARGS)
  @pytest.mark.parametrize("nocopy_arg", NOCOPY_ARGS)
  def test_should_copy_if_last_arg_specifies_to_copy(
      self,
      rnd_args_factory: RndArgsFactory,
      mock_copykitten: mock.Mock,
      copy_arg: str,
      nocopy_arg: str,
  ):
    self.assert_copies_to_clipboard(
        args=[nocopy_arg, copy_arg],
        expect_copy=True,
        rnd_args_factory=rnd_args_factory,
        mock_copykitten=mock_copykitten,
    )

  @pytest.mark.parametrize("copy_arg", COPY_ARGS)
  @pytest.mark.parametrize("nocopy_arg", NOCOPY_ARGS)
  def test_should_not_copy_if_last_arg_specifies_to_not_copy(
      self,
      rnd_args_factory: RndArgsFactory,
      mock_copykitten: mock.Mock,
      copy_arg: str,
      nocopy_arg: str,
  ):
    self.assert_copies_to_clipboard(
        args=[copy_arg, nocopy_arg],
        expect_copy=False,
        rnd_args_factory=rnd_args_factory,
        mock_copykitten=mock_copykitten,
    )

  def assert_copies_to_clipboard(
      self,
      args: Sequence[str],
      expect_copy: bool,
      rnd_args_factory: RndArgsFactory,
      mock_copykitten: mock.Mock,
  ) -> None:
    rnd_args = rnd_args_factory()
    exit_code = rnd.rnd(args, *rnd_args)

    assert exit_code == 0
    rnd_output = rnd_args.stdout.getvalue()
    assert len(rnd_output) > 0
    if expect_copy:
      mock_copykitten.copy.assert_called_once_with(rnd_output.strip())
    else:
      mock_copykitten.copy.assert_not_called()


class TestRndReportsInvalidArgs:

  def test_invalid_arg(self, rnd_args: RndArgs):
    exit_code = rnd.rnd(["--c2btdhxxwe"], *rnd_args)

    assert exit_code == 2
    stderr_string = rnd_args.stderr.getvalue()
    assert contains_with_non_abutting_text(stderr_string, "c2btdhxxwe")
    assert len(rnd_args.stdout.getvalue()) == 0


class RndArgs(NamedTuple):
  stdout: io.StringIO
  stderr: io.StringIO
  spec: SubprocessSpec

  @staticmethod
  def new_test_instance() -> RndArgs:
    return RndArgs(
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        spec=FakeSubprocessSpec(["cg8xk8mkkb"]),
    )


@pytest.fixture
def rnd_args() -> RndArgs:
  return RndArgs.new_test_instance()


@pytest.fixture
def rnd_args_factory() -> RndArgsFactory:
  return RndArgs.new_test_instance


RndArgsFactory = Callable[[], RndArgs]


def can_be_parsed_as_int(s: str) -> bool:
  try:
    int(s)
  except ValueError:
    return False
  else:
    return True


ALPHABET_LETTERS = "abcdefghjkmnpqrstvwxyz"
ALPHABET_NUMBERS = "23456789"
ALPHABET = ALPHABET_LETTERS + ALPHABET_NUMBERS


class MockCopykitten(mock.Mock):
  copy: mock.Mock


@pytest.fixture(autouse=True)
def mock_copykitten(monkeypatch: pytest.MonkeyPatch) -> MockCopykitten:
  mock_object = mock.create_autospec(rnd.copykitten, spec_set=True)
  monkeypatch.setattr(rnd, "copykitten", mock_object)
  return mock_object
