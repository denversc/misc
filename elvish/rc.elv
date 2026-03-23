set-env TZ "America/New_York"

# Alias "ls" to "lsd"
fn ls { |@args| e:lsd $@args }

# https://starship.rs/guide/
eval (starship init elvish)

# https://carapace-sh.github.io/carapace-bin/setup.html#elvish
set-env CARAPACE_BRIDGES 'zsh,inshellisense'
eval (carapace _carapace|slurp)

# https://github.com/ajeetdsouza/zoxide
eval (zoxide init --cmd f elvish | slurp)

# Creates a unique directory in ~/tmp and cd's into it.
# An optional positional argument specifies the prefix for the directory name.
fn mkd {|@args|
  if (> (count $args) 1) {
    fail "mkd: too many arguments; unexpected argument: "$args[1]
  }

  var name = tmp
  if (> (count $args) 0) {
    set name = $args[0]
  }

  mkdir -p ~/tmp
  cd (mktemp -d ~/tmp/$name"XXXXXXXXXX")
}
