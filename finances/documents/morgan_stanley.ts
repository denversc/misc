import {
  isDocumentParseError,
  type Document,
  type DocumentParseError,
} from "../document.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "../date.ts";

export interface ParsedMorganStanleyRelease {
  type: "MorganStanleyRelease";
  awardId: string;
  settlementDate: string;
  vestedValue: string;
  saleAmount: string;
  sharesSold: string;
  salePrice: string;
}

class MorganStanleyRelease implements Document<
  ParsedMorganStanleyRelease,
  "MorganStanleyRelease"
> {
  readonly type = "MorganStanleyRelease" as const;

  identify(lines: readonly string[]): boolean {
    return lines.some((line) => line.toLowerCase() === "release confirmation");
  }

  calculateFileName(pdf: Readonly<ParsedMorganStanleyRelease>): string {
    const {
      awardId,
      settlementDate,
      vestedValue,
      saleAmount,
      sharesSold,
      salePrice,
    } = pdf;
    return (
      `${settlementDate} Morgan Stanley Release Confirmation ` +
      `${awardId} ${sharesSold} shares vested for ` +
      `${vestedValue} sold for ${saleAmount} ` +
      `(${salePrice} per share)`
    );
  }

  parse(
    lines: readonly string[],
  ): ParsedMorganStanleyRelease | DocumentParseError {
    const statementDate = this.#parseStatementDate(lines);
    if (isDocumentParseError(statementDate)) {
      return statementDate;
    }

    const amountDue = this.#parseAmountDue(lines);
    if (isDocumentParseError(amountDue)) {
      return amountDue;
    }

    return { type: "MorganStanleyRelease", statementDate, amountDue };
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

export const morganStanleyRelease: Readonly<
  Document<ParsedMorganStanleyRelease, "MorganStanleyRelease">
> = Object.freeze(new MorganStanleyRelease());
