# To use this file, add this line to the top of ~/.zshrc:
#
# source "$HOME/misc/zshrc.zsh"
#
# Note that ~/.zshrc is loaded for *interactive shells*.
# Therefore, this file should only configure behavior that is relevant
# to a human who is directly typing commands, etc., and not background scripts.
#
# Setup Instructions:
# 1. Add "export EDITOR=nvim" in ~/.zshrc
# 2. Install fzf, as documented below.
# 3. brew install zsh-history-substring-search

###############################################################################
# Prompt
###############################################################################

if [[ "$OSTYPE" == "darwin"* ]]; then
  PROMPT='%K{#9da9d1}%F{#000000}  %F{#9da9d1}%K{#6a95e9} %F{#ffffff}%~ %F{#6a95e9}%k'$'\n''%F{#9ece6a}❯ %f'
else
  PROMPT='%K{#9da9d1}%F{#000000}  %F{#9da9d1}%K{#a9c8a1} %F{#000000}%~ %F{#a9c8a1}%k'$'\n''%F{#9ece6a}❯ %f'
fi

###############################################################################
# General configuration
###############################################################################

# Spelling correction for command names.
# If you mistype a command (e.g., sl instead of ls),
# zsh will ask: zsh: correct 'sl' to 'ls' [nyae]?.           █
unsetopt CORRECT

# Advanced pattern matching (globbing).
# It allows the use of special characters like # (match 0 or more of the preceding),
# ~ (exclude), and ^
setopt EXTENDED_GLOB
#
# Silence the "are you sure you want to delete all the files" prompt
setopt RM_STAR_SILENT

# Normally, when you hit Tab on an ambiguous word, Zsh either completes the
# unambiguous part or just shows you a list of matches. With MENU_COMPLETE
# enabled, hitting Tab will immediately insert the first match into your command
# line. Each subsequent Tab press will cycle through the other available matches.
setopt MENU_COMPLETE

# By default, Zsh moves the cursor to the end of a word before attempting to
# complete it. If you enable COMPLETE_IN_WORD, Zsh will attempt completion at
# the cursor's current position, even if there is text to the right.
setopt COMPLETE_IN_WORD

###############################################################################
# Vim Mode
###############################################################################

# Enable vim-style key bindings, instead of emacs-style key bindings.
bindkey -v

# Reduce the delay after pressing ESC to 0.2 seconds, making the switch to
# Normal Mode feel instantaneous. By default, zsh waits 0.4 seconds after ESC
# to see if it's part of a longer escape sequence, which feels like "lag."
KEYTIMEOUT=20

# Custom vim key bindings
#
# To see all bindings in *normal* mode, run
#   bindkey -M vicmd
# To see all bindings in *insert* mode, run
#   bindkey -M viins
#
autoload -Uz edit-command-line
zle -N edit-command-line

# Open the prompt in $EDITOR by pressing "v" in normal mode or CTRL+G.
bindkey -M vicmd 'v' edit-command-line
bindkey -M vicmd '^g' edit-command-line
bindkey -M viins '^g' edit-command-line

# Press "jk" in insert mode to go back to normal mode.
# Note that the delay after pressing "j" is defined by KEYTIMEOUT
bindkey -M viins 'jk' vi-cmd-mode

###############################################################################
# History management
###############################################################################

# The file in which to save the history
HISTFILE=~/.zsh_history

# How many commands to keep in RAM
HISTSIZE=100000

# How many commands to save on disk
SAVEHIST=100000

# Save the start time (Unix epoch) and the duration (in seconds) of each
# command to the history file.
setopt EXTENDED_HISTORY

# Automatically import new commands from the history file into your current
# session and append your commands to the file immediately. This keeps the
# history synchronized across all open terminal windows.
setopt SHARE_HISTORY

# Do not store adjacent duplicates in the history.
setopt HIST_IGNORE_DUPS

# When the history file reaches its maximum size (SAVEHIST), zsh will delete the
# oldest duplicates before deleting unique commands.
setopt HIST_EXPIRE_DUPS_FIRST

# Any command that begins with a space is not saved to the history.
# This is useful for commands containing sensitive information (like API keys).
setopt HIST_IGNORE_SPACE

# When using history expansion (like !! or !$), zsh does not execute the command
# immediately. Instead, it loads the expanded command onto the prompt so you can
# review or edit it before pressing Enter.
setopt HIST_VERIFY

# Changes how zsh internalizes "words" in history. It makes history expansion
# (like !$) more intelligent by respecting shell-style quoting rather than just
# splitting on spaces.
setopt HIST_LEX_WORDS

# fzf history search.
# Requires: "$(brew --prefix)/opt/fzf/install" --xdg --key-bindings --completion --no-update-rc --no-bash --no-fish
#
# Key Bindings:
#   * CTRL-R (History): Search through your command history.
#       Selecting a result pastes it onto your command line.
#   * CTRL-T (Files): Search for files and folders in the current directory.
#       The selected path is pasted at the cursor.
#   * ALT-C (Directory Navigation): Search for subdirectories.
#       Selecting one will instantly cd into that directory.
#
# While the fzf interface is open, you can use these keys to navigate results:
#   * CTRL-K / CTRL-P: Move the selection cursor up.
#   * CTRL-J / CTRL-N: Move the selection cursor down.
#   * Enter: Select the highlighted item.
#   * TAB: Mark multiple items (if multi-select mode -m is enabled).
#   * ESC / CTRL-C: Exit the finder without making a selection.

if [[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/fzf/fzf.zsh" ]] ; then
  export FZF_CTRL_R_OPTS="
    --height=100%
    --layout=reverse
    --info=inline
    --border
    --border-label 'CTRL-R History Search'
    --color=dark
    --color='header:italic:bold'
  "
  export FZF_CTRL_T_OPTS="
    --height=100%
    --layout=reverse
    --info=inline
    --border
    --border-label 'CTRL-T File Search'
    --color=dark
    --color='header:italic:bold'
  "
  source "${XDG_CONFIG_HOME:-$HOME/.config}/fzf/fzf.zsh"
fi

# Bind up and down arrows to search the history for what has been typed so far.
# Requires: brew install zsh-history-substring-search
if [[ -f "$(brew --prefix)/share/zsh-history-substring-search/zsh-history-substring-search.zsh" ]] ; then
  source "$(brew --prefix)/share/zsh-history-substring-search/zsh-history-substring-search.zsh"
  bindkey -M viins '^[[A' history-substring-search-up
  bindkey -M viins '^[[B' history-substring-search-up
  bindkey -M viins "${terminfo[kcuu1]}" history-substring-search-up
  bindkey -M viins "${terminfo[kcud1]}" history-substring-search-down
fi
