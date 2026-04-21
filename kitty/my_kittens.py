from __future__ import annotations

import os
import subprocess
import typing

import kittens.tui.handler
import kitty.launch

if typing.TYPE_CHECKING:
  from collections.abc import Iterable, Sequence
  from kitty.boss import Boss
  from kitty.window import Window


def main(_args: Sequence[str]) -> None:
  pass


@kittens.tui.handler.result_handler(no_ui=True)
def handle_result(args: Sequence[str], _answer: None, target_window_id: int, boss: Boss) -> None:
  window = boss.window_id_map.get(target_window_id)
  cwd = resolve_cwd_from_window(window)
  kittens = MyKittens(boss=boss, cwd=cwd)

  match args:
    case [_, "dev_window"]:
      kittens.launch_dev_window()
    case [_, "gemini_tab"]:
      kittens.launch_gemini_tab(take_focus=True, next_to=window)
    case [script_name, *script_args]:
      raise ValueError(f"{script_name}: invalid args: {subprocess.list2cmdline(script_args)}")


def resolve_cwd_from_window(window: Window | None) -> str:
  if window is not None:
    cwd = window.cwd_of_child
    if cwd is not None:
      return cwd

  return os.getcwd()


class MyKittens:

  def __init__(self, boss: Boss, cwd: str) -> None:
    self.boss = boss
    self.cwd = cwd

  def launch_dev_window(self) -> None:
    cwd_clean = self.cwd.strip().rstrip(os.sep).strip()
    title = os.path.basename(cwd_clean) or cwd_clean
    args = tuple(self.dev_window_launch_args(title=title))
    new_window = self.launch(args)
    self.launch_gemini_tab(take_focus=False, next_to=new_window)

  def launch_gemini_tab(self, take_focus: bool, next_to: Window | None) -> None:
    args = tuple(self.gemini_tab_launch_args(
       take_focus=take_focus,
       next_to=next_to,
    ))
    self.launch(args)

  def launch(self, args: Sequence[str]) -> Window | None:
    launch_opts, launch_args = kitty.launch.parse_launch_args(args)
    return kitty.launch.launch(self.boss, launch_opts, launch_args)

  def dev_window_launch_args(self, title: str) -> Iterable[str]:
    yield "--type=os-window"
    yield f"--window-title={title}"
    yield f"--tab-title={title}"
    yield f"--os-window-title={title}"
    yield f"--cwd={self.cwd}"

  def gemini_tab_launch_args(self, take_focus: bool, next_to: Window | None) -> Iterable[str]:
    yield "--type=tab"
    yield f"--cwd={self.cwd}"

    if not take_focus:
      yield "--dont-take-focus"

    if next_to is not None:
      yield f"--next-to=id:{next_to.id}"
     
    yield "/usr/bin/env"
    yield "zsh"
    yield "-l"
    yield "-c"
    yield "gemini"
