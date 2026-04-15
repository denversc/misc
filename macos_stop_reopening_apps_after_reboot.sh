#!/bin/bash

# This script configures macOS to prevent applications from automatically
# relaunching after a system reboot or logout.
#
# It achieves this by modifying the 'com.apple.loginwindow' preferences:
#
# 1. TALLogoutSavesState: Setting this to 'false' prevents macOS from saving
#    the state of open applications when the user logs out. This is equivalent
#    to unchecking the "Reopen windows when logging back in" checkbox in the
#    logout/restart dialog.
#
# 2. LoginwindowLaunchesRelaunchApps: Setting this to 'false' ensures that the
#    login window process does not attempt to relaunch any applications that
#    were previously open, even if their state was somehow saved.

set -euo pipefail
set -xv

defaults write com.apple.loginwindow TALLogoutSavesState -bool false

defaults write com.apple.loginwindow LoginwindowLaunchesRelaunchApps -bool false
