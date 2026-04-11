#!/bin/bash

set -euo pipefail
set -v

echo "# Created by $0" >starship.green.toml
echo >>starship.green.toml
sed 's/#a3aed2/#a3d2a5/g; s/#769ff0/#76f08a/g; s/fg:#e3e5e5 bg:#76f08a/fg:#090c0c bg:#76f08a/g' starship.toml >> starship.green.toml
