import { type ParsePdfError } from "./parse_pdf_error.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";
import { unreachable } from "./unreachable.ts";

export type StatementType =
  | "QuestradeRESPStatement"
  | "QuestradeRRSPStatement"
  | "QuestradeMarginStatement";

export function isStatementType(value: unknown): value is StatementType {
  return (
    value === "QuestradeRESPStatement" ||
    value === "QuestradeRRSPStatement" ||
    value === "QuestradeMarginStatement"
  );
}

export interface ParsedPdf {
  type: StatementType;
  statementDate: string;
  accountNumber: string;
  balance: string;
}

export function identify(
  pdfLines: readonly string[],
): StatementType | undefined {
  if (
    !pdfLines.some((line) =>
      line.toLowerCase().startsWith("questrade wealth management inc."),
    )
  ) {
    return undefined;
  }

  if (pdfLines.some((line) => line.includes("(RESP)"))) {
    return "QuestradeRESPStatement";
  }

  if (
    pdfLines.some((line) =>
      line.toLowerCase().includes("registered retirement savings plan"),
    )
  ) {
    return "QuestradeRRSPStatement";
  }

  if (
    pdfLines.some((line) =>
      line.toLowerCase().includes("individual margin account"),
    )
  ) {
    return "QuestradeMarginStatement";
  }

  return undefined;
}

export function parsePdf(
  pdfLines: readonly string[],
): ParsedPdf | ParsePdfError {
  const type = identify(pdfLines);
  if (!type) {
    return {
      type: "ParsePdfError",
      message: "Unable to determine Questrade statement type",
    };
  }

  const accountNumberRegex = /Account\s*#:\s*(\d+)/i;
  const accountNumberLine = pdfLines.find((line) =>
    accountNumberRegex.test(line),
  );
  if (!accountNumberLine) {
    return { type: "ParsePdfError", message: "Account number line not found" };
  }
  const accountNumber = accountNumberLine.match(accountNumberRegex)?.[1];
  if (!accountNumber) {
    throw new Error(
      "internal error rhtan4myg2: accountNumberRegex should have matched",
    );
  }

  const currentMonthRegex = /Current month\s*:\s*(\w+\s+\d+,\s*\d+)/i;
  const currentMonthLine = pdfLines.find((line) =>
    line.match(currentMonthRegex),
  );
  if (!currentMonthLine) {
    return { type: "ParsePdfError", message: "Current month line not found" };
  }
  const statementDateStr = currentMonthLine.match(currentMonthRegex)?.[1];
  if (!statementDateStr) {
    throw new Error(
      "internal error ydjbyakqr8: currentMonthRegex should have matched",
    );
  }
  const statementDate = parseDateToYYYYMMDD("MMMM D, YYYY", statementDateStr);
  if (isParseDateError(statementDate)) {
    const { message } = statementDate;
    return {
      type: "ParsePdfError",
      message:
        `unable to parse statement date: ${statementDateStr} ` + `(${message})`,
    };
  }

  const balanceRegex = /Current month balance:\s*(\$[\d,.]+)/i;
  const balanceLine = pdfLines.find((line) => line.match(balanceRegex));
  if (!balanceLine) {
    return { type: "ParsePdfError", message: "Balance line not found" };
  }
  const balance = balanceLine.match(balanceRegex)?.[1];
  if (!balance) {
    throw new Error(
      "internal error ky4fmdxh8b: balanceRegex should have matched",
    );
  }

  return { type, statementDate, accountNumber, balance };
}

export function calculateFileName(parsedPdf: ParsedPdf): string {
  const { type, statementDate, accountNumber, balance } = parsedPdf;
  let typeName: string;
  if (type === "QuestradeRESPStatement") {
    typeName = "RESP";
  } else if (type === "QuestradeRRSPStatement") {
    typeName = "RRSP";
  } else if (type === "QuestradeMarginStatement") {
    typeName = "Margin Account";
  } else {
    unreachable(type, "unknown type");
  }

  return `${statementDate} Questrade ${typeName} ${accountNumber} Statement ${balance}.pdf`;
}
