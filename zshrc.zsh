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

say() { builtin print -r -- $@ }
sayp() { builtin print -rP -- $@ }
sayn() { builtin print -rn -- $@ }
saypn() { builtin print -rPn -- $@ }

say_error() {
  saypn "%F{red}ERROR%f"
  if (( # == 0 )); then
    saypn "%f"
    say
  else
    saypn ": %f"
    say $@
  fi
}

say_warning() {
  saypn "%F{yellow}WARNING%f"
  if (( # == 0 )); then
    saypn "%f"
    say
  else
    saypn ": %f"
    say $@
  fi
}

say_args() { say ${(q)@} }

good() { sayp "%F{green}SUCCESS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!%f" }

bad() {
  local return_code="$?"

  emulate -L zsh
  setopt extended_glob warn_create_global no_unset pipe_fail

  if (( # > 0 )); then
    say_error "$0: expected 0 arguments, but got $#: $*" >&2
    return 2
  fi
  sayp "%F{red}ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!%f"
  return "$return_code"
}

# Function: kup (kitten file upload)
#
# Arguments: All arguments are passed verbatim to the "kitten" command.
#
# Uses the "kitten transfer" kitten to send files from the computer that is
# running Kitty (the local host) to the computer that is running this function
# (the remote host).
kup() {
  emulate -L zsh
  setopt extended_glob warn_create_global no_unset pipe_fail

  typeset -r kitten_args=(kitten transfer --direction=upload "$@")
  say_args "${kitten_args[@]}"
  "${kitten_args[@]}"
}

# Function: kdl (kitten file download)
#
# Arguments: All arguments are passed verbatim to the "kitten" command.
#
# Uses the "kitten transfer" kitten to send files from the computer that is
# running this function (the remote host) to the computer that is running Kitty
# (the local host).
kdl() {
  emulate -L zsh
  setopt extended_glob warn_create_global no_unset pipe_fail

  typeset -r kitten_args=(kitten transfer --direction=download "$@")
  say_args "${kitten_args[@]}"
  "${kitten_args[@]}"
}

# Function: mkd (make temp directory)
#
# Arguments: one positional argument may be specified and, if specified, will
#   be incorporated into the name of the created directory.
#
# Creates a subdirectory of ~/tmp with a unique name and "cd's" into it.
mkd() {
  emulate -L zsh
  setopt extended_glob warn_create_global no_unset pipe_fail

  if (( # > 1 )); then
    say_error "$0: expected 0 arguments, but got $#: $*" >&2
    return 2
  fi

  typeset name=${1:-tmp}
  mkdir -p ~/tmp || return
  cd ~/tmp || return
  local mktemp_result
  mktemp_result=$(mktemp -d ${name}XXXXXXXXXX) || return
  cd "$mktemp_result"
}

# Function: strip_whitespace
#
# Arguments: If zero arguments are specified, then stdin is used as the input.
#   If one argument is specified then its value is used as the input.
#   More than one argument being specified is an error.
#
# Reads stdin or the given string, strips any leading and trailing whitespace,
# then writes the result to stdout, without a trailing newline.
strip_whitespace() {
  emulate -L zsh
  setopt extended_glob warn_create_global no_unset pipe_fail

  if (( # == 0 )); then
    local input="$(<&0)"
  elif (( # == 1 )); then
    local input="$1"
  else
    say_error "$0: expected 0 or 1 arguments, but got $#: $*" >&2
    return 2
  fi

  input=${input##[[:space:]]#}
  input=${input%%[[:space:]]#}
  sayn "$input"
}

# Function: gcu ("git create upstream")
# Arguments:
#   -n: Dry run. Prints the command but does not execute it.
#
# This function is a convenience wrapper around calling
#
#   git push -u origin $branch:$username[/$project]/$branch
#
# The function first determines the local branch name by running 
# `git branch --show-current`. The output from this command, with leading and
# trailing whitespace stripped, will be used for `$branch` in the `git push`
# command.
#
# The function then determines the username by running `git config user.email`.
# The output from this command will be taken up to, but excluding, the first
# `@` character, then all leading and trailing whitespace stripped. The result
# will be used as for `$username` in the `git push` command.
#
# Finally, the function determines the project by running
# `git rev-parse --show-toplevel`, hereafter referred to as the "project
# directory". If the current directory **IS** the project directory then the
# `/$project` component of the `git push` command will be omitted entirely.
# Otherwise the name of the immediate child directory of the project directory
# that is or is a parent of the current directory is considered, hereafter
# referred to as "project child directory". If the project child directory
# contains one or more `-` (dash) characters, then the substring starting after
# the last character is taken, its leading and trailing whitespace is stripped,
# and the resulting value will be used for `$project` in the `git push` command.
#
# For example, suppose the current git branch is named "foo", the user.email
# is developer01@company.com, the current directory is
# /work/product1/foo-server/component1 and the root git directory is
# /work/product1. Then the resulting git command would be:
#
#   git push -u origin foo:developer01/server/foo
gcu() {
  emulate -L zsh
  setopt extended_glob warn_create_global no_unset pipe_fail

  local -A opts
  zparseopts -D -A opts n
  local -i dry_run_enabled=${+opts[-n]}

  if (( # > 0 )); then
    say_error "$0: unexpected arguments: $*" >&2
    return 2
  fi

  local branch
  branch=$(git branch --show-current 2>/dev/null | strip_whitespace)
  if [[ -z "$branch" ]]; then
    say_error "$0: not on a branch or not in a git repository" >&2
    return 1
  fi

  local email
  email=$(git config user.email 2>/dev/null | strip_whitespace)
  if [[ -z "$email" ]]; then
    say_error "$0: git config user.email is not set" >&2
    return 1
  fi

  local username
  username=$(strip_whitespace "${email%%@*}")
  if [[ -z "$username" ]]; then
    say_error "$0: could not determine username from email: $email" >&2
    return 1
  fi

  local project_root
  project_root=$(git rev-parse --show-toplevel 2>/dev/null)
  if [[ -z "$project_root" ]]; then
    say_error "$0: not in a git repository" >&2
    return 1
  fi
  project_root="${project_root:A}"

  local current_dir="${PWD:A}"
  local project_part=""

  if [[ "$current_dir" != "$project_root" ]]; then
    local rel_path=${current_dir#$project_root/}
    local child_dir=${rel_path%%/*}
    local project_name

    if [[ "$child_dir" == *"-"* ]]; then
      project_name=${child_dir##*-}
    else
      project_name=$child_dir
    fi
    project_name=$(strip_whitespace "$project_name")
    project_part="/$project_name"
  fi

  local remote_ref="$username${project_part}/$branch"

  typeset -r git_args=(git push -u origin "$branch:$remote_ref")
  say_args "${git_args[@]}"

  if (( dry_run_enabled )); then
    say_warning "dry run enabled by -n flag; command not executed" >&2
  else
    "${git_args[@]}"
  fi
}

###############################################################################
# Visual Enhancements (Gradients)
###############################################################################

_gradient_preexec() {
  _gradient_cmd_start=$SECONDS
}

# Helper to intelligently shrink the command string based on shell tokens.
_gradient_shrink_cmd() {
  local cmd="$1"
  local limit=$2
  (( limit <= 0 )) && return 1

  # Split into shell words (correctly handles quotes/spaces)
  local -a words
  words=("${(@z)cmd}")

  # Helper to join words and collapse multiple "…" into one
  _join_and_collapse() {
    # 1. Remove empty elements from the array
    local -a filtered
    filtered=("${(@)words:#}")

    # 2. Collapse adjacent ellipses tokens
    local -a final
    local last_w=""
    local w
    for w in "${filtered[@]}"; do
      if [[ "$w" == "…" && "$last_w" == "…" ]]; then
        continue
      fi
      final+=("$w")
      last_w="$w"
    done

    # 3. Join with a single space
    echo "${(j: :)final}"
  }

  local current=$(_join_and_collapse)
  [[ ${#current} -le $limit ]] && echo "$current" && return 0

  # Step 1: Remove flags and their values from right to left
  integer i
  for (( i=${#words}; i > 1; i-- )); do
    # If this word starts with - and the next one doesn't, it's a flag+value pair
    if [[ "${words[i-1]}" == -* && i -lt ${#words} && "${words[i]}" != -* ]]; then
      words[i-1]="…"
      words[i]=""
      current=$(_join_and_collapse)
      [[ ${#current} -le $limit ]] && echo "$current" && return 0
    fi
  done

  # Step 2: Remove remaining flags from right to left
  for (( i=${#words}; i >= 1; i-- )); do
    if [[ "${words[i]}" == -* ]]; then
      words[i]="…"
      current=$(_join_and_collapse)
      [[ ${#current} -le $limit ]] && echo "$current" && return 0
    fi
  done

  # Step 3: Remove intermediate positional arguments, preserving the final argument
  # We do this by continually removing the *penultimate* (second-to-last) real word.
  while (( ${#words} > 2 )); do
    # Find the last actual word (ignore ellipses at the end)
    integer last_idx=${#words}
    while [[ "$last_idx" -gt 0 && "${words[last_idx]}" == "…" ]]; do
       (( last_idx-- ))
    done

    # We need at least two real words to have an "intermediate" one to remove
    (( last_idx < 3 )) && break

    # Find the penultimate word
    integer pen_idx=$(( last_idx - 1 ))
    while [[ "$pen_idx" -gt 1 && "${words[pen_idx]}" == "…" ]]; do
       (( pen_idx-- ))
    done

    # If the penultimate word is just the command itself, we can't remove it
    (( pen_idx <= 1 )) && break

    words[pen_idx]="…"
    current=$(_join_and_collapse)
    [[ ${#current} -le $limit ]] && echo "$current" && return 0
  done

  # Step 4: Blind truncation of whatever is left
  if [[ ${#current} -gt $limit ]]; then
    echo "${current[1,$((limit-1))]}…"
  else
    echo "$current"
  fi
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
  local status_indicator=""

  if (( last_status != 0 )); then
    start_hex="#b82e2e"     # Medium-Dark Crimson (Failure)
    end_hex="#ffb86c"       # Fiery Yellow-Orange (Failure)
    status_indicator="  $last_status"
  fi

  local elapsed_str
  if (( elapsed < 600 )); then
    elapsed_str="${elapsed}s"
  else
    integer mins=$(( elapsed / 60 ))
    integer secs=$(( elapsed % 60 ))
    elapsed_str="${mins}m ${secs}s"
  fi

  local date_long=$(print -P "%D{%a %b %d, %Y}")
  local date_short=$(print -P "%D{%Y-%m-%d}")
  local time_str=$(print -P "%D{%H:%M}")
  local last_cmd=$(fc -ln -1 | xargs)

  local max_len=$(( COLUMNS - 10 ))
  local status_info=""
  local date_part time_part stats_part cmd_part

  # Prepare the parts that don't change
  time_part="  ${time_str}"
  stats_part=" 󰜎 ${elapsed_str}${status_indicator}"

  # Logic Loop: Try different combinations to fit the limit
  # 1. Try Full Date + Intelligent Cmd
  date_part=" 󰸘 ${date_long}"
  integer avail=$(( max_len - ${#date_part} - ${#time_part} - ${#stats_part} - 4 )) # 4 for "  "

  local shrunken_cmd=$(_gradient_shrink_cmd "$last_cmd" $avail)
  if [[ -n "$shrunken_cmd" && ( "$shrunken_cmd" == "$last_cmd" || ${#shrunken_cmd} -ge 3 ) ]]; then
    cmd_part="  ${shrunken_cmd}"
    status_info="${date_part}${time_part}${stats_part}${cmd_part} "
  else
    # 2. Try Short Date + Intelligent Cmd
    date_part=" 󰸘 ${date_short}"
    avail=$(( max_len - ${#date_part} - ${#time_part} - ${#stats_part} - 4 ))
    shrunken_cmd=$(_gradient_shrink_cmd "$last_cmd" $avail)

    if [[ -n "$shrunken_cmd" && ( "$shrunken_cmd" == "$last_cmd" || ${#shrunken_cmd} -ge 3 ) ]]; then
      cmd_part="  ${shrunken_cmd}"
      status_info="${date_part}${time_part}${stats_part}${cmd_part} "
    else      # 3. Drop command, keep Short Date
      status_info="${date_part}${time_part}${stats_part} "
      # 4. Emergency: If even that doesn't fit, drop date
      if [[ ${#status_info} -gt $max_len ]]; then
        status_info="${time_part}${stats_part} "
      fi
      # 5. Emergency: If even that doesn't fit, drop time
      if [[ ${#status_info} -gt $max_len ]]; then
        status_info="${stats_part} "
      fi
    fi
  fi

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
# zsh will ask: zsh: correct 'sl' to 'ls' [nyae]?.
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

# Enable case-insensitive completion.
# The '' first means try exact matches first, then fall back to case-insensitive.
# It also adds some standard "fuzzy matching".
zstyle ':completion:*' matcher-list '' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'

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
  bindkey -M viins '^[[B' history-substring-search-down
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
