import type { Document, DocumentParseError } from "../document.ts";
import { isDocumentParseError } from "../document.ts";
import { stringFromPdf, yyyymmddDateFromPdf } from "../document_utils.ts";

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

  identify(pdf: string): boolean {
    const regex = /^release confirmation$/im;
    return regex.test(pdf);
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

  parse(pdf: string): ParsedMorganStanleyRelease | DocumentParseError {
    const awardId = stringFromPdf(pdf, /^Award ID:\s+([\w\d]+)$/im);
    if (isDocumentParseError(awardId)) {
      return awardId;
    }

    const settlementDate = yyyymmddDateFromPdf(
      pdf,
      /^Settlement Date:\s*(\d+-\w+-\d+)$/im,
      "DD-MMM-YYYY",
    );
    if (isDocumentParseError(settlementDate)) {
      return settlementDate;
    }

    const vestedValue = stringFromPdf(pdf, /^Total Gain.*:\s*(\$[\d,.]+)$/im);
    if (isDocumentParseError(vestedValue)) {
      return vestedValue;
    }

    const saleAmount = stringFromPdf(
      pdf,
      /^Sale PricexQuantity Sold:\s*\((\$[\d,.]+)\)$/im,
    );
    if (isDocumentParseError(saleAmount)) {
      return saleAmount;
    }

    const sharesSold = stringFromPdf(
      pdf,
      /^Quantity Sold:\s*\((\d+\.\d{3})0*\)$/im,
    );
    if (isDocumentParseError(sharesSold)) {
      return sharesSold;
    }

    const salePrice = stringFromPdf(
      pdf,
      /\sshares at (\$\d+\.\d{4})0* per share\s/im,
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
