#!/bin/bash

# Clones GitHub repositories into the current directory.

set -euo pipefail
set -x

function main {
  setup_repo -d rutt -b main -u https://github.com/denversc/rutt.git -p git@github.com:denversc/rutt.git
}

function setup_repo {
  local dest_dir=""
  local git_branch=""
  local pull_repo_url=""
  local push_repo_url=""

  local OPTIND=1
  local OPTERR=0
  while getopts ":d:b:u:p:o:sy:z:" arg ; do
    case "$arg" in
      d) dest_dir="${OPTARG}" ;;
      b) git_branch="${OPTARG}" ;;
      u) pull_repo_url="${OPTARG}" ;;
      p) push_repo_url="${OPTARG}" ;;
      :)
        echo "ERROR: missing value after option: -${OPTARG}" >&2
        exit 1
        ;;
      ?)
        echo "ERROR: unrecognized option: -${OPTARG}" >&2
        exit 1
        ;;
      *)
        echo "INTERNAL ERROR: unknown argument: $arg" >&2
        exit 1
        ;;
    esac
  done

  if [[ $OPTIND -le $# ]] ; then
    echo "ERROR: unexpected argument: ${!OPTIND}" >&2
    exit 1
  elif [[ -z $dest_dir ]] ; then
    echo "ERROR: -d must be specified" >&2
    exit 1
  elif [[ -z $git_branch ]] ; then
    echo "ERROR: -b must be specified" >&2
    exit 1
  elif [[ -z $pull_repo_url ]] ; then
    echo "ERROR: -u must be specified" >&2
    exit 1
  fi

  (
    mkdir "${dest_dir}"
    local readonly repo_dir="${dest_dir}/.repo"
    local readonly worktree_dir="${dest_dir}/${git_branch}"

    git init --bare "${repo_dir}"

    git --git-dir "${repo_dir}" remote add origin "${pull_repo_url}"
    git --git-dir "${repo_dir}" fetch --no-tags origin

    if [[ ! -z $push_repo_url ]] ; then
      git --git-dir "${repo_dir}" remote set-url origin --push "${push_repo_url}"
    fi

    git --git-dir "${repo_dir}" worktree add -b "${git_branch}" "${worktree_dir}" "remotes/origin/${git_branch}"
  )
}

main
