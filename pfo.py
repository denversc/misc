from collections.abc import Sequence
import subprocess
import sys
import time
import typing

def main(args: Sequence[str]) -> None:
  if len(args) < 2:
    print("ERROR: must specify a command to run", file=sys.stderr)
    sys.exit(2)

  process = subprocess.Popen(
      args[1:],
      bufsize=0, # unbuffered
      pipesize=256,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,      
  )

  prefixer = TimestampPrefixer(
      start_time = TimestampPrefixer.monotonic_time(),
      dest = sys.stdout.buffer,
  )

  while True:
    chunk = process.stdout.read(8192)
    if not chunk:
      break
    prefixer.process_chunk(chunk)

  sys.exit(process.wait())

class TimestampPrefixer:

  def __init__(self, start_time: float, dest: typing.BinaryIO) -> None:
    self.start_time = start_time
    self.dest = dest
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
      self.dest.write(chunk)
      return

    self.dest.write(chunk[:end_index + 1])
    self._next_chunk_starts_new_line = False

    start_index = end_index + 1
    while start_index < len(chunk):
      end_index = chunk.find(b"\n", start_index)
      self._print_current_time()
      if end_index < 0:
        self.dest.write(chunk[start_index:])
        break
      self.dest.write(chunk[start_index:end_index + 1])
      start_index = end_index + 1
    else:
      self._next_chunk_starts_new_line = True

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

    self.dest.write(timestamp.encode("utf8", errors="strict"))

if __name__ == "__main__":
  main(sys.argv)
