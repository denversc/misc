git clone --depth 1 https://github.com/neovide/neovide.git .

for size in [16, 22, 32, 48, 64, 128, 256, 512, 1024, 2048]:
  outfile = f"neovide_{size}.png"
  outsize = f"{size}:{size}"
  svgexport assets/neovide.svg @(outfile) @(outsize)
  xdg-icon-resource install --novendor --size @(size) @(outfile) neovide

sed -e "/^TryExec=/d" -e "s#Exec=neovide#Exec=\"$HOME/local/homebrew/linuxbrew/.linuxbrew/bin/neovide\" --neovim-bin \"$HOME/local/homebrew/linuxbrew/.linuxbrew/bin/nvim\"#g" assets/neovide.desktop >neovide.desktop

xdg-desktop-menu install --novendor neovide.desktop
