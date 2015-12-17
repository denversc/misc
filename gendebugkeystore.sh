#!/bin/sh

set -xev

exec keytool \
    -genkeypair \
    -alias androiddebugkey \
    -keypass android \
    -keystore debug.keystore \
    -storepass android \
    -dname "CN=Android Debug,O=Android,C=US" \
    -validity 99999 \

