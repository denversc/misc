# See https://xon.sh/envvars.html

if $XONSH_INTERACTIVE:

  $AUTO_SUGGEST_IN_COMPLETIONS = False
  $COMPLETIONS_CONFIRM = False
  $COMPLETION_IN_THREAD = True
  $COMPLETION_MODE = "menu-complete"
  $ENABLE_ASYNC_PROMPT = True
  $HISTCONTROL = set(["ignoredups", "ignoreerr", "ignorespace", "erasedups"])
  $VI_MODE = True
  $XONSH_HISTORY_BACKEND = "sqlite"
  $XONSH_HISTORY_SIZE = "10000 commands"
  $XONSH_USE_SYSTEM_CLIPBOARD = False

  # Setup JAVA_HOME based on the JDK installed and/or configured by asdf.
  # See https://github.com/halcyon/asdf-java#java_home
  asdf_javahome_script = p"$ASDF_DATA_DIR/plugins/java/set-java-home.xsh"
  if asdf_javahome_script.exists():
    source @(asdf_javahome_script)
  del asdf_javahome_script
