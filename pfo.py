import argparse
from collections.abc import Sequence
import dataclasses
import pathlib
import signal
import subprocess
import sys
import time
import typing

def main(args: Sequence[str]) -> None:
  parsed_args = parse_args(prog=args[0], args=args[1:])

  process = subprocess.Popen(
      parsed_args.subprocess_args,
      bufsize=0, # unbuffered
      pipesize=256,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,      
  )

  def signal_handler(sig, stack):
    process.send_signal(sig)

  signal.signal(signal.SIGABRT, signal_handler)
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)

  if parsed_args.alt_output_file is not None:
    alt_dest = parsed_args.alt_output_file.open("wb")
  else:
    alt_dest = None

  try:
    prefixer = TimestampPrefixer(
        start_time = TimestampPrefixer.monotonic_time(),
        dest = sys.stdout.buffer,
        alt_dest = alt_dest,
    )

    while True:
      chunk = process.stdout.read(8192)
      if not chunk:
        break
      prefixer.process_chunk(chunk)
  finally:
    if alt_dest is not None:
      alt_dest.close()

  sys.exit(process.wait())

@dataclasses.dataclass(frozen=True)
class ParsedArgs:
  subprocess_args: Sequence[str]
  line_number_prefix_enabled: bool
  timestamp_prefix_enabled: bool
  alt_output_file: pathlib.Path | None

def parse_args(prog: str, args: Sequence[str]) -> ParsedArgs:
  args = tuple(args) # Make an immutable copy of args

  arg_parser = argparse.ArgumentParser(
      prog=prog,
      usage="%(prog)s [options] <subcommand> [subcommand_args]",
  )
  
  prefix_timestamp_arg = arg_parser.add_argument(
      "-t", "--prefix-timestamp",
      action="store_true",
      default=True,
      dest="prefix_timestamp",
      help="Prefix each line with a timestamp (default: %(default)s)",
  )
  arg_parser.add_argument(
      "-T", "--no-prefix-timestamp",
      action="store_false",
      dest=prefix_timestamp_arg.dest,
      help="Do NOT prefix each line with a timestamp (this is the opposite of " +
        "/".join(prefix_timestamp_arg.option_strings) +
        ")"
  )
  prefix_line_number_arg = arg_parser.add_argument(
      "-n", "--prefix-line-number",
      action="store_true",
      default=True,
      dest="prefix_line_number",
      help="Prefix each line with a line number (default: %(default)s)",
  )
  arg_parser.add_argument(
      "-N", "--no-prefix-line-number",
      action="store_false",
      dest=prefix_line_number_arg.dest,
      help="Do NOT prefix each line with a line number (this is the opposite of " +
        "/".join(prefix_line_number_arg.option_strings) +
        ")"
  )
  arg_parser.add_argument(
      "-d", "--dest-file",
      dest="dest_file",
      default=None,
      help="A file to which output is written, in addition to being written to stdout",
  )

  (namespace, subprocess_args) = arg_parser.parse_known_args(args)

  if len(subprocess_args) == 0:
    arg_parser.error("No subprocess arguments were specified")
  elif subprocess_args[0].startswith("-"):
    arg_parser.error(f"Unrecognized command-line option: {subprocess_args[0]}")

  return ParsedArgs(
    subprocess_args=tuple(subprocess_args),
    line_number_prefix_enabled=namespace.prefix_line_number,
    timestamp_prefix_enabled=namespace.prefix_timestamp,
    alt_output_file=None if namespace.dest_file is None else pathlib.Path(namespace.dest_file),
  )

class TimestampPrefixer:

  def __init__(self, start_time: float, dest: typing.BinaryIO, alt_dest: typing.BinaryIO | None) -> None:
    self.start_time = start_time
    self.dest = dest
    self.alt_dest = alt_dest
    self._next_chunk_starts_new_line = True
    self._last_formatted_time: str | None = None
    self._last_formatted_time_values: tuple[int, int, int] | None = None

  @staticmethod
  def monotonic_time() -> float:
    return time.monotonic()

  def process_chunk(self, chunk: bytes) -> None:
    if len(chunk) == 0:
      raise ValueError("len(chunk)==0, but expected len(chunk) to be strictly greater than zero")

    if self._next_chunk_starts_new_line:
      self._print_current_time()
      self._next_chunk_starts_new_line = False

    end_index = chunk.find(b"\n")
    if end_index < 0:
      self._write(chunk)
      self.dest.flush()
      return

    self._write(chunk[:end_index + 1])
    self._next_chunk_starts_new_line = False

    start_index = end_index + 1
    while start_index < len(chunk):
      end_index = chunk.find(b"\n", start_index)
      self._print_current_time()
      if end_index < 0:
        self._write(chunk[start_index:])
        break
      self._write(chunk[start_index:end_index + 1])
      start_index = end_index + 1
    else:
      self._next_chunk_starts_new_line = True

    self.dest.flush()

  def _print_current_time(self) -> None:
    current_time = self.monotonic_time()
    elapsed_time = current_time - self.start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time) - (minutes * 60)
    millis = int((elapsed_time - (minutes * 60) - seconds) * 1000)

    cache_key = (minutes, seconds, millis)
    if self._last_formatted_time_values == cache_key:
      timestamp = self._last_formatted_time
    else:
      timestamp = f"{minutes:02d}:{seconds:02d}.{millis:03d} "
      self._last_formatted_time_values = cache_key
      self._last_formatted_time = timestamp

    self._write(timestamp.encode("utf8", errors="strict"))

  def _write(self, chunk: bytes) -> None:
    self.dest.write(chunk)
    alt_dest = self.alt_dest
    if alt_dest is not None:
      alt_dest.write(chunk)

if __name__ == "__main__":
  main(sys.argv)
