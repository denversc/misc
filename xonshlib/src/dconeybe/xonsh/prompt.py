from __future__ import annotations

from collections.abc import Iterable

###############################################################################
# xonsh prompt setup
# https://xon.sh/tutorial.html#customizing-the-prompt
###############################################################################


class Prompt:

  def __init__(self, hostname: str) -> None:
    self.hostname = hostname

  def time_format(self) -> str:
    # See https://docs.python.org/3.13/library/time.html#time.strftime
    return "%a %b %d, %Y %H:%M:%S"

  def prompt(self) -> str:
    return "".join(self._prompt_chunks())

  def _prompt_chunks(self) -> Iterable[str]:
    yield "{BACKGROUND_" + self._hostname_color() + "}{WHITE}"
    yield "{hostname}"
    yield "{RESET} "

    yield "{BOLD_YELLOW}{cwd}{RESET}"

    yield "{last_return_code_if_nonzero:"
    yield " {RED}[retcode={BOLD_INTENSE_RED}{}{RED}]{RESET}"
    yield "}"

    yield "\n"

    yield "{BOLD_BLUE} "
    yield "{RESET} "

  def right_prompt(self) -> str:
    return "{FAINT_WHITE}[{localtime}]"

  def _hostname_color(self):
    colors = {"dconeybe2.c.googlers.com": "GREEN", "dconeybe-macbookpro3.roam.internal": "BLUE"}
    return colors.get(self.hostname, "RED")
