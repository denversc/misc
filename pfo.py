from collections.abc import Sequence
import subprocess
import sys
import time

def main(args: Sequence[str]) -> None:
  if len(args) < 2:
    print("ERROR: must specify a command to run", file=sys.stderr)
    sys.exit(2)

  start_time = time.monotonic()

  process = subprocess.Popen(
      args[1:],
      bufsize=0, # unbuffered
      pipesize=256,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,      
  )

  first_line = True
  while True:
    chunk = process.stdout.read(32)
    if not chunk:
      break

    chunk_start_index = 0
    while chunk_start_index < len(chunk):
      orig_chunk_start_index = chunk_start_index
      index = chunk.find(b"\n", chunk_start_index)
      if index < 0:
        line = chunk[chunk_start_index:]
        chunk_start_index = len(chunk)
      else:
        line = chunk[chunk_start_index:index+1]
        chunk_start_index = index + 1

      if first_line or orig_chunk_start_index > 0:
        first_line = False
        cur_time = time.monotonic()
        elapsed_time = cur_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time) - (minutes * 60)
        timestamp = f"{minutes:02d}:{seconds:02d} "
        sys.stdout.buffer.write(timestamp.encode("utf8"))

      sys.stdout.buffer.write(line)
      sys.stdout.buffer.flush()

  sys.exit(process.wait())

if __name__ == "__main__":
  main(sys.argv)
