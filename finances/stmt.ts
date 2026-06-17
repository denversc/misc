import * as fs from "node:fs/promises";
import { Command } from "commander";
import { PDFParse } from "pdf-parse";
import { parse, format } from "@formkit/tempo";
import * as path from "node:path";

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
  hash: string;
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
  const hash = Bun.CryptoHasher.hash("sha512-256", fileContents, "hex");
  return { text, lines, hash };
}

type PdfType =
  | "PublicMobileStatement"
  | "QuestradeRESPStatement"
  | "QuestradeRRSPStatement"
  | "QuestradeMarginStatement";

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
  const invoiceDateStr = pdfLines[invoiceIndex + 1];
  if (!invoiceDateStr) {
    return {
      type: "ParsePdfError",
      message: "expected line after INVOICE line",
    };
  }
  let parsedInvoiceDate: Date;
  try {
    parsedInvoiceDate = parse(invoiceDateStr, "MMM D, YYYY", "en");
  } catch (e: unknown) {
    return {
      type: "ParsePdfError",
      message: `unable to parse invoice date "${invoiceDateStr}": ${messageForError(e)}`,
    };
  }

  if (isNaN(parsedInvoiceDate.getTime())) {
    return {
      type: "ParsePdfError",
      message: `invalid invoice date: ${invoiceDateStr}`,
    };
  }

  const invoiceDate = format(parsedInvoiceDate, "YYYY-MM-DD");

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

interface ParsedQuestradeStatement {
  type: QuestradeStatementType;
  statementDate: Date;
  accountNumber: string;
  balance: string;
}

function parseQuestradeStatement(
  pdfLines: readonly string[],
): ParsedQuestradeStatement | ParsePdfError {
  const type = identifyQuestradeStatementType(pdfLines);
  if (!type) {
    return {
      type: "ParsePdfError",
      message: "Unable to determine Questrade statement type",
    };
  }

  const accountNumberRegex = /Account\s*#:\s*(\d+)/i;
  const accountNumberLine = pdfLines.find((line) =>
    line.match(accountNumberRegex),
  );
  if (!accountNumberLine) {
    return { type: "ParsePdfError", message: "Account number line not found" };
  }
  const accountNumber = accountNumberLine.match(accountNumberRegex)?.[1];
  if (!accountNumber) {
    throw new Error(
      "internal error rhtan4myg2: " + "accountNumber should have matched",
    );
  }

  const statementDate = new Date();
  const balance = "$0.00";

  return { type, statementDate, accountNumber, balance };
}

type ParsedPdf = ParsedPublicMobileStatement | ParsedQuestradeStatement;

function parsePdf(pdfLines: string[]): ParsedPdf | ParsePdfError {
  const type = identify(pdfLines);
  if (!type) {
    return { type: "ParsePdfError", message: "unrecognized pdf content" };
  } else if (type === "PublicMobileStatement") {
    return parsePublicMobileStatement(pdfLines);
  } else if (isQuestradeStatementType(type)) {
    return parseQuestradeStatement(pdfLines);
  } else {
    unreachable(type, "unknown type");
  }
}

function calculateFileName(parsedPdf: ParsedPdf): string {
  if (parsedPdf.type === "PublicMobileStatement") {
    const { invoiceDate, totalAmountPaid } = parsedPdf;
    const formattedDate = format(invoiceDate, "YYYY-MM-DD");
    return `${formattedDate} Public Mobile Payment ${totalAmountPaid}.pdf`;
  } else if (isQuestradeStatementType(parsedPdf.type)) {
    throw new Error("not implemented h6rjr85kc6");
  } else {
    unreachable(parsedPdf.type, "unknown type");
  }
}

interface CalculateFileNamesError {
  type: "CalculateFileNamesError";
  message: string;
  filePath: string;
}

function isCalculateFileNamesError(e: unknown): e is CalculateFileNamesError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "CalculateFileNamesError" &&
    "message" in e &&
    typeof e.message === "string" &&
    "filePath" in e &&
    typeof e.filePath === "string"
  );
}

