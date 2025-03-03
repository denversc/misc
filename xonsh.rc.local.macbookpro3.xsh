# To use this file, run:
# ln -sf ../xonsh.rc.local.macbookpro3.xsh xonshrc.d/01_local.xsh

import os
import sys

sys.path.append($HOME + "/misc/xonshlib/src")

# Store tracebacks into this file for debugging purposes.
# https://xon.sh/envvars.html#xonsh-traceback-logfile
$XONSH_TRACEBACK_LOGFILE = $HOME + "/.local/state/xonsh/traceback.log.txt"

if $XONSH_LOGIN:

  # https://wiki.archlinux.org/title/XDG_Base_Directory
  $PATH.append($HOME + "/.local/bin")
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

  nvim_path = $(brew --prefix neovim) + "/bin/nvim"
  $EDITOR = nvim_path
  $PAGER = nvim_path + " -R -S " + $HOME + "/misc/nvim_git_pager.lua"
  $MANPAGER = nvim_path + " +Man!"
  del nvim_path

  # Ensure that Google utilities, like gcert, are in the PATH.
  $PATH.append("/usr/local/bin")
  $PATH.prepend("/usr/local/git/current/bin")

  # Make sure that subprocess.Popen respects the changes to $PATH made above.
  # Notably, changes to $PATH below are required by the zoxide xontrib.
  os.environ["PATH"] = os.pathsep.join($PATH.paths)

# Clean up global namespace.
del sys
del os
