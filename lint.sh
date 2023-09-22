#!/bin/bash

if [[ $# -gt 0 ]] ; then
  readonly pyflakes_args=(pyflakes "$@")
else
  readonly pyflakes_args=(pyflakes *.py)
fi

echo "${pyflakes_args[*]}"
"${pyflakes_args[@]}"
