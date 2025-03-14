from __future__ import annotations

import pytest
import hypothesis
import hypothesis.strategies as st

from dconeybe.testing.exception_notes import ExceptionNotes


@hypothesis.given(st.text())
def test_should_do_nothing_if_no_exception(note: str):
  with ExceptionNotes(note):
    pass


@hypothesis.given(st.text())
def test_should_add_the_one_and_only_note(note: str):
  with pytest.raises(Z3v96tvmw3Error) as exc_info:
    with ExceptionNotes(note):
      raise Z3v96tvmw3Error()

  assert exc_info.value.__notes__ == [note]


@hypothesis.given(st.text(), st.text())
def test_should_add_both_of_the_notes_in_order(note1: str, note2: str):
  with pytest.raises(Z3v96tvmw3Error) as exc_info:
    with ExceptionNotes(note1, note2):
      raise Z3v96tvmw3Error()

  assert exc_info.value.__notes__ == [note1, note2]


@hypothesis.given(st.text(), st.text(), st.text(), st.text())
def test_should_add_all_of_the_notes_in_order(note1: str, note2: str, note3: str, note4: str):
  with pytest.raises(Z3v96tvmw3Error) as exc_info:
    with ExceptionNotes(note1, note2, note3, note4):
      raise Z3v96tvmw3Error()

  assert exc_info.value.__notes__ == [note1, note2, note3, note4]


@hypothesis.given(st.text())
def test_should_re_raise_the_same_exception(note: str):
  exception = Z3v96tvmw3Error()
  with pytest.raises(Z3v96tvmw3Error) as exc_info:
    with ExceptionNotes(note):
      raise exception

  assert exc_info.value is exception


class Z3v96tvmw3Error(Exception):
  pass
