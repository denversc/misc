---
title: 'Denver''s Linux Setup Instructions'
lang: 'en'
---

<!--
Here are instructions to use "pandoc" to produce HTML from this document.

Install pandoc using homebrew:

  brew install pandoc

Then run this command to produce HTML from this file:

  pandoc -s --toc -o LinuxSetup.html -f commonmark_x -t html LinuxSetup.md

If editing this document, it may be useful to run the pandoc command
automatically every time that this file changes. The Python "watchdog" library
can be used for this. Install it by running:

  pip install -U watchdog

If using the asdf package manager, run

  asdf reshim python

Then, the "watchmedo" command can run pandoc upon changes to this file:

  watchmedo shell-command -w -p LinuxSetup.md -c 'pandoc -s --toc -o LinuxSetup.html -f commonmark_x -t html LinuxSetup.md'
-->

## Kitty Terminfo {#kitty-terminfo}

Install Kitty's terminfo files so that ssh sessions over Kitty will properly
access the terminal:

```bash
sudo apt install kitty-terminfo
```

## Misc Github Repo

Clone my personal "misc" GitHub repository
<https://github.com/denversc/misc.git> by running:

```bash
git clone https://github.com/denversc/misc.git ~/misc
git -C ~/misc remote set-url origin --push git@github.com:denversc/misc.git
```

## zsh setup

Upon first login, you will be prompted to initialize `~/.zshrc`.
When prompted, select the option "Populate your ~/.zshrc with the configuration
recommended by the system administrator and exit".

If you get an error message like "Error opening terminal: xterm-kitty" then
either re-connect via ssh using a standard terminal emulator or install Kitty's
terminfo files, as outlined in [Kitty Terminfo].

Set up zsh's init files to use the ones from the "misc" GitHub repository:

```bash
echo "source \"$HOME/misc/zshenv.zsh\"" > ~/.zshenv
echo "source \"$HOME/misc/zshrc.zsh\"" > ~/.zshrc
echo "source \"$HOME/misc/zprofile.zsh\"" > ~/.zprofile

# Optional, for a custom prompt color theme, select one of these:
echo "prompt adam1 red yellow magenta" >>~/.zshrc
echo "prompt adam1 green blue blue" >>~/.zshrc
```

## Homebrew

On some Linux systems, the `/home` directory is readonly. But homebrew wants to
use `/home/linuxbrew` to install bottles (precompiled binaries). As a
workaround, create a directory in `~/local` and bind-mount it to `/home`.
Note that the mount command below will need to be re-executed after each reboot.

```bash
# Set up the directory.
mkdir -p ~/local/homebrew/
echo "This directory is intended to be bind-mounted to /home by running:\nsudo mount --bind ~/local/homebrew /home" >~/local/homebrew/README.txt

# Bind-mount the directory.
# This command will need to be re-run after each reboot.
sudo mount --bind ~/local/homebrew /home
```

Now, install homebrew as per the instructions at <https://brew.sh/>.
At the time of writing (Feb 28, 2025) the instructions are to run this:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then, add the following line above the "source" line in `~/.zprofile`:

```bash
export HOMEBREW_PREFIX=/home/linuxbrew/.linuxbrew
```

Use my personal homebrew settings from the misc github repository:

```bash
mkdir ~/.config/homebrew
ln -sf ~/misc/brew.env ~/.config/homebrew/brew.env
```

Finally, install some commonly-needed things:

```bash
brew analytics off
sudo apt install build-essential
brew install aria2 bat coreutils fd fzf git-delta glow lazygit lsd neovim ripgrep zoxide gcc ninja
```

## Git

```bash
cp ~/misc/.gitconfig ~/.gitconfig
git config --global user.name "Denver Coneybeare"
git config --global user.email "dconeybe@google.com"
```

## JetBrainsMono Nerd Font

Install the JetBrainsMono Nerd Font <https://www.nerdfonts.com> by running:

```bash
mkdir -p ~/.local/share/fonts
cd ~/.local/share/fonts
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/JetBrainsMono.zip
unzip JetBrainsMono.zip
mv README.md README.JetBrainsMono.md
fc-cache -fv
```

