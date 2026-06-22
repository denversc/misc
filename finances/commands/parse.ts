import { isReadPdfError, readPdf } from "../pdf_read.ts";
import { isDocumentParseError } from "../document.ts";
import { identify, isIdentifyError } from "../identify.ts";

export interface ParseOptions {
  v?: boolean;
}

export async function parseCommand(
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

  const document = identify(readPdfResult);
  if (typeof document === "undefined") {
    console.error(`ERROR: unable to identify pdf contents: ${filePath}`);
    process.exit(1);
  }
  if (isIdentifyError(document)) {
    const { message } = document;
    console.error(`ERROR: ${message}: ${filePath}`);
    process.exit(1);
  }

  const parseResult = document.parse(readPdfResult);
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
