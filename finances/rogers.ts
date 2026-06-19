import { type Document, type DocumentParseError } from "./document.ts";
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

  parse(lines: readonly string[]): ParsedRogersBill | DocumentParseError {
    const amountDueIndex = lines.findIndex(
      (line) => line.toLowerCase() === "what is the total due?",
    );
    if (amountDueIndex < 0) {
      return {
        type: "DocumentParseError",
        message: "amount due line not found",
      };
    }
    const amountDue = lines[amountDueIndex + 1]?.trim();
    if (!amountDue) {
      return {
        type: "DocumentParseError",
        message: "expected line after amount due line",
      };
    }

    const billDateIndex = lines.findIndex(
      (line) => line.toLowerCase() === "bill date",
    );
    if (billDateIndex < 0) {
      return {
        type: "DocumentParseError",
        message: "bill date line not found",
      };
    }
    const billDateStr = lines[billDateIndex + 1]?.trim();
    if (!billDateStr) {
      return {
        type: "DocumentParseError",
        message: "expected line after bill date line",
      };
    }
    const billDate = parseDateToYYYYMMDD("MMM D, YYYY", billDateStr);
    if (isParseDateError(billDate)) {
      const { message } = billDate;
      return {
        type: "DocumentParseError",
        message: `unable to parse invoice date: ${billDateStr} (${message})`,
      };
    }

    return { type: "RogersBill", billDate, amountDue };
  }
}

export const rogersBill: Readonly<Document<ParsedRogersBill, "RogersBill">> =
  Object.freeze(new RogersBill());
