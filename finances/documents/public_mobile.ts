import type { Document, DocumentParseError } from "../document.ts";
import { yyyymmddDateFromPdf, stringFromPdf } from "../document_utils.ts";
import { isDocumentParseError } from "../document.ts";

export interface ParsedPublicMobileStatement {
  type: "PublicMobileStatement";
  invoiceDate: string;
  totalAmountPaid: string;
}

class PublicMobileStatement implements Document<
  ParsedPublicMobileStatement,
  "PublicMobileStatement"
> {
  readonly type = "PublicMobileStatement" as const;

  identify(pdf: string): boolean {
    const regex = /^Public Mobile Account$/im;
    return regex.test(pdf);
  }

  calculateFileName(pdf: Readonly<ParsedPublicMobileStatement>): string {
    const { invoiceDate, totalAmountPaid } = pdf;
    return `${invoiceDate} Public Mobile Payment ${totalAmountPaid}.pdf`;
  }

  parse(pdf: string): ParsedPublicMobileStatement | DocumentParseError {
    const invoiceDate = yyyymmddDateFromPdf(
      pdf,
      /^invoice\s+(\w+\s+\d+,\s+\d+)$/im,
      "MMM D, YYYY",
    );
    if (isDocumentParseError(invoiceDate)) {
      return invoiceDate;
    }

    const totalAmountPaid = stringFromPdf(
      pdf,
      /^total amount paid\s+(\$\d+\.\d+)$/im,
    );
    if (isDocumentParseError(totalAmountPaid)) {
      return totalAmountPaid;
    }

    return { type: "PublicMobileStatement", invoiceDate, totalAmountPaid };
  }
}

export const publicMobileStatement: Readonly<
  Document<ParsedPublicMobileStatement, "PublicMobileStatement">
> = Object.freeze(new PublicMobileStatement());
