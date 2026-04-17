#!/bin/zsh

set -e -u -o pipefail

exec podman run -it \
  -v ~/.config/gcloud-podman:/root/.config/gcloud:Z \
  -v ~/misc:/root/misc:Z \
  gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine \
  /bin/bash
