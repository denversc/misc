import * as fs from "node:fs/promises";
import { Command } from "commander";
import * as path from "node:path";

import { isReadPdfError, readPdf } from "./pdf_read.ts";
import { isDocumentParseError } from "./document.ts";
import { identify, isIdentifyError } from "./identify.ts";
import {
  calculateFileNames,
  isCalculateFileNamesError,
} from "./calculate_file_names.ts";

const program = new Command();

interface PrintOptions {
  v?: boolean;
}

async function printCommand(
  filePath: string | string[],
  options?: PrintOptions,
): Promise<void> {
  if (Array.isArray(filePath)) {
    for (const currentFilePath of filePath) {
      await printCommand(currentFilePath, options);
    }
    return;
  }

  const readPdfResult = await readPdf(filePath);
  if (isReadPdfError(readPdfResult)) {
    console.error(`ERROR: ${readPdfResult.message}: ${filePath}`);
    process.exit(1);
  }

  if (options?.v) {
    console.log(filePath);
  }
  console.log(readPdfResult.text);
}

interface ParseOptions {
  v?: boolean;
}

async function parseCommand(
  filePath: string | string[],
  options?: ParseOptions,
): Promise<void> {
  if (Array.isArray(filePath)) {
    for (const currentFilePath of filePath) {
      await parseCommand(currentFilePath, options);
    }
    return;
  }

  const readPdfResult = await readPdf(filePath);
  if (isReadPdfError(readPdfResult)) {
    console.error(`ERROR: ${readPdfResult.message}: ${filePath}`);
    process.exit(1);
  }

  const document = identify(readPdfResult.lines);
  if (typeof document === "undefined") {
    console.error(`ERROR: unable to identify pdf contents: ${filePath}`);
    process.exit(1);
  }
  if (isIdentifyError(document)) {
    const { message } = document;
    console.error(`ERROR: ${message}: ${filePath}`);
    process.exit(1);
  }

  const parseResult = document.parse(readPdfResult.lines);
  if (isDocumentParseError(parseResult)) {
    const { message } = parseResult;
    console.error(`ERROR: ${message}: ${filePath}`);
    process.exit(1);
  }

  if (options?.v) {
    console.log(filePath);
  }
  console.log(parseResult);
}

interface IdentifyOptions {
  v?: boolean;
}

async function identifyCommand(
  filePath: string | string[],
  options?: IdentifyOptions,
): Promise<void> {
  if (Array.isArray(filePath)) {
    for (const currentFilePath of filePath) {
      await identifyCommand(currentFilePath, options);
    }
    return;
  }

  const readPdfResult = await readPdf(filePath);
  if (isReadPdfError(readPdfResult)) {
    console.error(`ERROR: ${readPdfResult.message}: ${filePath}`);
    process.exit(1);
  }

  const document = identify(readPdfResult.lines);
  if (isIdentifyError(document)) {
    const { message } = document;
    console.error(`ERROR: ${message}: ${filePath}`);
    process.exit(1);
  }

  const type: string = document?.type ?? "<unknown>";

  if (options?.v) {
    console.log(`${filePath}: ${type}`);
  } else {
    console.log(type);
  }
}

interface FilenameOptions {
  v?: boolean;
}

async function filenameCommand(
  filePaths: string | string[],
  options?: FilenameOptions,
): Promise<void> {
  if (typeof filePaths === "string") {
    return filenameCommand([filePaths]);
  }

  const outputFileNameByFilePath = await calculateFileNames(filePaths);
  if (isCalculateFileNamesError(outputFileNameByFilePath)) {
    const { message, filePath } = outputFileNameByFilePath;
    console.error(`ERROR: ${message}: ${filePath}`);
    process.exit(1);
  }

  for (const filePath of filePaths) {
    const outputFileName = outputFileNameByFilePath.get(filePath);
    if (!outputFileName) {
      throw new Error(
        `internal error patvap56xt: ` +
          `outputFileNameByFilePath.get(${Bun.inspect(filePath)}) ` +
          `returned ${Bun.inspect(outputFileName)}`,
      );
    }

    if (options?.v) {
      console.log(`${filePath}: ${outputFileName}`);
    } else {
      console.log(outputFileName);
    }
  }
}

interface RenameOptions {
  v?: boolean;
}

async function renameCommand(
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

program
  .name("stmt")
  .description(
    "Reads PDF file and extracts information " +
      "relevant for financial record keeping",
  )
  .version("1.0.0");

program
  .command("print")
  .description("Reads PDF files and prints their text to stdout")
  .argument("<files...>", "paths of the PDF files")
  .option("-v", "print the file path on its own line before its contents")
  .action(printCommand);

program
  .command("identify")
  .description("Reads PDF files and prints their types to stdout")
  .argument("<files...>", "paths of the PDF files")
  .option("-v", "prefix each line with the file path")
  .action(identifyCommand);

program
  .command("parse")
  .description(
    "Reads PDF files, parses their content, and prints them to stdout",
  )
  .argument("<files...>", "paths of the PDF files")
  .option("-v", "print the file path on its own line before its contents")
  .action(parseCommand);

program
  .command("filename")
  .description(
    "Reads PDF files and prints their normalized file names to stdout",
  )
  .argument("<files...>", "paths of the PDF files")
  .option("-v", "prefix each line with the file path")
  .action(filenameCommand);

program
  .command("rename")
  .description("Renames PDF files to their normalized file names")
  .argument("<files...>", "paths of the PDF files")
  .option("-v", "prefix each output path with the source path")
  .action(renameCommand);

program.parse(process.argv);
