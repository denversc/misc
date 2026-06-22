import type {
  Document,
  DocumentSource,
  DocumentParseError,
} from "../document.ts";
import { isDocumentParseError } from "../document.ts";
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

  identify(source: Readonly<DocumentSource>): boolean {
    return source.lines.some((line) => line.includes("UTILITIES@KITCHENER.CA"));
  }

  calculateFileName(pdf: Readonly<ParsedKitchenerUtilitiesBill>): string {
    const { statementDate, amountDue } = pdf;
    return `${statementDate} Kitchener Utilities Bill ${amountDue}.pdf`;
  }

  parse(
    source: Readonly<DocumentSource>,
  ): ParsedKitchenerUtilitiesBill | DocumentParseError {
    const statementDate = yyyymmddDateFromLines(
      source.lines,
      /^Statement Date:\s*(\w+\s+\d+\s+\d+)\s+/i,
      "MMM D YYYY",
    );
    if (isDocumentParseError(statementDate)) {
      return statementDate;
    }

    const amountDue = stringFromLines(
      source.lines,
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
