from __future__ import annotations


class ExceptionNotes:
  """
  Context manager that adds "notes" to the exception raised in the context, if
  one is thrown.

  See https://docs.python.org/3/library/exceptions.html#BaseException.add_note
  for details about adding "notes" to exceptions. The idea is, however, that
  if a test fails then the test framework will include notes in the output,
  which can be _very_ helpful for adding context to an error.

  Using this context is syntactically similar to code like this:

  try:
    ...
  except:
    sys.exception().add_note(note)
    raise
  """

  def __init__(self, note: str, *more_notes: str) -> None:
    """
    Args:
      note: The first, and possibly _only_, note to add.
      more_notes: The second, third, and so on, notes to add.
    """
    self._notes = [note]
    self._notes.extend(more_notes)

  def __enter__(self) -> None:
    pass

  def __exit__[
      T: BaseException
  ](self, exc_type: type[T] | None, exc_value: T | None, traceback: object | None,) -> None:
    if exc_value is not None:
      for note in self._notes:
        exc_value.add_note(note)