These instructions were adapted from
<https://medium.com/@almatins/install-nerdfont-or-any-fonts-using-the-command-line-in-debian-or-other-linux-f3067918a88c>.

## Kitty Terminal Emulator

Install Kitty's terminfo files so that ssh sessions over Kitty will properly
access the terminal:

```bash
sudo apt install kitty-terminfo
```

Do not install Kitty itself via apt as it will install an outdated version;
however, having Kitty's terminfo file installed in the standard location will
make things "just work"™ when using Kitty.

To install Kitty, follow the instructions at
<https://sw.kovidgoyal.net/kitty/binary>. Namely, download a binary bundle from
the GitHub Releases page.

```bash
mkdir -p ~/local/kitty
cd ~/local/kitty
wget https://github.com/kovidgoyal/kitty/releases/download/v0.41.0/kitty-0.41.0-x86_64.txz
tar xf kitty-0.41.0-x86_64.txz
```

Then add symlinks to ensure that Kitty is in the `PATH`:

```bash
mkdir -p ~/.local/bin
ln -s ~/local/kitty/bin/kitty ~/.local/bin/kitty
ln -s ~/local/kitty/bin/kitten ~/.local/bin/kitten
```

Finally, set up Kitty’s configuration files:

```bash
rm -rf ~/.config/kitty
ln -s ~/misc/kitty ~/.config/kitty
git clone https://github.com/yurikhan/kitty_grab ~/misc/kitty/kitty_grab
```

Check if there are any additional instructions in `~/misc/kitty/README.txt`.

If desired, create a desktop entry for Kitty.
You may need to come back to this step after installing xonsh and svgexport,
as documented below:

