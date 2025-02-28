# See https://xon.sh/tutorial.html#aliases

from dconeybe.xonsh.aliases import rnd as dconeybe_rnd
aliases["rnd"] = dconeybe_rnd.rnd
del dconeybe_rnd

from dconeybe.xonsh.aliases import abspath as dconeybe_abspath
aliases["abspath"] = dconeybe_abspath.abspath
del dconeybe_abspath

aliases["ls"] = ["lsd", "--hyperlink=always"]

aliases["good"] = "echo 'SUCCESS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'"

# Show a desktop notification (a.k.a. "popup").
# https://sw.kovidgoyal.net/kitty/kittens/notify/
aliases["pop"] = ["kitten", "notify"]

# Enable hyperlinks in ripgrep.
# https://sw.kovidgoyal.net/kitty/kittens/hyperlinked_grep
aliases["rg"] = ["rg", "--hyperlink-format=kitty"]
