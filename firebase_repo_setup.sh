#!/bin/bash

# Clones the GitHub repositories for Firestore development into the current directory.

set -euo pipefail
set -x

function main {
  setup_repo -d firebase-tools -b main -u https://github.com/firebase/firebase-tools.git -p git@github.com:firebase/firebase-tools.git
  setup_repo -d js -b main -u https://github.com/firebase/firebase-js-sdk.git -p git@github.com:firebase/firebase-js-sdk.git
  setup_repo -d android -b main -u https://github.com/firebase/firebase-android-sdk.git -p git@github.com:firebase/firebase-android-sdk.git -s
  setup_repo -d ios -b main -u https://github.com/firebase/firebase-ios-sdk.git -p git@github.com:firebase/firebase-ios-sdk.git
  setup_repo -d data-connect-ios -b main -u https://github.com/firebase/data-connect-ios-sdk.git -p git@github.com:firebase/data-connect-ios-sdk.git
  setup_repo -d cpp -b main -u https://github.com/firebase/firebase-cpp-sdk.git -p git@github.com:firebase/firebase-cpp-sdk.git
  setup_repo -d unity -b main -u https://github.com/firebase/firebase-unity-sdk.git -p git@github.com:firebase/firebase-unity-sdk.git
  setup_repo -d google-cloud-node -b main -u https://github.com/googleapis/google-cloud-node.git -p git@github.com:googleapis/google-cloud-node.git
  setup_repo -d google-cloud-java -b main -u https://github.com/googleapis/google-cloud-java.git -p git@github.com:googleapis/google-cloud-java.git
  setup_repo -d google-cloud-python -b main -u https://github.com/googleapis/google-cloud-python.git -p git@github.com:googleapis/google-cloud-python.git
  setup_repo -d admin-node -b main -u https://github.com/firebase/firebase-admin-node.git -p git@github.com:firebase/firebase-admin-node.git
  setup_repo -d admin-java -b main -u https://github.com/firebase/firebase-admin-java.git -p git@github.com:firebase/firebase-admin-java.git
  setup_repo -d admin-python -b main -u https://github.com/firebase/firebase-admin-python.git -p git@github.com:firebase/firebase-admin-python.git
  setup_repo -d quickstart-js -b master -u https://github.com/firebase/quickstart-js.git -p git@github.com:firebase/quickstart-js.git
  setup_repo -d quickstart-android -b master -u https://github.com/firebase/quickstart-android.git -p git@github.com:firebase/quickstart-android.git
  setup_repo -d quickstart-ios -b main -u https://github.com/firebase/quickstart-ios.git -p git@github.com:firebase/quickstart-ios.git
  setup_repo -d quickstart-cpp -b main -u https://github.com/firebase/quickstart-cpp.git -p git@github.com:firebase/quickstart-cpp.git
  setup_repo -d quickstart-unity -b master -u https://github.com/firebase/quickstart-unity.git -p git@github.com:firebase/quickstart-unity.git
  setup_repo -d flutterfire -b main -u https://github.com/firebase/flutterfire.git -p git@github.com:firebase/flutterfire.git
  setup_repo -d team -b main -u git@github.com:FirebasePrivate/firestore-team.git
  #git clone sso://user/dconeybe/firebase-misc misc
}

function setup_repo {
  local dest_dir=""
  local git_branch=""
  local git_origin="origin"
  local pull_repo_url=""
  local push_repo_url=""
  local git_origin2=""
  local git_origin2_repo_url=""
  local git_submodules_init=0

  local OPTIND=1
  local OPTERR=0
  while getopts ":d:b:u:p:o:sy:z:" arg ; do
    case "$arg" in
      d) dest_dir="${OPTARG}" ;;
      b) git_branch="${OPTARG}" ;;
      u) pull_repo_url="${OPTARG}" ;;
      p) push_repo_url="${OPTARG}" ;;
      o) git_origin="${OPTARG}" ;;
      s) git_submodules_init=1 ;;
      y) git_origin2="${OPTARG}" ;;
      z) git_origin2_repo_url="${OPTARG}" ;;
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

  if [[ ! -z $git_origin2 ]] && [[ -z $git_origin2_repo_url ]] ; then
    echo "ERROR: -y was specified, but -z was not specified, and BOTH or neither must be specified" >&2
    exit 1
  elif [[ -z $git_origin2 ]] && [[ ! -z $git_origin2_repo_url ]] ; then
    echo "ERROR: -z was specified, but -y was not specified, and BOTH or neither must be specified" >&2
    exit 1
  fi

  (
    mkdir "${dest_dir}"
    local readonly repo_dir="${dest_dir}/.repo"
    local readonly worktree_dir="${dest_dir}/${git_branch}"

    git init --bare "${repo_dir}"

    git --git-dir "${repo_dir}" remote add "${git_origin}" "${pull_repo_url}"
    git --git-dir "${repo_dir}" fetch --no-tags "${git_origin}"

    if [[ ! -z $push_repo_url ]] ; then
      git --git-dir "${repo_dir}" remote set-url "${git_origin}" --push "${push_repo_url}"
    fi

    if [[ ! -z $git_origin2 ]] && [[ ! -z $git_origin2_repo_url ]] ; then
      git --git-dir "${repo_dir}" remote add "${git_origin2}" "${git_origin2_repo_url}"
      git --git-dir "${repo_dir}" fetch --no-tags "${git_origin2}"
    fi

    git --git-dir "${repo_dir}" worktree add -b "${git_branch}" "${worktree_dir}" "remotes/${git_origin}/${git_branch}"

    if [[ $git_submodules_init == "1" ]] ; then
      git -C "${worktree_dir}" submodule init
      git -C "${worktree_dir}" submodule update
    elif [[ $git_submodules_init != "0" ]] ; then
      echo "ERROR: internal error swfdf3n6a7: invalid git_submodules_init: ${git_submodules_init}" >&2
      exit 1
    fi
  )
}

main
