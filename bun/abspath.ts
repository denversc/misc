import { resolve } from "node:path";
import { TextDecoderStream } from "node:stream/web";
import process from "node:process";

const args = process.argv.slice(2);

async function main() {
  if (args.length > 0) {
    for (const arg of args) {
      console.log(resolve(arg));
    }
    return;
  }

  const decoderStream = new TextDecoderStream("utf-8", { fatal: true });
  const reader = Bun.stdin.stream().pipeThrough(decoderStream).getReader();

  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        if (buffer.length > 0) {
          const cleanLine = buffer.endsWith('\r') ? buffer.slice(0, -1) : buffer;
          console.log(resolve(cleanLine));
        }
        break;
      }

      buffer += value;
      
      let newlineIndex;
      while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, newlineIndex);
        buffer = buffer.slice(newlineIndex + 1);
        const cleanLine = line.endsWith('\r') ? line.slice(0, -1) : line;
        console.log(resolve(cleanLine));
      }
    }
  } catch (e) {
    // If TextDecoderStream is initialized with { fatal: true }, 
    // it throws a TypeError on invalid sequences.
    if (e instanceof TypeError) {
      console.error("UTF-8 decoding error");
    } else {
      console.error("Error reading stdin:", e);
    }
    process.exit(1);
  }
}

main();
