#!/bin/zsh

set -e -u -o pipefail

exec podman run -it \
  -v /Volumes/dev/gcloud-podman/config:/root/.config/gcloud:Z \
  -v /Volumes/dev/gcloud-podman/dev01-493607-71c679891ef4.json:/root/dev01-493607-71c679891ef4.json:Z \
  -v /Volumes/dev/gcloud-podman/misc:/root/misc:Z \
  gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine \
  /bin/bash

# Useful commands from within the container:
#
# gcloud auth activate-service-account --key-file=/root/dev01-493607-71c679891ef4.json
# gcloud config set project dev01-493607
# gcloud compute instances start dev01
# gcloud compute instances stop dev01
