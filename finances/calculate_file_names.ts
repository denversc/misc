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

    const document = identify(readPdfResult.lines);
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

    const parseResult = document.parse(readPdfResult.lines);
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
