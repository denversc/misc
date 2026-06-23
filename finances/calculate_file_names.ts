import { isReadPdfError, readPdf } from "./pdf_read.ts";
import { isDocumentParseError } from "./document.ts";
import { identify, isIdentifyError } from "./identify.ts";

export interface CalculateFileNamesError {
  type: "CalculateFileNamesError";
  message: string;
  filePath: string;
}

export function isCalculateFileNamesError(
  e: unknown,
): e is CalculateFileNamesError {
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

export async function calculateFileNames(
  filePaths: string[],
): Promise<Map<string, string> | CalculateFileNamesError> {
  const infoByFileName = new Map<
    string,
    Array<{ filePath: string; pdf: string }>
  >();
  const fileNameByFilePath = new Map<string, string>();

  for (const filePath of filePaths) {
    if (fileNameByFilePath.has(filePath)) {
      continue;
    }

    const pdf = await readPdf(filePath);
    if (isReadPdfError(pdf)) {
      return {
        type: "CalculateFileNamesError",
        message: pdf.message,
        filePath,
      };
    }

    const document = identify(pdf);
    if (typeof document === "undefined") {
      return {
        type: "CalculateFileNamesError",
        message: "unable to identify pdf contents",
        filePath,
      };
    }
    if (isIdentifyError(document)) {
      return {
        type: "CalculateFileNamesError",
        message: document.message,
        filePath,
      };
    }

    const parseResult = document.parse(pdf);
    if (isDocumentParseError(parseResult)) {
      return {
        type: "CalculateFileNamesError",
        message: parseResult.message,
        filePath,
      };
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const fileName = document.calculateFileName(parseResult as unknown as any);
    fileNameByFilePath.set(filePath, fileName);

    const newFileNameInfo = { filePath, pdf };
    const info = infoByFileName.get(fileName);
    if (info) {
      info.push(newFileNameInfo);
    } else {
      infoByFileName.set(fileName, [newFileNameInfo]);
    }
  }

  for (const [fileName, infoList] of infoByFileName.entries()) {
    const pdfs = new Set<string>();
    for (const info of infoList) {
      pdfs.add(info.pdf);
    }

    if (pdfs.size < 2) {
      continue;
    }

    const numberByPdf = new Map<string, number>();
    for (const pdf of pdfs) {
      numberByPdf.set(pdf, numberByPdf.size + 1);
    }

    const fileNameByPdf = new Map<string, string>();
    for (const [pdf, fileNumber] of numberByPdf) {
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
      fileNameByPdf.set(pdf, numberedFileName);
    }

    for (const info of infoList) {
      const newFileName = fileNameByPdf.get(info.pdf);
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
