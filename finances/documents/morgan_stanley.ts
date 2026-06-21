import {
  isDocumentParseError,
  type Document,
  type DocumentParseError,
} from "../document.ts";
import { stringFromLines, yyyymmddDateFromLines } from "../document_utils.ts";
import { prefixMessage } from "../error.ts";

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
    const awardId = stringFromLines(lines, /^Award ID:\s+([\w\d]+)$/i);
    if (isDocumentParseError(awardId)) {
      prefixMessage(awardId, "Award ID not found: ");
      return awardId;
    }

    const settlementDate = yyyymmddDateFromLines(
      lines,
      /^Settlement Date:\s*(\d+-\w+-\d+)$/i,
      "DD-MMM-YYYY",
    );
    if (isDocumentParseError(settlementDate)) {
      prefixMessage(settlementDate, "Settlement Date not found: ");
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
}

export const morganStanleyRelease: Readonly<
  Document<ParsedMorganStanleyRelease, "MorganStanleyRelease">
> = Object.freeze(new MorganStanleyRelease());
