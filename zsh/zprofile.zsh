# To use this file, add this line to the top of ~/.zprofile:
#
# source "$HOME/misc/zprofile.zsh"

# Add ANDROID_HOME related directories to the PATH.
#
# See https://developer.android.com/tools/variables

if [[ -n $ANDROID_HOME ]] ; then
  export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/25.1.8937393
  if (( ! ${path[(I)$ANDROID_HOME/tools]} )); then
    path=($ANDROID_HOME/tools $path)
  fi
  if (( ! ${path[(I)$ANDROID_HOME/tools/bin]} )); then
    path=($ANDROID_HOME/tools/bin $path)
  fi
  if (( ! ${path[(I)$ANDROID_HOME/platform-tools]} )); then
    path=($ANDROID_HOME/platform-tools $path)
  fi
fi
