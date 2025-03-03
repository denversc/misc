# To use this file, run:
# ln -sf $PWD/xonsh.rc.local.macbookpro3.xsh $HOME/.config/xonsh/rc.local.xsh

import os
import sys

sys.path.append($HOME + "/misc/xonshlib/src")

if $XONSH_LOGIN:

  # Suppress detailed tracebacks, which are occasionally useful but normally
  # noisy and distracting.
  # https://xon.sh/envvars.html#xonsh-show-traceback
  $XONSH_SHOW_TRACEBACK = False

  # Store tracebacks into this file for debugging purposes.
  # https://xon.sh/envvars.html#xonsh-traceback-logfile
  $XONSH_TRACEBACK_LOGFILE = $HOME + "/.local/state/xonsh/traceback.log.txt"

  # Disable suggesting commands when an unknown command is entered.
  # I generally just find this annoying and not helpful.
  # https://xon.sh/envvars.html#suggest-commands
  $SUGGEST_COMMANDS = False

  # https://wiki.archlinux.org/title/XDG_Base_Directory
  $PATH.append($HOME + ".local/bin")
  $XDG_CONFIG_HOME = $HOME + "/.config"
  $XDG_CACHE_HOME = $HOME + "/.cache"
  $XDG_DATA_HOME = $HOME + "/.local/share"
  $XDG_STATE_HOME = $HOME + "/.local/state"

  # https://docs.brew.sh/Installation
  # eval $(/opt/homebrew/bin/brew shellenv)
  $HOMEBREW_PREFIX = "/opt/homebrew"
  $HOMEBREW_CELLAR = $HOMEBREW_PREFIX + "/Cellar"
  $HOMEBREW_REPOSITORY = $HOMEBREW_PREFIX
  $INFOPATH = $HOMEBREW_PREFIX + "/share/info"
  $PATH.prepend($HOMEBREW_PREFIX + "/sbin")
  $PATH.prepend($HOMEBREW_PREFIX + "/bin")

  # https://asdf-vm.com/guide/getting-started.html
  $ASDF_DATA_DIR = $XDG_STATE_HOME + "/asdf"
  $PATH.prepend($ASDF_DATA_DIR + "/shims")

  # Ensure that Google utilities, like gcert, are in the PATH.
  $PATH.append("/usr/local/bin")
  $PATH.prepend("/usr/local/git/current/bin")

  # Make sure that subprocess.Popen respects the changes to $PATH made above.
  # Notably, changes to $PATH below are required by the zoxide xontrib.
  os.environ["PATH"] = os.pathsep.join($PATH.paths)

# Clean up global namespace.
del sys
del os
