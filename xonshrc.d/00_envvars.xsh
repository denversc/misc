import os
import sys
import tempfile

# Make sure that my custom xonsh library is available.
sys.path.append($HOME + "/misc/xonshlib/src")

# Changing $XXX variables is reflected in os.environ.
# https://xon.sh/envvars.html#update-os-environ
$UPDATE_OS_ENVIRON = True

# Suppress detailed tracebacks, which are occasionally useful but normally
# noisy and distracting.
# https://xon.sh/envvars.html#xonsh-show-traceback
$XONSH_SHOW_TRACEBACK = False

# https://xon.sh/envvars.html#title
$TITLE = "{current_job:{} | } {cwd}"

# Load zsh rc files to set environment variables and aliases.
with tempfile.TemporaryDirectory() as temp_dir_path:
  empty_file_path = os.path.join(temp_dir_path, "empty.zsh")
  open(empty_file_path, "w").close()
  if $XONSH_INTERACTIVE and $XONSH_LOGIN:
    source-zsh --interactive --login @(empty_file_path)
  elif $XONSH_INTERACTIVE:
    source-zsh --interactive @(empty_file_path)
  elif $XONSH_LOGIN:
    source-zsh --login @(empty_file_path)
  else:
    source-zsh @(empty_file_path)

  del temp_dir_path
  del empty_file_path

# Clean up global namespace
del tempfile
del sys
del os
