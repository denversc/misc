import {
  isDocumentParseError,
  type Document,
  type DocumentParseError,
} from "../document.ts";
import { stringFromLines, yyyymmddDateFromLines } from "../document_utils.ts";

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

  identify(lines: readonly string[]): boolean {
    return lines.some((line) => line.includes("UTILITIES@KITCHENER.CA"));
  }

  calculateFileName(pdf: Readonly<ParsedKitchenerUtilitiesBill>): string {
    const { statementDate, amountDue } = pdf;
    return `${statementDate} Kitchener Utilities Bill ${amountDue}.pdf`;
  }

  parse(
    lines: readonly string[],
  ): ParsedKitchenerUtilitiesBill | DocumentParseError {
    const statementDate = yyyymmddDateFromLines(
      lines,
      /^Statement Date:\s*(\w+\s+\d+\s+\d+)\s+/i,
      "MMM D YYYY",
    );
    if (isDocumentParseError(statementDate)) {
      return statementDate;
    }

    const amountDue = stringFromLines(
      lines,
      /^Pre-authorized Withdrawal:\s*(\d+\.\d+)$/i,
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
