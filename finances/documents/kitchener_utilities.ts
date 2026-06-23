import type { Document, DocumentParseError } from "../document.ts";
import { isDocumentParseError } from "../document.ts";
import { stringFromPdf, yyyymmddDateFromPdf } from "../document_utils.ts";

export interface ParsedKitchenerUtilitiesBill {
  type: "KitchenerUtilitiesBill";
  statementDate: string;
  amountDue: string;
}

class KitchenerUtilitiesBill implements Document<
  ParsedKitchenerUtilitiesBill,
  "KitchenerUtilitiesBill"
> {
  readonly type = "KitchenerUtilitiesBill" as const;

  identify(pdf: string): boolean {
    const regex = /\s519-741-2626.*utilities@kitchener.ca$/im;
    return regex.test(pdf);
  }

  calculateFileName(pdf: Readonly<ParsedKitchenerUtilitiesBill>): string {
    const { statementDate, amountDue } = pdf;
    return `${statementDate} Kitchener Utilities Bill ${amountDue}.pdf`;
  }

  parse(pdf: string): ParsedKitchenerUtilitiesBill | DocumentParseError {
    const statementDate = yyyymmddDateFromPdf(
      pdf,
      /^Statement Date:\s*(\w+\s+\d+\s+\d+)\s/im,
      "MMM D YYYY",
    );
    if (isDocumentParseError(statementDate)) {
      return statementDate;
    }

    const amountDue = stringFromPdf(
      pdf,
      /^Pre-authorized Withdrawal:\s*(\d+\.\d+)$/im,
      { resultPrefix: "$" },
    );
    if (isDocumentParseError(amountDue)) {
      return amountDue;
    }

    return { type: "KitchenerUtilitiesBill", statementDate, amountDue };
  }
}

export const kitchenerUtilitiesBill: Readonly<
  Document<ParsedKitchenerUtilitiesBill, "KitchenerUtilitiesBill">
> = Object.freeze(new KitchenerUtilitiesBill());
