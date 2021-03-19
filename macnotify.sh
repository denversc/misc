#!/bin/bash

###############################################################################
# macnotify.sh
# By: Denver Coneybeare
# Mar 19, 2021
#
# Displays a notification on a Mac computer. This is useful to append to the
# end of a long command to let you know that it's completed.
###############################################################################

set -euo pipefail

if [[ $# -eq 0 ]] ; then
  echo "ERROR: no arguments specified" >&2
  echo "Syntax: $0 [title] <message>" >&2
  exit 2
elif [[ $# -eq 1 ]] ; then
  readonly TITLE="$0"
  readonly MESSAGE="$1"
elif [[ $# -eq 2 ]] ; then
  readonly TITLE="$1"
  readonly MESSAGE="$2"
elif [[ $# -gt 2 ]] ; then
  echo "ERROR: unexpected argument: $3" >&2
  exit 2
fi

exec osascript -e "display notification \"${MESSAGE}\" with title \"${TITLE}\""
