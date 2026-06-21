import {
  isDocumentParseError,
  type Document,
  type DocumentParseError,
} from "../document.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "../date.ts";

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
    const statementDate = this.#parseStatementDate(lines);
    if (isDocumentParseError(statementDate)) {
      return statementDate;
    }

    const amountDue = this.#parseAmountDue(lines);
    if (isDocumentParseError(amountDue)) {
      return amountDue;
    }

    return { type: "KitchenerUtilitiesBill", statementDate, amountDue };
  }

  #parseStatementDate(lines: readonly string[]): string | DocumentParseError {
    const regex = /Statement Date:\s*(\w+\s+\d+\s+\d+)/i;
    const line = lines.find((line) => regex.test(line));
    if (!line) {
      return {
        type: "DocumentParseError",
        message: "Statement Date line not found",
      };
    }

    const dateStr = line.match(regex)?.[1];
    if (!dateStr) {
      throw new Error("internal error vngd3pn5ry: regex should have matched");
    }

    const date = parseDateToYYYYMMDD("MMM D YYYY", dateStr);
    if (isParseDateError(date)) {
      const { message } = date;
      return {
        type: "DocumentParseError",
        message: `unable to parse statement date: ${dateStr} (${message})`,
      };
    }

    return date;
  }

  #parseAmountDue(lines: readonly string[]): string | DocumentParseError {
    const regex = /Pre-authorized Withdrawal:\s*(\d+\.\d+)/i;
    const line = lines.find((line) => regex.test(line));
    if (!line) {
      return {
        type: "DocumentParseError",
        message: "Pre-authorized Withdrawal line not found",
      };
    }

    const amountDueStr = line.match(regex)?.[1];
    if (!amountDueStr) {
      throw new Error("internal error ms3atxxre5: regex should have matched");
    }

    return `$${amountDueStr}`;
  }
}

export const kitchenerUtilitiesBill: Readonly<
  Document<ParsedKitchenerUtilitiesBill, "KitchenerUtilitiesBill">
> = Object.freeze(new KitchenerUtilitiesBill());