async function calculateFileNames(
  filePaths: string[],
): Promise<Map<string, string> | CalculateFileNamesError> {
  const infoByFileName = new Map<
    string,
    Array<{ filePath: string; hash: string }>
  >();
  const fileNameByFilePath = new Map<string, string>();

  for (const filePath of filePaths) {
    if (fileNameByFilePath.has(filePath)) {
      continue;
    }

    const readPdfResult = await readPdf(filePath);
    if (isReadPdfError(readPdfResult)) {
      return {
        type: "CalculateFileNamesError",
        message: readPdfResult.message,
        filePath,
      };
    }

    const parsedPdf = parsePdf(readPdfResult.lines);
    if (isParsePdfError(parsedPdf)) {
      return {
        type: "CalculateFileNamesError",
        message: `unable to parse pdf contents: ${parsedPdf.message}`,
        filePath,
      };
    }

    const fileName = calculateFileName(parsedPdf);
    fileNameByFilePath.set(filePath, fileName);

    const newFileNameInfo = { filePath, hash: readPdfResult.hash };
    const info = infoByFileName.get(fileName);
    if (info) {
      info.push(newFileNameInfo);
    } else {
      infoByFileName.set(fileName, [newFileNameInfo]);
    }
  }

  for (const [fileName, infoList] of infoByFileName.entries()) {
    const hashes = new Set<string>();
    for (const info of infoList) {
      hashes.add(info.hash);
    }

    if (hashes.size < 2) {
      continue;
    }

    const numberByHash = new Map<string, number>();
    for (const hash of hashes) {
      numberByHash.set(hash, numberByHash.size + 1);
    }

    const fileNameByHash = new Map<string, string>();
    for (const [hash, fileNumber] of numberByHash) {
      const lastPeriodIndex = fileName.lastIndexOf(".");
      let numberedFileName: string;
      if (lastPeriodIndex < 0) {
        numberedFileName = `${fileName} ${fileNumber}`;
      } else {
        numberedFileName =
          fileName.substring(0, lastPeriodIndex) +
          ` ${fileNumber}` +
          fileName.substring(lastPeriodIndex);
      }
      fileNameByHash.set(hash, numberedFileName);
    }

    for (const info of infoList) {
      const newFileName = fileNameByHash.get(info.hash);
      if (!newFileName) {
        throw new Error(
          `internal error kwteqzzx79: ` +
            `fileNameByHash.get(info.hash) ` +
            `returned ${Bun.inspect(newFileName)}`,
        );
      }

      fileNameByFilePath.set(info.filePath, newFileName);
    }
  }

  return fileNameByFilePath;
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

function identify(pdfLines: readonly string[]): PdfType | undefined {
  if (pdfLines.includes("Public Mobile Account")) {
    return "PublicMobileStatement";
  }

  if (
    pdfLines.some((line) =>
      line.toLowerCase().startsWith("questrade wealth management inc."),
    )
  ) {
    const questradeStatementType = identifyQuestradeStatementType(pdfLines);
    if (questradeStatementType) {
      return questradeStatementType;
    }
  }

  return undefined;
}

type QuestradeStatementType =
  | "QuestradeRESPStatement"
  | "QuestradeRRSPStatement"
  | "QuestradeMarginStatement";

function isQuestradeStatementType(
  value: unknown,
): value is QuestradeStatementType {
  return (
    value === "QuestradeRESPStatement" ||
    value === "QuestradeRRSPStatement" ||
    value === "QuestradeMarginStatement"
  );
}

function identifyQuestradeStatementType(
  pdfLines: readonly string[],
): QuestradeStatementType | undefined {
  if (pdfLines.some((line) => line.includes("(RESP)"))) {
    return "QuestradeRESPStatement";
  }

  if (
    pdfLines.some((line) =>
      line.toLowerCase().includes("registered retirement savings plan"),
    )
  ) {
    return "QuestradeRRSPStatement";
  }

  if (
    pdfLines.some((line) =>
      line.toLowerCase().includes("individual margin account"),
    )
  ) {
    return "QuestradeMarginStatement";
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
