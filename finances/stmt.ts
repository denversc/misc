import * as fs from "node:fs/promises";
import { Command } from "commander";
import { PDFParse } from "pdf-parse";

const program = new Command();

function propertyFromUnknown(obj: unknown, propertyName: string): unknown {
  return typeof obj === "object" && obj !== null && propertyName in obj
    ? (obj as Record<string, unknown>)[propertyName]
    : undefined;
}

function messageForError(e: unknown): string {
  const code = propertyFromUnknown(e, "code");
  const message = propertyFromUnknown(e, "message");
  if (code === "ENOENT") {
    return "file not found";
  } else if (code === "EACCES") {
    return "insufficient permissions to read file";
  } else if (typeof message === "string" && message.trim().length > 0) {
    return message.trim();
  } else {
    return `unknown error (${Bun.inspect(e)})`;
  }
}

interface ReadPdfError {
  type: "ReadPdfError";
  message: string;
}

function isReadPdfError(e: unknown): e is ReadPdfError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "ReadPdfError" &&
    "message" in e &&
    typeof e.message === "string"
  );
}

async function readPdf(filePath: string): Promise<string | ReadPdfError> {
  let fileContents: Buffer<ArrayBuffer>;
  try {
    fileContents = await fs.readFile(filePath);
  } catch (e: unknown) {
    return { type: "ReadPdfError", message: messageForError(e) };
  }

  const parser = new PDFParse({ data: fileContents });

  try {
    const textContents = await parser.getText();
    return textContents.text;
  } catch (e: unknown) {
    const errorMessage = messageForError(e);
    const message = `parsing pdf file contents failed (${errorMessage})`;
    return { type: "ReadPdfError", message };
  } finally {
    await parser.destroy();
  }
}

async function printCommand(filePath: string | string[]): Promise<void> {
  if (Array.isArray(filePath)) {
    for (const currentFilePath of filePath) {
      await printCommand(currentFilePath);
    }
    return;
  }

  const text = await readPdf(filePath);
  if (isReadPdfError(text)) {
    console.error(`ERROR: ${text.message}: ${filePath}`);
    process.exit(1);
  }

  console.log(text);
}

type PdfType = "PublicMobileStatement";

function identify(pdfText: string): PdfType | undefined {
  const lines = pdfText.split("\n").map((line) => line.trim());
  if (lines.includes("Public Mobile Account")) {
    return "PublicMobileStatement";
  }
  return undefined;
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

  const text = await readPdf(filePath);
  if (isReadPdfError(text)) {
    console.error(`ERROR: ${text.message}: ${filePath}`);
    process.exit(1);
  }

  const type = identify(text);
  if (options?.v) {
    console.log(`${filePath}: ${type}`);
  } else {
    console.log(type);
  }
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
  .argument("<file...>", "path of the PDF file")
  .action(printCommand);

program
  .command("identify")
  .description("Reads PDF files and prints their types to stdout")
  .argument("<files...>", "path of the PDF file")
  .option("-v", "prefix each line with the file path")
  .action(identifyCommand);

program.parse(process.argv);
