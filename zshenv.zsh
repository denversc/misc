# To use this file, run this command:
# echo "source \"$PWD/zshenv.zsh\"" > ~/.zshenv

# XDG Base Directories
# https://specifications.freedesktop.org/basedir-spec/latest/

# $XDG_DATA_HOME defines the base directory relative to which user-specific data
# files should be stored.
if [[ ! -v XDG_DATA_HOME ]] ; then
  export XDG_DATA_HOME="$HOME/.local/share"
fi

# $XDG_CONFIG_HOME defines the base directory relative to which user-specific
# configuration files should be stored.
if [[ ! -v XDG_CONFIG_HOME ]] ; then
  export XDG_CONFIG_HOME="$HOME/.config"
fi

# $XDG_STATE_HOME defines the base directory relative to which user-specific
# state files should be stored. The $XDG_STATE_HOME contains state data that
# should persist between (application) restarts, but that is not important or
# portable enough to the user that it should be stored in $XDG_DATA_HOME. For
# example, it may contain actions history (logs, history, recently used files,
# etc.) or current state of the application that can be reused on a restart
# (view, layout, open files, undo history, etc.).
if [[ ! -v XDG_STATE_HOME ]] ; then
  export XDG_STATE_HOME="$HOME/.local/state"
fi

# $XDG_CACHE_HOME defines the base directory relative to which user-specific
# non-essential data files should be stored.
if [[ ! -v XDG_CACHE_HOME ]] ; then
  export XDG_CACHE_HOME="$HOME/.cache"
fi

# User-specific executable files may be stored in $HOME/.local/bin.
# Distributions should ensure this directory shows up in the UNIX $PATH
# environment variable, at an appropriate place.
export PATH="$HOME/.local/bin:$PATH"
