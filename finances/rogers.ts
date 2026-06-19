import { type ParsePdfError } from "./parse_pdf_error.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";

export interface ParsedPdf {
  type: "RogersBill";
  billDate: string;
  amountDue: string;
}

export function identify(
  pdfLines: readonly string[],
): "RogersBill" | undefined {
  if (pdfLines.some((line) => line.toUpperCase().includes("1-888-ROGERS-1"))) {
    return "RogersBill";
  }
}

export function parsePdf(pdfLines: string[]): ParsedPdf | ParsePdfError {
  const amountDueIndex = pdfLines.findIndex(
    (line) => line.toLowerCase() === "what is the total due?",
  );
  if (amountDueIndex < 0) {
    return { type: "ParsePdfError", message: "amount due line not found" };
  }
  const amountDue = pdfLines[amountDueIndex + 1]?.trim();
  if (!amountDue) {
    return {
      type: "ParsePdfError",
      message: "expected line after amount due line",
    };
  }

  const billDateIndex = pdfLines.findIndex(
    (line) => line.toLowerCase() === "bill date",
  );
  if (billDateIndex < 0) {
    return { type: "ParsePdfError", message: "bill date line not found" };
  }
  const billDateStr = pdfLines[billDateIndex + 1]?.trim();
  if (!billDateStr) {
    return {
      type: "ParsePdfError",
      message: "expected line after bill date line",
    };
  }
  const billDate = parseDateToYYYYMMDD("MMM D, YYYY", billDateStr);
  if (isParseDateError(billDate)) {
    const { message } = billDate;
    return {
      type: "ParsePdfError",
      message: `unable to parse invoice date: ${billDateStr} (${message})`,
    };
  }

  return { type: "RogersBill", billDate, amountDue };
}

export function calculateFileName(parsedPdf: ParsedPdf): string {
  const { billDate, amountDue } = parsedPdf;
  return `${billDate} Rogers Bill ${amountDue}.pdf`;
}
