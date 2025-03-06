# See https://xon.sh/tutorial.html#aliases

from collections.abc import Sequence

@aliases.return_command
def ssh_to_lb_alias(args: Sequence[str]) -> list[str]:
  """
  Convenience alias to ssh to my cloudtop instance.
  """
  final_args = [
    "ssh",
    "lb",
    "-t",
    "/usr/local/google/home/dconeybe/.local/bin/xonsh",
    "--login",
    "--interactive",
  ]

  kitty_public_key = ${...}.get("KITTY_PUBLIC_KEY")
  if kitty_public_key:
    final_args.extend([
      "-D",
      "KITTY_PUBLIC_KEY='" + ${...}.get("KITTY_PUBLIC_KEY", "") + "'",
    ])

  final_args.extend(args)

  return final_args


def register_my_aliases() -> None:
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

  # Convenience wrapper to ssh to my cloudtop instance.
  aliases["slb"] = ssh_to_lb_alias


# Only register aliases in interactive mode.
if $XONSH_INTERACTIVE:
  register_my_aliases()


# Clean up global namespace
del register_my_aliases
del ssh_to_lb_alias
