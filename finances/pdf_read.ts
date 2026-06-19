import * as fs from "node:fs/promises";
import { PDFParse } from "pdf-parse";

import { messageForError } from "./error.ts";

export interface ReadPdfError {
  type: "ReadPdfError";
  message: string;
}

export function isReadPdfError(e: unknown): e is ReadPdfError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "ReadPdfError" &&
    "message" in e &&
    typeof e.message === "string"
  );
}

export interface ReadPdfResult {
  text: string;
  lines: string[];
  hash: string;
}

export async function readPdf(
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
