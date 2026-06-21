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
    const awardId = this.#parseAwardId(lines);
    if (isDocumentParseError(awardId)) {
      return awardId;
    }

    const settlementDate = this.#parseSettlementDate(lines);
    if (isDocumentParseError(settlementDate)) {
      return settlementDate;
    }

    const vestedValue = "zzyzx";
    const saleAmount = "zzyzx";
    const sharesSold = "zzyzx";
    const salePrice = "zzyzx";

    return {
      type: "MorganStanleyRelease",
      awardId,
      settlementDate,
      vestedValue,
      saleAmount,
      sharesSold,
      salePrice,
    };
  }

  #parseAwardId(lines: readonly string[]): string | DocumentParseError {
    const regex = /^Award ID:\s+([\w\d]+)$/i;
    const line = lines.find((line) => regex.test(line));
    if (!line) {
      return {
        type: "DocumentParseError",
        message: "Award ID line not found",
      };
    }

    const awardId = line.match(regex)?.[1];
    if (!awardId) {
      throw new Error("internal error stdp7xw6rb: regex should have matched");
    }

    return awardId;
  }

  #parseSettlementDate(lines: readonly string[]): string | DocumentParseError {
    const regex = /^Settlement Date:\s*(\d+-\w+-\d+)$/i;
    const line = lines.find((line) => regex.test(line));
    if (!line) {
      return {
        type: "DocumentParseError",
        message: "Settlement Date line not found",
      };
    }

    const dateStr = line.match(regex)?.[1];
    if (!dateStr) {
      throw new Error("internal error tccydgchk6: regex should have matched");
    }

    const date = parseDateToYYYYMMDD("DD-MMM-YYYY", dateStr);
    if (isParseDateError(date)) {
      const { message } = date;
      return {
        type: "DocumentParseError",
        message: `unable to parse settlement date: ${dateStr} (${message})`,
      };
    }

    return date;
  }
}

export const morganStanleyRelease: Readonly<
  Document<ParsedMorganStanleyRelease, "MorganStanleyRelease">
> = Object.freeze(new MorganStanleyRelease());
