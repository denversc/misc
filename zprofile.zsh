# To use this file, run this command:
# echo "source \"$PWD/zshrc.zshrc\"" > ~/.zshrc
#
# If Homebrew is installed, set HOMEPREW_PREFIX prior to the "source" line.

# Enable Homebrew package manager.
# The caller must have $HOMEBREW_PREFIX defined.
# https://docs.brew.sh/Manpage#shellenv-shell-
if [[ -v HOMEBREW_PREFIX ]] ; then
  eval "$("$HOMEBREW_PREFIX/bin/brew" shellenv)"
fi

# Set up nvim to be used as the editor, pager, and manpager.
if [[ -v HOMEBREW_PREFIX ]] ; then
  readonly nvim_path="$(brew --prefix neovim)/bin/nvim"
  if [[ -e $nvim_path ]] ; then
    export EDITOR="$nvim_path"
    export MANPAGER="$nvim_path +Man!"
  fi
fi

# asdf version manager (https://asdf-vm.com/guide/getting-started.html).
export ASDF_DATA_DIR="${XDG_STATE_HOME:?XDG_STATE_HOME is not set}/asdf"
export PATH="$ASDF_DATA_DIR/shims:$PATH"

# Rust setup.
if [[ -e "$HOME/.cargo/env" ]] ; then
  source "$HOME/.cargo/env"
fi

# https://developer.android.com/tools/variables
export ANDROID_HOME="$HOME/local/android_sdk"
export ANDROID_NDK_HOME="$ANDROID_HOME/ndk/25.1.8937393"
export PATH="$ANDROID_HOME/tools:$PATH"
export PATH="$ANDROID_HOME/tools/bin:$PATH"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

# Developer Builds in Prod (http://go/dbip)
export REPLACE_BLAZE_WITH_DBIP=1
