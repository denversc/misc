from __future__ import annotations

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
    return (
        "{BACKGROUND_" + self._hostname_color() + "}{WHITE}{user}@{hostname}{RESET} "
        "{BOLD_YELLOW}{cwd}{RESET}"
        "{RED}{last_return_code_if_nonzero: [retcode={BOLD_INTENSE_RED}{}{RED}]{RESET}}"
        "\n{BOLD_BLUE}{prompt_end}{RESET} "
    )

  def right_prompt(self) -> str:
    return "{FAINT_WHITE}[{localtime}]"

  def _hostname_color(self):
    colors = {"dconeybe2.c.googlers.com": "GREEN", "dconeybe-macbookpro3.roam.internal": "BLUE"}
    return colors.get(self.hostname, "RED")
