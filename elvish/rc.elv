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
