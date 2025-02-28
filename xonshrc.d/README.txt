This is the run-control directory for the xonsh shell.
See https://xon.sh/xonshrc.html

To use this configuration, run the following commands:
mkdir -p "$HOME/.config/xonsh"
ln -sf "$PWD" "$HOME/.config/xonsh/rc.d"
sed -e "s#PWD#$PWD#g" rc.local.xsh.template >"$HOME/.config/xonsh/rc.local.xsh"
