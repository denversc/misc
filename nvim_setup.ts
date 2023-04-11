// Run: deno run --allow-write --allow-read --allow-env nvim_setup.ts

import { dirname, fromFileUrl } from "https://deno.land/std@0.166.0/path/mod.ts";
import dir from "https://deno.land/x/dir/mod.ts";
import { Path } from "https://deno.land/x/path@v3.0.0/src/Path.ts";

/**
 * Calcaulates and returns the absolute path of the directory that contains
 * this file.
 */
function getDirPath(): Path {
  return new Path(dirname(fromFileUrl(import.meta.url)));
}

/**
 * Calcaulates and returns the absolute path of the init.lua script that
 * contains the commands to be executed upon neovim's launch.
 */
function getInitLuaSrcFile(): Path {
  return getDirPath().push("init.lua");
}

/**
 * Calcaulates and returns the absolute path of the init.lua script that
 * is loaded by neovim upon launch.
 */
function getInitLuaDestDir(): string {
  return new Path(dir("config")).push("nvim");
}

async function main(): void {
  const srcFile = getInitLuaSrcFile();
  if (! srcFile.exists) {
    throw new Error(`File not found: ${srcFile.toString()}`);
  }
  const destDir = getInitLuaDestDir();
  await destDir.mkDir(true);
  const destFile = destDir.push("init.lua");

  console.log(`Creating ${destFile.toString()} to call ${srcFile.toString()}`);
  const line = `dofile('${srcFile.toString()}')\n`;
  await Deno.writeTextFile(destFile.toString(), line);
}

main()
