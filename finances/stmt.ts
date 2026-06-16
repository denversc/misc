import * as fs from "node:fs/promises";
import { Command } from "commander";
import { PDFParse } from "pdf-parse";

const program = new Command();

function unreachable(value: never, message: string): never {
  throw new Error(`should never get here: ${message} (${Bun.inspect(value)})`);
}

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

interface ReadPdfResult {
  text: string;
  lines: string[];
}

async function readPdf(
  filePath: string,
): Promise<ReadPdfResult | ReadPdfError> {
  let fileContents: Buffer<ArrayBuffer>;
  try {
    fileContents = await fs.readFile(filePath);
  } catch (e: unknown) {
    return { type: "ReadPdfError", message: messageForError(e) };
  }

  const parser = new PDFParse({ data: fileContents });

  let text: string;
  try {
    const textContents = await parser.getText();
    text = textContents.text;
  } catch (e: unknown) {
    const errorMessage = messageForError(e);
    const message = `parsing pdf file contents failed (${errorMessage})`;
    return { type: "ReadPdfError", message };
  } finally {
    await parser.destroy();
  }

  const lines = text.split("\n").map((line) => line.trim());
  return { text, lines };
}

type PdfType = "PublicMobileStatement";

interface ParsePdfError {
  type: "ParsePdfError";
  message: string;
}

function isParsePdfError(e: unknown): e is ParsePdfError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "ParsePdfError" &&
    "message" in e &&
    typeof e.message === "string"
  );
}

interface ParsedPublicMobileStatement {
  type: "PublicMobileStatement";
  invoiceDate: string;
  totalAmountPaid: string;
}

function parsePublicMobileStatement(
  pdfLines: string[],
): ParsedPublicMobileStatement | ParsePdfError {
  const invoiceIndex = pdfLines.findIndex(
    (line) => line.toLowerCase() === "invoice",
  );
  if (invoiceIndex < 0) {
    return { type: "ParsePdfError", message: "INVOICE line not found" };
  }
  const invoiceDate = pdfLines[invoiceIndex + 1];
  if (!invoiceDate) {
    return {
      type: "ParsePdfError",
      message: "expected line after INVOICE line",
    };
  }

  const totalAmountPaidLine = pdfLines.find((line) =>
    line.toLowerCase().startsWith("total amount paid"),
  );
  if (!totalAmountPaidLine) {
    return {
      type: "ParsePdfError",
      message: "Total Amount Paid line not found",
    };
  }

  const totalAmountPaid = totalAmountPaidLine.substring(17).trim();

  return { type: "PublicMobileStatement", invoiceDate, totalAmountPaid };
}

type ParsedPdf = ParsedPublicMobileStatement;

function parsePdf(pdfLines: string[]): ParsedPdf | ParsePdfError {
  const type = identify(pdfLines);
  if (!type) {
    return { type: "ParsePdfError", message: "unrecognized pdf content" };
  } else if (type === "PublicMobileStatement") {
    return parsePublicMobileStatement(pdfLines);
  } else {
    unreachable(type, "unknown type");
  }
}

function calculateOutputFileName(parsedPdf: ParsedPdf): string {
  if (parsedPdf.type === "PublicMobileStatement") {
    const { invoiceDate, totalAmountPaid } = parsedPdf;
    return `${invoiceDate} Public Mobile Payment ${totalAmountPaid}.pdf`;
  } else {
    unreachable(parsedPdf.type, "unknown type");
  }
}

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

  const text = await readPdf(filePath);
  if (isReadPdfError(text)) {
    console.error(`ERROR: ${text.message}: ${filePath}`);
    process.exit(1);
  }

  const parsedPdf = parsePdf(text.lines);
  if (isParsePdfError(parsedPdf)) {
    console.error(
      `ERROR: unable to parse pdf contents: ` +
        `${parsedPdf.message}: ${filePath}`,
    );
    process.exit(1);
  }

  if (options?.v) {
    console.log(filePath);
  }
  console.log(parsedPdf);
}

function identify(pdfLines: string[]): PdfType | undefined {
  if (pdfLines.includes("Public Mobile Account")) {
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

  const readPdfResult = await readPdf(filePath);
  if (isReadPdfError(readPdfResult)) {
    console.error(`ERROR: ${readPdfResult.message}: ${filePath}`);
    process.exit(1);
  }

  const type = identify(readPdfResult.lines);
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

  const outputFileNameByFilePath = new Map<string, string>();

  for (const filePath of filePaths) {
    if (outputFileNameByFilePath.has(filePath)) {
      continue;
    }

    const readPdfResult = await readPdf(filePath);
    if (isReadPdfError(readPdfResult)) {
      console.error(`ERROR: ${readPdfResult.message}: ${filePath}`);
      process.exit(1);
    }

    const parsedPdf = parsePdf(readPdfResult.lines);
    if (isParsePdfError(parsedPdf)) {
      console.error(
        `ERROR: unable to parse pdf contents: ` +
          `${parsedPdf.message}: ${filePath}`,
      );
      process.exit(1);
    }

    const outputFileName = calculateOutputFileName(parsedPdf);
    outputFileNameByFilePath.set(filePath, outputFileName);
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

program.parse(process.argv);

program.parse(process.argv);
