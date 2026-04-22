from __future__ import annotations

import pathlib
import subprocess
import tempfile
import typing

import my_kittens

if typing.TYPE_CHECKING:
  from collections.abc import Sequence
  from kitty.boss import Boss


def main(args: Sequence[str]) -> str | None:
  my_kittens.raise_exception_if_nonempty_args(args)

  unresolved_directory = pathlib.Path.home() / "work" / "android"
  directory = unresolved_directory.resolve(strict=False)

  fzf_history_file = pathlib.Path.home() / ".local" / "state" / "kitty" / "android_worktree_history.txt"
  fzf_history_file.parent.mkdir(parents=True, exist_ok=True)

  subdirectory_names = tuple(f.name for f in directory.iterdir() if not f.name.startswith("."))

  with tempfile.NamedTemporaryFile() as stdin_file, tempfile.NamedTemporaryFile() as stdout_file:
    stdin_file.write("\n".join(subdirectory_names).encode("utf8"))
    stdin_file.seek(0)

    process = subprocess.Popen(
      args=[
        "/opt/homebrew/bin/fzf",
        "--style=full",
        "--color=dark",
        "--layout=reverse",
        "--cycle",
        "--list-label=Android Worktrees",
        f"--footer={directory}",
        "--ghost=Select Android Worktree",
        f"--history={fzf_history_file.absolute()}",
      ],
      stdin=stdin_file,
      stdout=stdout_file,
    )

    match process.wait():
      case 0:
        stdout_file.seek(0)
        return stdout_file.read().decode('utf8').strip()
      case 1 | 130:
        return None
      case exit_code:
        raise Exception(f"ERROR: fzf completed with error exit code: {exit_code}")


def handle_result(args: Sequence[str], subdirectory_name: str | None, target_window_id: int, boss: Boss) -> None:
  my_kittens.raise_exception_if_nonempty_args(args)

  if subdirectory_name is None:
    return

  cwd = pathlib.Path.home() / "work" / "android" / subdirectory_name / "firebase-dataconnect"
  kittens = my_kittens.MyKittens.from_target_window_id(boss, target_window_id, cwd=cwd)
  dev_window = kittens.launch_dev_window(title=subdirectory_name)
  kittens.launch_gemini_tab(take_focus=False, target_window=dev_window, title=subdirectory_name)
