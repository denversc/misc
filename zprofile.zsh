# To use this file, add this line to the top of ~/.zprofile:
#
# source "$HOME/misc/zprofile.zsh"

# Add ANDROID_HOME related directories to the PATH.
#
# See https://developer.android.com/tools/variables

if [[ -n "$ANDROID_HOME" ]] ; then
  export ANDROID_NDK_HOME="$ANDROID_HOME/ndk/25.1.8937393"
  export PATH="$ANDROID_HOME/tools:$PATH"
  export PATH="$ANDROID_HOME/tools/bin:$PATH"
  export PATH="$ANDROID_HOME/platform-tools:$PATH"
fi
