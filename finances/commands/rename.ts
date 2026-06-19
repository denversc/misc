import * as fs from "node:fs/promises";
import * as path from "node:path";

import {
  calculateFileNames,
  isCalculateFileNamesError,
} from "../calculate_file_names.ts";

export interface RenameOptions {
  v?: boolean;
}

export async function renameCommand(
  filePaths: string | string[],
  options?: RenameOptions,
): Promise<void> {
  if (typeof filePaths === "string") {
    return renameCommand([filePaths]);
  }

  const outputFileNameByFilePath = await calculateFileNames(filePaths);
  if (isCalculateFileNamesError(outputFileNameByFilePath)) {
    const { message, filePath } = outputFileNameByFilePath;
    console.error(`ERROR: ${message}: ${filePath}`);
    process.exit(1);
  }

  const renamedPaths = new Set<string>();
  let skippedCount = 0;

  for (const srcFilePath of filePaths) {
    const destFileName = outputFileNameByFilePath.get(srcFilePath);
    if (!destFileName) {
      throw new Error(
        `internal error xwttprzh98: ` +
          `outputFileNameByFilePath.get(${Bun.inspect(srcFilePath)}) ` +
          `returned ${Bun.inspect(destFileName)}`,
      );
    }

    if (renamedPaths.has(srcFilePath)) {
      console.log(
        `Skipping renaming ${srcFilePath} to ${destFileName} (already processed)`,
      );
      skippedCount++;
      continue;
    }

    const srcFileName = path.basename(srcFilePath);
    if (srcFileName === destFileName) {
      console.log(
        `Skipping renaming ${srcFilePath} (already has the correct file name)`,
      );
      skippedCount++;
      continue;
    }

    const dir = path.dirname(srcFilePath);
    const destFilePath = path.join(dir, destFileName);

    if (options?.v) {
      console.log(`Renaming ${srcFilePath} to ${destFileName}`);
    } else {
      console.log(destFilePath);
    }

    await fs.rename(srcFilePath, destFilePath);
    renamedPaths.add(srcFilePath);
  }

  console.log(`${renamedPaths.size} files renamed (${skippedCount} skipped)`);
}
