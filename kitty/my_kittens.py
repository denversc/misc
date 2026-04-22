from __future__ import annotations

import os
import pathlib
import subprocess
import typing

import kitty.launch

if typing.TYPE_CHECKING:
  from collections.abc import Iterable, Sequence
  from typing import Self
  from kitty.boss import Boss
  from kitty.tabs import Tab
  from kitty.window import Window


class MyKittens:

  def __init__(self, boss: Boss, window: Window | None, cwd: pathlib.Path) -> None:
    self.boss = boss
    self.window = window
    self.cwd = cwd

  @classmethod
  def from_target_window_id(
    cls,
    boss: Boss,
    target_window_id: int,
    cwd: pathlib.Path | None = None,
  ) -> Self:
    window = boss.window_id_map.get(target_window_id)
    if cwd is None:
      cwd = resolve_cwd_from_window(window)
    return cls(boss=boss, window=window, cwd=cwd)

  def launch(self, args: Sequence[str], target_tab: Tab | None = None) -> Window | None:
    launch_opts, launch_args = kitty.launch.parse_launch_args(args)
    return kitty.launch.launch(self.boss, launch_opts, launch_args, target_tab=target_tab)

  def title_from_cwd(self) -> str:
    title = self.cwd.resolve(strict=False).name.strip()
    if len(title) > 0:
      return title

    return str(self.cwd).strip()

  def launch_dev_window(self, title: str) -> Window | None:
    args = tuple(self.dev_window_launch_args(title=title))
    return self.launch(args)

  def dev_window_launch_args(self, title: str) -> Iterable[str]:
    yield "--type=os-window"
    yield f"--window-title={title}"
    yield f"--tab-title={title}"
    yield f"--os-window-title={title}"
    yield f"--cwd={self.cwd}"

  def launch_gemini_tab(
    self,
    take_focus: bool,
    target_window: Window | None,
    title: str | None = None,
  ) -> None:
    args = tuple(self.gemini_tab_launch_args(
       take_focus=take_focus,
       title=title,
    ))
    target_window = target_window if target_window is not None else self.window
    target_tab = target_window.tabref() if target_window is not None else None
    self.launch(args, target_tab=target_tab)

  def gemini_tab_launch_args(
    self,
    take_focus: bool,
    title: str | None,
  ) -> Iterable[str]:
    yield "--type=tab"
    yield f"--cwd={self.cwd}"

    if not take_focus:
      yield "--dont-take-focus"

    yield "/usr/bin/env"
    yield "zsh"
    yield "-l"
    yield "-c"
    yield "".join(self._gemini_zsh_command_chunks(title))

  @staticmethod
  def _gemini_zsh_command_chunks(title: str | None) -> Iterable[str]:
    # Set the terminal title using ANSI escape sequences.
    # Gemini will eventually replace this with its fancy value.
    yield r'printf "\e]2;󰦖 Gemini '
    if title is not None:
      yield f"({title}) "
    yield r'starting...\a'

    # Echo a similar "loading" string to the terminal's stdout.
    yield '󰦖 Gemini '
    if title is not None:
      yield f"({title}) "
    yield 'starting in $PWD"'

    yield " ; "

    # Launch gemini-cli.
    if title is not None:
      yield f"CLI_TITLE='{title.replace("'", "")}' "
    yield "gemini"


def resolve_cwd_from_window(window: Window | None) -> pathlib.Path:
  if window is not None:
    cwd = window.cwd_of_child
    if cwd is not None:
      return pathlib.Path(cwd.strip().rstrip(os.sep).strip())

  return pathlib.Path.cwd()


class NoArgsSupportedError(Exception):
  pass


def raise_exception_if_nonempty_args(args: Iterable[str]) -> None:
  args = tuple(args)
  if len(args) > 1:
    raise NoArgsSupportedError(
      f"{args[0]} does not support args, but got {len(args)} args: " +
      subprocess.list2cmdline(args[1:])
    )

