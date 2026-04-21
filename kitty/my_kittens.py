from __future__ import annotations

import os
import subprocess
import typing

import kitty.launch

if typing.TYPE_CHECKING:
  from collections.abc import Iterable, Sequence
  from typing import Self
  from kitty.boss import Boss
  from kitty.window import Window


class MyKittens:

  def __init__(self, boss: Boss, window: Window | None, cwd: str) -> None:
    self.boss = boss
    self.window = window
    self.cwd = cwd

  @classmethod
  def from_target_window_id(cls, boss: Boss, target_window_id: int) -> Self:
    window = boss.window_id_map.get(target_window_id)
    cwd = resolve_cwd_from_window(window)
    return cls(boss=boss, window=window, cwd=cwd)

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


def resolve_cwd_from_window(window: Window | None) -> str:
  if window is not None:
    cwd = window.cwd_of_child
    if cwd is not None:
      return cwd

  return os.getcwd()


class NoArgsSupportedError(Exception):
  pass


def raise_exception_if_nonempty_args(args: Iterable[str]) -> None:
  args = tuple(args)
  if len(args) > 1:
    raise NoArgsSupportedError(
      f"{args[0]} does not support args, but got {len(args)} args: " +
      subprocess.list2cmdline(args[1:])
    )

