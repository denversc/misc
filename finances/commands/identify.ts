import { isReadPdfError, readPdf } from "../pdf_read.ts";
import { identify, isIdentifyError } from "../identify.ts";

export interface IdentifyOptions {
  v?: boolean;
}

export async function identifyCommand(
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

  const document = identify(readPdfResult);
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
