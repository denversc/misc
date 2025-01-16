import io
import os
import collections

from dconeybe.xonsh.aliases import rnd
from dconeybe.xonsh.aliases.typing import Stdout
from dconeybe.xonsh.testing.exception_notes import ExceptionNotes

def test_rnd_empty_args_should_end_with_newline():
  stdout, stderr = io.StringIO(), io.StringIO()
  rnd.rnd([], stdout, stderr)

  stdout_string = stdout.getvalue()
  assert stdout_string.endswith("\n")

def test_rnd_empty_args_should_not_write_to_stderr():
  stdout, stderr = io.StringIO(), io.StringIO()
  rnd.rnd([], stdout, stderr)

  assert stderr.getvalue() == ""

def test_rnd_empty_args_should_return_none():
  stdout, stderr = io.StringIO(), io.StringIO()
  rnd_return_value = rnd.rnd([], stdout, stderr)

  assert rnd_return_value is None

def test_rnd_empty_args_should_generate_string_with_default_length():
  stdout, stderr = io.StringIO(), io.StringIO()
  rnd.rnd([], stdout, stderr)

  result = stdout.getvalue().strip()
  assert len(result) == 10

def test_rnd_empty_args_should_generate_unique_strings():
  results: list[Stdout] = []
  for _ in range(100):
    stdout, stderr = io.StringIO(), io.StringIO()
    rnd.rnd([], stdout, stderr)
    results.append(stdout.getvalue().strip())

  counts = collections.defaultdict(lambda: 0)
  for result in results:
    counts[result] += 1
  for (result, count) in counts.items():
    with ExceptionNotes(f"result={result!r}", f"results={results!r}"):
      assert count == 1


ALPHABET_LETTERS = "abcdefghjkmnpqrstvwxyz"
ALPHABET_NUMBERS = "23456789"
ALPHABET = ALPHABET_LETTERS + ALPHABET_NUMBERS
