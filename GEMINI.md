# Miscellaneous scripts and configuration files

This git repository contains personal configuration files and scripts.

## Repository contents

This section provides a high-level overview of the files and directories in this repository.

### Zsh init scripts

The following files are used as the init scripts for the zsh shell:

* `zprofile.zsh`
  * sourced from ~/.zprofile
  * initializes environment variables that may be overridden by subshells
* `zshenv.zsh`
  * sourced from ~/.zshenv
  * sets XDG environment variables (e.g. XDG_DATA_HOME, XDG_CONFIG_HOME)
  * prepends ~/.local/bin to the path
* `zshrc.zsh`
  * sourced from ~/.zshrc
  * adds utility functions like "say", "good", "bad", and "mkd"
  * sets up a fancy prompt, key bindings, competions, and the like

## Git information

Refer to `docs/git.md` to understand how to interact with this repository with the
`git` command-line tool. For example, how to format git commit messages.
