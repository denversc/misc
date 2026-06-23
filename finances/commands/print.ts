import { isReadPdfError, readPdf } from "../pdf_read.ts";

export interface PrintOptions {
  v?: boolean;
}

export async function printCommand(
  filePath: string | string[],
  options?: PrintOptions,
): Promise<void> {
  if (Array.isArray(filePath)) {
    for (const currentFilePath of filePath) {
      await printCommand(currentFilePath, options);
    }
    return;
  }

  const pdf = await readPdf(filePath);
  if (isReadPdfError(pdf)) {
    console.error(`ERROR: ${pdf.message}: ${filePath}`);
    process.exit(1);
  }

  if (options?.v) {
    console.log(filePath);
  }
  console.log(pdf);
}
