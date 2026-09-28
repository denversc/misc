"""Aggregates nested .gitignore files into a unified pattern list.

This tool recursively searches a directory tree to discover all .gitignore
files and combines their rules into a single output stream on standard output.

Patterns originating from subdirectories are prefixed with their relative path
so that the aggregated rules match files identically when evaluated from the root
directory.

To install the YAML dependency, run:
  pip install ruamel.yaml
"""

import argparse
import enum
import pathlib
import ruamel.yaml
import ruamel.yaml.comments
import ruamel.yaml.scalarstring


class YamlUpdateStrategy(enum.StrEnum):
  """Strategy for updating the target list in the YAML file."""

  APPEND = "append"
  UNION = "union"
  REPLACE = "replace"


def find_gitignore_files(root_directory: pathlib.Path) -> list[pathlib.Path]:
  """Finds all .gitignore files recursively under root_directory, skipping .git directories.

  Returns paths ordered by directory depth (shallower first), and
  alphabetically sorted at each depth.
  """
  gitignore_paths: list[pathlib.Path] = []
  for current_root, directories, files in root_directory.walk():
    # Prune .git directory from recursion
    if ".git" in directories:
      directories.remove(".git")
    if ".gitignore" in files:
      gitignore_paths.append(current_root / ".gitignore")

  def sort_key(path: pathlib.Path) -> tuple[int, str]:
    relative_parent = path.parent.relative_to(root_directory)
    depth = len(relative_parent.parts)
    return (depth, relative_parent.as_posix())

  gitignore_paths.sort(key=sort_key)
  return gitignore_paths


def process_gitignore_file(
  file_path: pathlib.Path, root_directory: pathlib.Path
) -> list[str]:
  """Processes a single .gitignore file and returns transformed patterns."""
  relative_directory = file_path.parent.relative_to(root_directory)
  prefix = (
    ""
    if relative_directory == pathlib.Path(".")
    else f"{relative_directory.as_posix()}/"
  )

  results: list[str] = []
  with file_path.open("rt", encoding="utf-8", errors="strict") as gitignore_file:
    for raw_line in gitignore_file:
      line = raw_line.rstrip("\r\n")

      # Drop blank lines and comments
      if not line.strip() or line.startswith("#"):
        continue

      if not prefix:
        results.append(line)
        continue

      is_negated = line.startswith("!")
      pattern = line[1:] if is_negated else line

      if pattern.startswith("/"):
        pattern = pattern.removeprefix("/")
        new_pattern = f"{prefix}{pattern}"
      elif "/" in pattern.rstrip("/"):
        new_pattern = f"{prefix}{pattern}"
      else:
        new_pattern = f"{prefix}**/{pattern}"

      if is_negated:
        new_pattern = f"!{new_pattern}"
      results.append(new_pattern)

  return results


def update_yaml_file(
  yaml_file_path: pathlib.Path,
  key_path: str,
  new_patterns: list[str],
  strategy: YamlUpdateStrategy,
) -> None:
  """Updates or creates a YAML file, appending, merging, or replacing a list at key_path."""
  yaml = ruamel.yaml.YAML()
  yaml.preserve_quotes = True
  yaml.indent(mapping=2, sequence=4, offset=2)

  if yaml_file_path.exists():
    with yaml_file_path.open("r", encoding="utf-8") as f:
      data = yaml.load(f)
    if data is None:
      data = ruamel.yaml.comments.CommentedMap()
  else:
    data = ruamel.yaml.comments.CommentedMap()

  keys = key_path.split(".")
  current_mapping = data
  for key in keys[:-1]:
    if key not in current_mapping or not isinstance(
      current_mapping[key], (dict, ruamel.yaml.comments.CommentedMap)
    ):
      current_mapping[key] = ruamel.yaml.comments.CommentedMap()
    current_mapping = current_mapping[key]

  target_key = keys[-1]
  target_value = current_mapping.get(target_key)
  quoted_patterns = [
    ruamel.yaml.scalarstring.DoubleQuotedScalarString(pattern)
    for pattern in new_patterns
  ]

  if strategy == YamlUpdateStrategy.REPLACE:
    current_mapping[target_key] = quoted_patterns
  else:
    if target_value is None:
      current_mapping[target_key] = quoted_patterns
    elif isinstance(target_value, list):
      if strategy == YamlUpdateStrategy.APPEND:
        target_value.extend(quoted_patterns)
      elif strategy == YamlUpdateStrategy.UNION:
        existing_items = set(target_value)
        for pattern in quoted_patterns:
          if pattern not in existing_items:
            target_value.append(pattern)
            existing_items.add(pattern)
    else:
      raise ValueError(
        f"Target YAML path '{key_path}' in {yaml_file_path} is of type"
        f" {type(target_value).__name__}, not a list, and strategy is"
        f" '{strategy.value}'."
      )

  yaml_file_path.parent.mkdir(parents=True, exist_ok=True)
  with yaml_file_path.open("w", encoding="utf-8") as f:
    yaml.dump(data, f)


def main() -> None:
  parser = argparse.ArgumentParser(
    description=(
      "Recursively aggregates all .gitignore files into a unified pattern"
      " list."
    )
  )
  parser.add_argument(
    "root_directory",
    nargs="?",
    default=None,
    help="Root directory to search (defaults to current working directory)",
  )
  parser.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Suppress printing the aggregated .gitignore patterns to stdout.",
  )
  parser.add_argument(
    "--yaml-file",
    type=pathlib.Path,
    default=None,
    help="Path to a .yml or .yaml file to create or update.",
  )
  parser.add_argument(
    "--yaml-path",
    type=str,
    default=None,
    help=(
      "Dot-separated path to the list in the YAML file (e.g."
      " sync.code.ignore.paths). Required if --yaml-file is specified."
    ),
  )
  parser.add_argument(
    "--yaml-update-strategy",
    type=YamlUpdateStrategy,
    choices=list(YamlUpdateStrategy),
    default=None,
    help=(
      "Strategy for updating the target list in the YAML file (default:"
      " append)."
    ),
  )

  args = parser.parse_args()

  if not args.yaml_file:
    if args.yaml_path:
      parser.error("--yaml-path requires --yaml-file.")
    if args.yaml_update_strategy is not None:
      parser.error("--yaml-update-strategy requires --yaml-file.")
  elif not args.yaml_path:
    parser.error("--yaml-path is required when --yaml-file is specified.")

  yaml_update_strategy = args.yaml_update_strategy or YamlUpdateStrategy.APPEND

  root_directory = (
    pathlib.Path(args.root_directory)
    if args.root_directory
    else pathlib.Path.cwd()
  )
  root_directory = root_directory.resolve()
  if not root_directory.exists():
    parser.error(f"Directory does not exist: {args.root_directory or root_directory}")
  elif not root_directory.is_dir():
    parser.error(f"Not a directory: {args.root_directory or root_directory}")

  gitignore_files = find_gitignore_files(root_directory)
  all_patterns: list[str] = []
  for file_path in gitignore_files:
    patterns = process_gitignore_file(file_path, root_directory)
    if patterns and not args.quiet:
      print(f"# {file_path.relative_to(root_directory)}")
      for pattern in patterns:
        print(pattern)
    all_patterns.extend(patterns)

  if args.yaml_file:
    update_yaml_file(
      yaml_file_path=args.yaml_file,
      key_path=args.yaml_path,
      new_patterns=all_patterns,
      strategy=yaml_update_strategy,
    )


if __name__ == "__main__":
  main()
