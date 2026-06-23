import type { Document, DocumentParseError } from "../document.ts";
import { isDocumentParseError } from "../document.ts";
import { yyyymmddDateFromPdf, stringFromPdf } from "../document_utils.ts";

export interface ParsedRogersBill {
  type: "RogersBill";
  billDate: string;
  amountDue: string;
}

class RogersBill implements Document<ParsedRogersBill, "RogersBill"> {
  readonly type = "RogersBill" as const;

  identify(pdf: string): boolean {
    const regex = /^Call 1-888-ROGERS-1$/im;
    return regex.test(pdf);
  }

  calculateFileName(pdf: Readonly<ParsedRogersBill>): string {
    const { billDate, amountDue } = pdf;
    return `${billDate} Rogers Bill ${amountDue}.pdf`;
  }

  parse(pdf: string): ParsedRogersBill | DocumentParseError {
    const amountDue = stringFromPdf(
      pdf,
      /^what is the total due\?\s+(\$\d+\.\d+)$/im,
    );
    if (isDocumentParseError(amountDue)) {
      return amountDue;
    }

    const billDate = yyyymmddDateFromPdf(
      pdf,
      /^bill date\s+(\w+\s+\d+,\s+\d+)$/im,
      "MMM D, YYYY",
    );
    if (isDocumentParseError(billDate)) {
      return billDate;
    }

    return { type: "RogersBill", billDate, amountDue };
  }
}

export const rogersBill: Readonly<Document<ParsedRogersBill, "RogersBill">> =
  Object.freeze(new RogersBill());
