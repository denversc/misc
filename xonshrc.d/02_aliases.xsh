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


def create_and_cd_into_temp_dir(args, stdout, stderr, spec) -> list[str]:
  from dconeybe.xonsh.aliases.argparse import AliasArgumentParser
  arg_parser = AliasArgumentParser(spec=spec, usage="%(prog)s [name]")
  arg_parser.add_argument(
    "name",
    nargs="?",
    help="The name of the temporary directory to use; " +
      "if empty (the default) then just use a random string."
  )

  parsed_args = arg_parser.parse_alias_args(args, stdout, stderr)
  if isinstance(parsed_args, int):
    return parsed_args
  del arg_parser

  match parsed_args.name:
    case None | "":
      name = "XXXXXXXXXX"
    case str(name):
      name = name + "_XXXXXXXXXX"
    case name:
      raise Exception(f"internal error fk5gw3ynhy: unsupported name: {name}")

  cd $(mktemp -d -p ~/tmp @(name))


def register_my_aliases() -> None:
  from dconeybe.xonsh.aliases import rnd as dconeybe_rnd
  aliases["rnd"] = dconeybe_rnd.rnd
  del dconeybe_rnd

  from dconeybe.xonsh.aliases import abspath as dconeybe_abspath
  aliases["abspath"] = dconeybe_abspath.abspath
  del dconeybe_abspath

  aliases["ls"] = ["lsd", "--hyperlink=always"]

  aliases["gii"] = ["git", "--no-pager"]

  aliases["good"] = "echo 'SUCCESS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'"

  # Show a desktop notification (a.k.a. "popup").
  # https://sw.kovidgoyal.net/kitty/kittens/notify/
  aliases["pop"] = ["kitten", "notify"]

  # Enable hyperlinks in ripgrep.
  # https://sw.kovidgoyal.net/kitty/kittens/hyperlinked_grep
  aliases["rg"] = ["rg", "--hyperlink-format=kitty"]

  # Convenience wrapper to ssh to my cloudtop instance.
  aliases["slb"] = ssh_to_lb_alias

  # Create a temporary directory and cd into it.
  aliases["mkd"] = create_and_cd_into_temp_dir


# Only register aliases in interactive mode.
if $XONSH_INTERACTIVE:
  register_my_aliases()


# Clean up global namespace
del create_and_cd_into_temp_dir
del register_my_aliases
del ssh_to_lb_alias
