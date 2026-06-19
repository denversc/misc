import { type Document } from "./document.ts";
import { type ParsePdfError } from "./parse_pdf_error.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";

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

  identify(lines: readonly string[]): boolean {
    return lines.includes("Public Mobile Account");
  }

  calculateFileName(pdf: Readonly<ParsedPublicMobileStatement>): string {
    const { invoiceDate, totalAmountPaid } = pdf;
    return `${invoiceDate} Public Mobile Payment ${totalAmountPaid}.pdf`;
  }

  parse(lines: readonly string[]): ParsedPublicMobileStatement | ParsePdfError {
    const invoiceIndex = lines.findIndex(
      (line) => line.toLowerCase() === "invoice",
    );
    if (invoiceIndex < 0) {
      return { type: "ParsePdfError", message: "INVOICE line not found" };
    }
    const invoiceDateStr = lines[invoiceIndex + 1]?.trim();
    if (!invoiceDateStr) {
      return {
        type: "ParsePdfError",
        message: "expected line after INVOICE line",
      };
    }
    const invoiceDate = parseDateToYYYYMMDD("MMM D, YYYY", invoiceDateStr);
    if (isParseDateError(invoiceDate)) {
      const { message } = invoiceDate;
      return {
        type: "ParsePdfError",
        message: `unable to parse invoice date: ${invoiceDateStr} (${message})`,
      };
    }

    const totalAmountPaidLine = lines.find((line) =>
      line.toLowerCase().startsWith("total amount paid"),
    );
    if (!totalAmountPaidLine) {
      return {
        type: "ParsePdfError",
        message: "Total Amount Paid line not found",
      };
    }

    const totalAmountPaid = totalAmountPaidLine.substring(17).trim();

    return { type: "PublicMobileStatement", invoiceDate, totalAmountPaid };
  }
}

export const publicMobileStatement: Readonly<
  Document<ParsedPublicMobileStatement, "PublicMobileStatement">
> = Object.freeze(new PublicMobileStatement());
