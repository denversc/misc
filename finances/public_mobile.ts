import { type ParsePdfError } from "./parse_pdf_error.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";

export interface ParsedPdf {
  type: "PublicMobileStatement";
  invoiceDate: string;
  totalAmountPaid: string;
}

export function identify(
  pdfLines: readonly string[],
): "PublicMobileStatement" | undefined {
  if (pdfLines.includes("Public Mobile Account")) {
    return "PublicMobileStatement";
  }
}

export function parsePdf(pdfLines: string[]): ParsedPdf | ParsePdfError {
  const invoiceIndex = pdfLines.findIndex(
    (line) => line.toLowerCase() === "invoice",
  );
  if (invoiceIndex < 0) {
    return { type: "ParsePdfError", message: "INVOICE line not found" };
  }
  const invoiceDateStr = pdfLines[invoiceIndex + 1]?.trim();
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

  const totalAmountPaidLine = pdfLines.find((line) =>
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

export function calculateFileName(parsedPdf: ParsedPdf): string {
  const { invoiceDate, totalAmountPaid } = parsedPdf;
  return `${invoiceDate} Public Mobile Payment ${totalAmountPaid}.pdf`;
}
