import { type Document } from "./document.ts";
import { type ParsePdfError } from "./parse_pdf_error.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";

export interface ParsedRogersBill {
  type: "RogersBill";
  billDate: string;
  amountDue: string;
}

class RogersBill implements Document<ParsedRogersBill, "RogersBill"> {
  readonly type = "RogersBill" as const;

  identify(lines: readonly string[]): boolean {
    return lines.some((line) => line.toUpperCase().includes("1-888-ROGERS-1"));
  }

  calculateFileName(pdf: Readonly<ParsedRogersBill>): string {
    const { billDate, amountDue } = pdf;
    return `${billDate} Rogers Bill ${amountDue}.pdf`;
  }

  parse(lines: readonly string[]): ParsedRogersBill | ParsePdfError {
    const amountDueIndex = lines.findIndex(
      (line) => line.toLowerCase() === "what is the total due?",
    );
    if (amountDueIndex < 0) {
      return { type: "ParsePdfError", message: "amount due line not found" };
    }
    const amountDue = lines[amountDueIndex + 1]?.trim();
    if (!amountDue) {
      return {
        type: "ParsePdfError",
        message: "expected line after amount due line",
      };
    }

    const billDateIndex = lines.findIndex(
      (line) => line.toLowerCase() === "bill date",
    );
    if (billDateIndex < 0) {
      return { type: "ParsePdfError", message: "bill date line not found" };
    }
    const billDateStr = lines[billDateIndex + 1]?.trim();
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
}

export const rogersBill: Readonly<Document<ParsedRogersBill, "RogersBill">> =
  Object.freeze(new RogersBill());
