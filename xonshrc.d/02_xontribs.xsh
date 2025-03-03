if $XONSH_INTERACTIVE:

  xontrib load coreutils

  # Requires: pip install xontrib-dalias
  # Adds decorators like @lines and @path.
  # e.g. $(@lines ls /) produces a list of strings, rather than a single string.
  # https://github.com/anki-code/xontrib-dalias
  xontrib load dalias

  # Requires: pip install xontrib-macro
  # https://github.com/anki-code/xontrib-macro
  xontrib load macro
  from xonsh.contexts import Block
  from xontrib.macro.data import Write
  from xontrib.macro.data import XmlBlock
  from xontrib.macro.run import Once

  # Requires: pip install xontrib-vox
  # https://xon.sh/python_virtual_environments.html
  xontrib load vox

  # Requires: pip install xontrib-kitty
  xontrib load kitty

  # Requires pip install xontrib-term-integrations
  # This _must_ be imported _after_ setting $PROMPT.
  xontrib load term_integration

  # Requires pip install xontrib-jedi
  xontrib load jedi

  # Requires pip install xontrib-zoxide
  xontrib load zoxide
