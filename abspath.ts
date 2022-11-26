import {
  isAbsolute,
  normalize,
  SEP,
} from "https://deno.land/std@0.166.0/path/mod.ts";

function toAbsolutePath(path: string): string {
  if (isAbsolute(path)) {
    return path;
  }
  return Deno.cwd() + SEP + path;
}

export function toAbsolutePaths<T>(
  paths: Array<string>,
  onPathConverted: (convertedPath: string) => T,
): void {
  for (const path of paths) {
    onPathConverted(normalize(toAbsolutePath(path)));
  }
}

toAbsolutePaths(Deno.args, console.log);
