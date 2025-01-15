###############################################################################
# xonsh prompt setup
# https://xon.sh/tutorial.html#customizing-the-prompt
###############################################################################

# See https://docs.python.org/3.13/library/time.html#time.strftime
$PROMPT_FIELDS["time_format"] = "%a %b %d, %Y %H:%M:%S"

def hostname_color():
  match $HOSTNAME:
    case "dconeybe2.c.googlers.com":
      return "GREEN"
    case "dconeybe-macbookpro3.roam.internal":
      return "BLUE"
  return "RED"

$PROMPT = ("{BACKGROUND_" + hostname_color() + "}{WHITE}{user}@{hostname}{RESET} "
  "{BOLD_YELLOW}{cwd}{RESET}"
  "{BOLD_WHITE}{curr_branch: [git_branch={}]}{RESET}"
  "{RED}{last_return_code_if_nonzero: [retcode={BOLD_INTENSE_RED}{}{RED}]{RESET}}"
  "\n{BOLD_BLUE}{prompt_end}{RESET} "
)

del hostname_color

$RIGHT_PROMPT = "{FAINT_WHITE}[{localtime}]"