```default
# Note: this code block is in xonsh syntax.

$RAISE_SUBPROC_ERROR = True
cd $(mktemp -d kitty_desktop_XXXXXX)
cp ~/local/kitty/share/icons/hicolor/scalable/apps/kitty.svg kitty.svg

for size in [16, 22, 32, 48, 64, 128, 256, 512, 1024, 2048]:
  outfile = f"kitty_{size}.png"
  outsize = f"{size}:{size}"
  svgexport kitty.svg @(outfile) @(outsize)
  xdg-icon-resource install --novendor --size @(size) @(outfile) kitty

for f in gp`~/local/kitty/share/applications/*desktop`:
  sed -e "/^TryExec=/d" -e "s#Exec=kitty#Exec=\"$HOME/local/kitty/bin/kitty\"#g" @(f) >@(f.name)
  xdg-desktop-menu install --novendor @(f.name)

rm -rf "$PWD"
```

## Neovim

```bash
brew install neovim
rm -rf ~/.config/nvim
ln -s ~/misc/nvim ~/.config/nvim
```

Uninstall classic vim. First, list the packages for classic vim:

```bash
apt list --installed | grep vim
```

then remove each of the packages, like this:

```bash
sudo apt remove vim-common vim-runtime vim-tiny vim
```

Set up some convenience integrations between git and nvim:

```bash
git config --global core.editor "$EDITOR -S $HOME/misc/nvim_git_editor.lua"
```

## Neovide

Neovide, a neovim wrapper with a nice GUI, takes a bit of extra work.

```bash
brew install neovide
```

Add a desktop entry for neovide so that it can be launched from gnome.
Note that the absolute path to neovide and nvim is the directory inside
~/local/homebrew rather than `/home/linuxbrew` because the latter is not
available until the bind-mount for `/home` is executed. As a result,
the neovide binary will not exist upon reboot and the icon will, therefore, be
absent from the toolbar. This nuisance can be fixed by using the path that is
not bind-mounted. You may need to come back to this step after installing
xonsh and svgexport, as documented below.

```default
# Note: this code block is in xonsh syntax.

$RAISE_SUBPROC_ERROR = True
cd $(mktemp -d neovide_desktop_XXXXXX)
git clone --depth 1 https://github.com/neovide/neovide.git .

for size in [16, 22, 32, 48, 64, 128, 256, 512, 1024, 2048]:
  outfile = f"neovide_{size}.png"
  outsize = f"{size}:{size}"
  svgexport assets/neovide.svg @(outfile) @(outsize)
  xdg-icon-resource install --novendor --size @(size) @(outfile) neovide

sed -e "/^TryExec=/d" -e "s#Exec=neovide#Exec=\"$HOME/local/homebrew/linuxbrew/.linuxbrew/bin/neovide\" --neovim-bin \"$HOME/local/homebrew/linuxbrew/.linuxbrew/bin/nvim\"#g" assets/neovide.desktop >neovide.desktop

xdg-desktop-menu install --novendor neovide.desktop

rm -rf "$PWD"
```

## LibreWolf

Install the LibreWolf browser <https://librewolf.net>.
Download the AppImage and add a desktop link to it.
Get the URL of the latest AppImage from the web site.

```bash
mkdir -p ~/local/librewolf
wget https://gitlab.com/api/v4/projects/24386000/packages/generic/librewolf/136.0.4-1/LibreWolf.x86_64.AppImage -O ~/local/librewolf/LibreWolf.x86_64.AppImage
chmod 755 ~/local/librewolf/LibreWolf.x86_64.AppImage
```

Then create a desktop entry for LibreWolf.
You may need to come back to this step after installing xonsh and svgexport,
as documented below:

```default
# Note: this code block is in xonsh syntax.

$RAISE_SUBPROC_ERROR = True
cd $(mktemp -d librewolf_desktop_XXXXXX)
wget https://gitlab.com/librewolf-community/branding/-/raw/master/icon/icon.svg -O librewolf.svg

for size in [16, 22, 32, 48, 64, 128, 256, 512, 1024, 2048]:
  outfile = f"librewolf_{size}.png"
  outsize = f"{size}:{size}"
  svgexport librewolf.svg @(outfile) @(outsize)
  xdg-icon-resource install --novendor --size @(size) @(outfile) librewolf

~/local/librewolf/LibreWolf.x86_64.AppImage --appimage-extract io.gitlab.LibreWolf.desktop

sed -e "/^TryExec=/d" -e "s#Exec=librewolf#Exec=\"$HOME/local/librewolf/LibreWolf.x86_64.AppImage\"#g" squashfs-root/io.gitlab.LibreWolf.desktop >librewolf.desktop

xdg-desktop-menu install --novendor librewolf.desktop

rm -rf "$PWD"
```

You should now be able to launch LibreWolf from the desktop shell.

## asdf Version Manager

Install the asdf version manager <https://asdf-vm.com/> by running:

```bash
brew install asdf
```

Restart your shell

## Python

First, install Python's build dependencies, as documented at
<https://devguide.python.org/getting-started/setup-building/#build-dependencies>.
Then, use asdf to install the latest version of Python
<https://github.com/asdf-community/asdf-python>:

```bash
sudo apt-get build-dep python3
sudo apt-get install build-essential gdb lcov pkg-config libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev libncurses-dev libreadline6-dev libsqlite3-dev libssl-dev lzma tk-dev uuid-dev zlib1g-dev

asdf plugin add python
asdf install python 3.13.2
asdf set -u python 3.13.2
```

The dependencies installed via brew were taken from
<https://github.com/pyenv/pyenv/wiki#suggested-build-environment>.
Check that those are up-to-date.

## Xonsh

Install the xonsh shell <https://xon.sh/>:

```bash
mkdir -p ~/local
python -m venv ~/local/xonsh
source ~/local/xonsh/bin/activate
pip install --upgrade pip
pip install 'xonsh[full]'
ln -s ~/local/xonsh/bin/xonsh ~/.local/bin/xonsh
```

Start xonsh and install its dependencies:

```bash
xpip install xontrib-dalias xontrib-macro xontrib-vox xontrib-kitty xontrib-term-integrations xontrib-jedi xontrib-zoxide
```

Run the setup instructions in `~/misc/xonshrc.d/README.txt`
to configure the rc files.

## Node.js

Install Node.js with the asdf version manager
<https://asdf-vm.com/guide/getting-started.html#_4-install-a-plugin>.

```bash
asdf plugin add nodejs

asdf list-all nodejs # optional, to pick the version to use

asdf install nodejs 22.14.0
asdf set -u nodejs 22.14.0
```

Choose the latest LTS version as the default,
which, at the time of writing (Feb 28, 2025) is 22.14.0
according to <https://nodejs.org/en/download/current>.

## svgexport

svgexport converts svg files to png files.
This is required for some of the steps below to generate desktop icons.

```bash
npm install -g svgexport
asdf reshim nodejs
```

## firebase-tools

The firebase command-line tool is installed via Node.js:

```bash
npm install -g firebase-tools
asdf reshim nodejs
```

## Java Development Kit

Install JDK with asdf <https://github.com/halcyon/asdf-java>:

```bash
asdf plugin add java

asdf list-all java # optional, to pick the version to use

asdf install java temurin-17.0.14+7
asdf set -u java temurin-17.0.14+7
```

Note that the xonsh rc files in misc will automatically set `JAVA_HOME`
as appropriate for asdf.
See <https://github.com/denversc/misc/commit/7dc8b7bbdd>.

## Work Git Repositories

```bash
git clone sso://user/dconeybe/firebase-misc ~/work/misc
cd ~/work
./misc/repo_setup.sh
```

## bat

Install and configure bat (advanced cat) <https://github.com/sharkdp/bat>:

```bash
brew install bat
mkdir -p ~/.config/bat
ln -sf ~/misc/bat_config.txt ~/.config/bat/config
```

## fd

Install and configure fd (advanced find) <https://github.com/sharkdp/fd>:

```bash
brew install fd
```

## lsd

Install and configure lsd (advanced ls) <https://github.com/lsd-rs/lsd>:

```bash
brew install lsd
mkdir -p ~/.config/lsd
ln -sf ~/misc/lsd.config.yaml ~/.config/lsd/config.yaml
```

## Ranger file manager w/ Kitty integration

Install and configure Ranger <https://github.com/ranger/ranger>:

```bash
brew install ranger pillow
mkdir ~/.config/ranger
echo "set preview_images true" >>~/.config/ranger/rc.conf
echo "set preview_images_method kitty" >>~/.config/ranger/rc.conf
```

Note that the pillow library is required to support image previews.

## Cmake

Use asdf to install cmake, so it's easy to switch between versions:

```bash
asdf plugin add cmake

asdf list all cmake # optional, to pick the version to use

asdf install cmake 3.31.6
asdf set -u cmake 3.31.6
```

## Gradle

Use asdf to install Gradle, so it’s easy to switch between versions:

```bash
asdf plugin add gradle https://github.com/rfrancis/asdf-gradle.git

asdf list all gradle # optional, to pick the version to use

asdf install gradle 8.13
asdf set -u gradle 8.13
```

Set a global gradle.properties to get desirable behavior, by default:

```bash
mkdir ~/.gradle
cp ~/misc/gradle.properties ~/.gradle/gradle.properties

## Update org.gradle.java.home in ~/.gradle/gradle.properties to the asdf-configured JVM.
asdf which javac
```

## clang-format

Use asdf to install clang-format, so it’s easy to switch between versions,
especially since the firebase-ios-sdk requires a specific version:

```bash
# Install dependencies of the asdf-clang-format plugin.
pip install requests sigstore tqdm

asdf plugin add clang-format https://github.com/dconeybe/asdf-clang-format

asdf list all clang-format # optional, to pick the version to use

asdf install clang-format 20.1.0
asdf set -u clang-format 20.1.0
```

## Podman

Install podman using the standard apt tool,
followed by some required customizations.
The customizations were adapted from
<http://g3doc/company/users/aaronyu/podman.md>

```bash
sudo apt install podman

# Determine your uid
id -u

# Pick a number that is larger than your userid (e.g. 600000).
sudo usermod --add-subuids 600000-665535 --add-subgids 600000-665535 dconeybe

# Check if they're added to the system:
grep dconeybe /etc/sub*id

# You should see:
# /etc/subgid:dconeybe:600000:65536
# /etc/subuid:dconeybe:600000:65536

# Maybe restart your user session for the new uid/gid mapping to take effect.
```

Test out  the installation by running an Alpine Linux container:

```bash
podman run -it --rm alpine:latest
```
