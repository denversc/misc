import type { Document, DocumentParseError } from "../document.ts";
import { isDocumentParseError } from "../document.ts";
import { stringFromPdf, yyyymmddDateFromPdf } from "../document_utils.ts";

export interface ParsedPCMastercardStatement {
  type: "PCMastercardStatement";
  statementDate: string;
  purchases: string;
}

class PCMastercardStatement implements Document<
  ParsedPCMastercardStatement,
  "PCMastercardStatement"
> {
  readonly type = "PCMastercardStatement" as const;

  identify(pdf: string): boolean {
    const regex = /^President's Choice Financial Mastercard\W/im;
    return regex.test(pdf);
  }

  calculateFileName(pdf: Readonly<ParsedPCMastercardStatement>): string {
    const { statementDate, purchases } = pdf;
    return `${statementDate} PC MasterCard Statement ${purchases}.pdf`;
  }

  parse(pdf: string): ParsedPCMastercardStatement | DocumentParseError {
    const statementDate = yyyymmddDateFromPdf(
      pdf,
      /^Statement date:\s*(\w+\.?\s+\d+,\s+\d+)$/im,
      "MM D, YYYY",
      { resultTransform: transformMonthNameToNumber },
    );
    if (isDocumentParseError(statementDate)) {
      return statementDate;
    }

    const purchases = stringFromPdf(
      pdf,
      /^\+\s*Purchases\s+(\$[\d,]+\.\d+)$/im,
    );
    if (isDocumentParseError(purchases)) {
      return purchases;
    }

    return {
      type: "PCMastercardStatement",
      statementDate,
      purchases,
    };
  }
}

const monthNumberByName = Object.freeze({
  "Jan.": "01",
  "Feb.": "02",
  "Mar.": "03",
  "Apr.": "04",
  May: "05",
  June: "06",
  July: "07",
  "Aug.": "08",
  "Sept.": "09",
  "Oct.": "10",
  "Nov.": "11",
  "Dec.": "12",
} as const);

function transformMonthNameToNumber(s: string): string | DocumentParseError {
  const replacements: Array<{ monthName: string; monthNumber: string }> = [];

  const months = Object.entries(monthNumberByName) as Readonly<
    Array<Readonly<[keyof typeof monthNumberByName, string]>>
  >;
  for (const [monthName, monthNumber] of months) {
    if (s.includes(monthName)) {
      replacements.push({ monthName, monthNumber });
    }
  }

  const replacement = replacements[0];
  if (!replacement) {
    return {
      type: "DocumentParseError",
      message:
        `unrecognized month name in date: ${s} ` +
        `(recognized month names are: ` +
        Object.getOwnPropertyNames(monthNumberByName).join(", ") +
        `)`,
    };
  } else if (replacements.length > 1) {
    return {
      type: "DocumentParseError",
      message:
        `${replacements.length} month names recognized in date, ` +
        `but expected exactly 1: ${s} ` +
        `(recognized month names: ` +
        replacements.map((entry) => entry.monthName).join(", ") +
        `)`,
    };
  }

  const { monthName, monthNumber } = replacement;
  return s.replace(monthName, monthNumber);
}

export const pcMastercardStatement: Readonly<
  Document<ParsedPCMastercardStatement, "PCMastercardStatement">
> = Object.freeze(new PCMastercardStatement());
