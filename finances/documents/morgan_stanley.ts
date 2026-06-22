import type {
  Document,
  DocumentSource,
  DocumentParseError,
} from "../document.ts";
import { isDocumentParseError } from "../document.ts";
import { stringFromLines, yyyymmddDateFromLines } from "../document_utils.ts";

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

  identify(source: Readonly<DocumentSource>): boolean {
    return source.lines.some(
      (line) => line.toLowerCase() === "release confirmation",
    );
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
      `(${salePrice} per share).pdf`
    );
  }

  parse(
    source: Readonly<DocumentSource>,
  ): ParsedMorganStanleyRelease | DocumentParseError {
    const awardId = stringFromLines(source.lines, /^Award ID:\s+([\w\d]+)$/i);
    if (isDocumentParseError(awardId)) {
      return awardId;
    }

    const settlementDate = yyyymmddDateFromLines(
      source.lines,
      /^Settlement Date:\s*(\d+-\w+-\d+)$/i,
      "DD-MMM-YYYY",
    );
    if (isDocumentParseError(settlementDate)) {
      return settlementDate;
    }

    const vestedValue = stringFromLines(
      source.lines,
      /^Total Gain.*:\s*(\$[\d,.]+)$/i,
    );
    if (isDocumentParseError(vestedValue)) {
      return vestedValue;
    }

    const saleAmount = stringFromLines(
      source.lines,
      /^Sale PricexQuantity Sold:\s*\((\$[\d,.]+)\)$/i,
    );
    if (isDocumentParseError(saleAmount)) {
      return saleAmount;
    }

    const sharesSold = stringFromLines(
      source.lines,
      /^Quantity Sold:\s*\((\d+\.\d{3})0*\)$/i,
    );
    if (isDocumentParseError(sharesSold)) {
      return sharesSold;
    }

    const salePrice = stringFromLines(
      source.lines,
      /shares at (\$\d+\.\d{4})0* per share/i,
    );
    if (isDocumentParseError(salePrice)) {
      return salePrice;
    }

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
