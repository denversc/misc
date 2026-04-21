from __future__ import annotations

import typing

import kittens.tui.handler
import my_kittens

if typing.TYPE_CHECKING:
  from collections.abc import Sequence
  from kitty.boss import Boss


def main(_args: Sequence[str]) -> None:
  pass


@kittens.tui.handler.result_handler(no_ui=True)
def handle_result(args: Sequence[str], _answer: None, target_window_id: int, boss: Boss) -> None:
  my_kittens.raise_exception_if_nonempty_args(args)
  kittens = my_kittens.MyKittens.from_target_window_id(boss, target_window_id)
  kittens.launch_gemini_tab(take_focus=True, next_to=None)
