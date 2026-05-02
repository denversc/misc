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
# 2. brew install fzf zsh-history-substring-search zsh-syntax-highlighting zsh-autosuggestions
# 3. Configure fzf, as documented below.

###############################################################################
# Functions
###############################################################################

say() { builtin print -r -- "$@" }
sayp() { builtin print -rP -- "$@" }
sayn() { builtin print -rn -- "$@" }
saypn() { builtin print -rPn -- "$@" }

say_args() { say "${(q)@}" }

good() { sayp "%F{green}SUCCESS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!%f" }

bad() {
  saypn "%F{red}ERROR%f"
  if (( # == 0 )); then
    saypn "%f"
    say
  else
    saypn ": %f"
    say "$@"
  fi
}

mkd() {
  if (( # > 1 )); then
    bad "$0: too many arguments; unexpected argument: $2" >&2
    return 2
  fi

  typeset name="${1:-tmp}"
  mkdir -p ~/tmp
  cd ~/tmp
  cd "$(mktemp -d "${name}XXXXXXXXXX")"
}

###############################################################################
# Visual Enhancements (Gradients)
###############################################################################

_gradient_preexec() {
  _gradient_cmd_start=$SECONDS
}

# Draws a horizontal line across the full width of the terminal with a
# TrueColor gradient transition. The colors change based on the success
# or failure of the previous command. If the command failed, it embeds
# the exit code, runtime, and the command name near the right edge.
_gradient_separator() {
  local last_status=$?
  
  # Suppress the border if no command was actually run (empty ENTER)
  [[ -z "$_gradient_cmd_start" ]] && return

  local elapsed=$(( SECONDS - _gradient_cmd_start ))
  unset _gradient_cmd_start

  # Skip if terminal is too narrow
  (( COLUMNS < 20 )) && return

  local start_hex="#6a95e9" # Blue (Success)
  local end_hex="#9ece6a"   # Green (Success)
  local status_icon=""      # Hollow Check Circle (\uf05d) for success

  if (( last_status != 0 )); then
    start_hex="#5e0000"     # Deep Maroon (Failure)
    end_hex="#ff8a8a"       # Bright Salmon (Failure)
    status_icon=""         # Error icon
  fi

  local elapsed_str
  if (( elapsed < 600 )); then
    elapsed_str="${elapsed}s"
  else
    integer mins=$(( elapsed / 60 ))
    integer secs=$(( elapsed % 60 ))
    elapsed_str="${mins}m ${secs}s"
  fi
  
  # Get the last command and trim it
  local last_cmd=$(fc -ln -1 | xargs)
  local base_info=" $status_icon $last_status  ${elapsed_str}  "
  
  # Allow the text section to consume up to half the terminal width
  integer max_cmd_len=$(( COLUMNS / 2 - ${#base_info} - 1 ))
  (( max_cmd_len < 5 )) && max_cmd_len=5 # Safety fallback for narrow terminals
  
  # Status Icon, Time, Command
  local status_info="${base_info}${last_cmd[1,$max_cmd_len]} "
  integer info_len=${#status_info}
  integer info_start=$(( COLUMNS - info_len - 5 ))
  integer info_end=$(( info_start + info_len ))

  # Extract RGB components
  local s=${start_hex#\#} e=${end_hex#\#}
  integer r1=$((16#${s:0:2})) g1=$((16#${s:2:2})) b1=$((16#${s:4:2}))
  integer r2=$((16#${e:0:2})) g2=$((16#${e:2:2})) b2=$((16#${e:4:2}))

  local line=""
  integer i
  # Calculate RGB for each column and build the line
  for (( i=0; i < COLUMNS; i++ )); do
    integer r=$(( r1 + (r2 - r1) * i / (COLUMNS - 1) ))
    integer g=$(( g1 + (g2 - g1) * i / (COLUMNS - 1) ))
    integer b=$(( b1 + (b2 - b1) * i / (COLUMNS - 1) ))
    
    local char="─"
    integer char_r=$r char_g=$g char_b=$b

    if (( i >= info_start && i < info_end )); then
       char="${status_info[i - info_start + 1]}"
       # Dim the text color by 1/3 so it is less loud/distracting
       char_r=$(( r * 2 / 3 ))
       char_g=$(( g * 2 / 3 ))
       char_b=$(( b * 2 / 3 ))
    else
       if (( i == info_start - 1 )); then
         char="┤"
       elif (( i == info_end )); then
         char="├"
       fi
    fi
    
    line+="\e[38;2;${char_r};${char_g};${char_b}m${char}"
  done
  
  # Print the line and reset color
  echo -e "${line}\e[0m"
}

# Use add-zsh-hook to run the separator before every prompt
autoload -Uz add-zsh-hook
add-zsh-hook preexec _gradient_preexec
add-zsh-hook precmd _gradient_separator

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

# Enable parameter expansion, command substitution, and arithmetic expansion in the prompt.
setopt PROMPT_SUBST

# Silence the "are you sure you want to delete all the files" prompt
setopt RM_STAR_SILENT

###############################################################################
# Command completion
###############################################################################

# Enable zsh builtin context-aware completions.
autoload -Uz compinit && compinit

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

###############################################################################
# fzf history search
###############################################################################

# Prerequisite 1: brew install fzf
# Prerequisite 2: "$(brew --prefix)/opt/fzf/install" --xdg --key-bindings --completion --no-update-rc --no-bash --no-fish
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

###############################################################################
# zsh-history-substring-search
###############################################################################

# Press UP or DOWN to cycle through history items that _start with_ what has
# been typed so far.
#
# https://github.com/zsh-users/zsh-history-substring-search
#
# Prerequisite: brew install zsh-history-substring-search

if [[ -f "$(brew --prefix)/share/zsh-history-substring-search/zsh-history-substring-search.zsh" ]] ; then
  source "$(brew --prefix)/share/zsh-history-substring-search/zsh-history-substring-search.zsh"
  bindkey -M viins '^[[A' history-substring-search-up
  bindkey -M viins '^[[B' history-substring-search-up
  bindkey -M viins "${terminfo[kcuu1]}" history-substring-search-up
  bindkey -M viins "${terminfo[kcud1]}" history-substring-search-down
fi

###############################################################################
# zsh-syntax-highlighting
###############################################################################

# Real-time syntax highlighting for the commands you type in your terminal.
#
# Valid Commands: Recognized commands (like `ls`, `git`, `docker`) turn a
# specific color (usually green). If you type a command that doesn't exist or
# misspell one, it remains a different color (often red).
#
# Arguments & Flags: Command arguments, options (like `-l` or `--all`), and
# strings are highlighted in different colors, making complex commands much
# easier to read and parse visually.
#
# Path Highlighting: It will also underline and color file paths. If the path
# exists, it's underlined; if it doesn't, it's not.
#
# https://github.com/zsh-users/zsh-syntax-highlighting
#
# Prerequisite: brew install zsh-syntax-highlighting

source "$(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"

###############################################################################
# zsh-autosuggestions
###############################################################################

# Suggests commands as you type based on your command history, providing a
# ghost-like completion that you can accept with a single keystroke.
#
# As you begin typing a command, it finds the most recent command in your
# history that starts with what you've typed and displays the rest of the
# command in a faint, muted color (usually grey). If the suggestion is what you
# want, you press the right arrow key (→) or the "End" key to accept it and
# instantly fill in the rest of the command. If it's _not_ what you want, you
# just keep typing, and the suggestion will disappear or update.
#
# https://github.com/zsh-users/zsh-autosuggestions
#
# Prerequisite: brew install zsh-autosuggestions

source "$(brew --prefix)/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
