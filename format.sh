#!/bin/bash

if [[ $# -gt 0 ]] ; then
  readonly pyink_file_args=("$@")
else
  readonly pyink_file_args=(*.py)
fi

readonly pyink_args=(
  pyink
  --line-length 100
  --target-version py311
  --pyink
  --pyink-indentation 2
  "${pyink_file_args[@]}"
)

echo "${pyink_args[*]}"
"${pyink_args[@]}"
