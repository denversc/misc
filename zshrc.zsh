# To use this file, add this line to the top of ~/.zshrc:
#
# source "$HOME/misc/zshrc.zsh"

if [[ "$OSTYPE" == "darwin"* ]]; then
  PROMPT='%K{#9da9d1}%F{#000000}  %F{#9da9d1}%K{#6a95e9} %F{#ffffff}%~ %F{#6a95e9}%k'$'\n''%F{#9ece6a}❯ %f'
else
  PROMPT='%K{#9da9d1}%F{#000000}  %F{#9da9d1}%K{#a9c8a1} %F{#000000}%~ %F{#a9c8a1}%k'$'\n''%F{#9ece6a}❯ %f'
fi
