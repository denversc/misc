wget https://gitlab.com/librewolf-community/branding/-/raw/master/icon/icon.svg -O librewolf.svg

for size in [16, 22, 32, 48, 64, 128, 256, 512, 1024, 2048]:
  outfile = f"librewolf_{size}.png"
  outsize = f"{size}:{size}"
  svgexport librewolf.svg @(outfile) @(outsize)
  xdg-icon-resource install --novendor --size @(size) @(outfile) librewolf

~/local/librewolf/LibreWolf.x86_64.AppImage --appimage-extract io.gitlab.LibreWolf.desktop

sed -e "/^TryExec=/d" -e "s#Exec=librewolf#Exec=\"$HOME/local/librewolf/LibreWolf.x86_64.AppImage\"#g" squashfs-root/io.gitlab.LibreWolf.desktop >librewolf.desktop

xdg-desktop-menu install --novendor librewolf.desktop
