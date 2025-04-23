cp ~/local/kitty/share/icons/hicolor/scalable/apps/kitty.svg kitty.svg

for size in [16, 22, 32, 48, 64, 128, 256, 512, 1024, 2048]:
  outfile = f"kitty_{size}.png"
  outsize = f"{size}:{size}"
  svgexport kitty.svg @(outfile) @(outsize)
  xdg-icon-resource install --novendor --size @(size) @(outfile) kitty

for f in gp`~/local/kitty/share/applications/*desktop`:
  sed -e "/^TryExec=/d" -e "s#Exec=kitty#Exec=\"$HOME/local/kitty/bin/kitty\"#g" @(f) >@(f.name)
  xdg-desktop-menu install --novendor @(f.name)
