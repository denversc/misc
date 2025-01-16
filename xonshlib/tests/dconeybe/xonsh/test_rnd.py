import collections

from dconeybe.xonsh import rnd

def test_rnd_empty_args_should_generate_string():
  result = rnd.rnd([])

  assert isinstance(result, str)
  assert len(result) == 10
  for index in range(len(result)):
    with ExceptionNotes(f"result={result!r}", f"index={index!r}"):
      assert result[index] in ALPHABET


def test_rnd_empty_args_should_generate_unique_strings():
  results = tuple(rnd.rnd([]) for _ in range(100))

  counts = collections.defaultdict(lambda: 0)
  for result in results:
    counts[result] += 1
  for (result, count) in counts.items():
    with ExceptionNotes(f"result={result!r}", f"results={results!r}"):
      assert count == 1


ALPHABET_LETTERS = "abcdefghjkmnpqrstvwxyz"
ALPHABET_NUMBERS = "23456789"
ALPHABET = ALPHABET_LETTERS + ALPHABET_NUMBERS


class ExceptionNotes:

  def __init__(self, note: str, *more_notes: str) -> None:
    self._notes = [note]
    self._notes.extend(more_notes)

  def __enter__(self) -> None:
    pass

  def __exit__(self, exc_type, exc_value, traceback) -> None:
    if exc_value is not None:
      for note in self._notes:
        exc_value.add_note(note)
