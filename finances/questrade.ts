import { type Document } from "./document.ts";
import { type ParsePdfError } from "./parse_pdf_error.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";

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

export interface ParsedQuestradeStatement<Type extends StatementType> {
  type: Type;
  statementDate: string;
  accountNumber: string;
  balance: string;
}

export type ParsedQuestradeRESPStatement =
  ParsedQuestradeStatement<"QuestradeRESPStatement">;
export type ParsedQuestradeRRSPStatement =
  ParsedQuestradeStatement<"QuestradeRRSPStatement">;
export type ParsedQuestradeMarginStatement =
  ParsedQuestradeStatement<"QuestradeMarginStatement">;

class QuestradeStatement<Type extends StatementType> implements Document<
  ParsedQuestradeStatement<Type>,
  Type
> {
  readonly type: Type;
  readonly #identifyingLine: string;
  readonly #fileNameType: string;

  constructor(type: Type, identifyingLine: string, fileNameType: string) {
    this.type = type;
    this.#identifyingLine = identifyingLine.toLowerCase();
    this.#fileNameType = fileNameType;
  }

  identify(lines: readonly string[]): boolean {
    if (
      !lines.some((line) =>
        line.toLowerCase().startsWith("questrade wealth management inc."),
      )
    ) {
      return false;
    }

    if (
      lines.some((line) => line.toLowerCase().includes(this.#identifyingLine))
    ) {
      return true;
    }

    return false;
  }

  calculateFileName(pdf: Readonly<ParsedQuestradeStatement<Type>>): string {
    const { statementDate, accountNumber, balance } = pdf;
    return (
      `${statementDate} Questrade ${this.#fileNameType} ` +
      `${accountNumber} Statement ${balance}.pdf`
    );
  }

  parse(
    lines: readonly string[],
  ): ParsedQuestradeStatement<Type> | ParsePdfError {
    const accountNumberRegex = /Account\s*#:\s*(\d+)/i;
    const accountNumberLine = lines.find((line) =>
      accountNumberRegex.test(line),
    );
    if (!accountNumberLine) {
      return {
        type: "ParsePdfError",
        message: "Account number line not found",
      };
    }
    const accountNumber = accountNumberLine.match(accountNumberRegex)?.[1];
    if (!accountNumber) {
      throw new Error(
        "internal error rhtan4myg2: accountNumberRegex should have matched",
      );
    }

    const currentMonthRegex = /Current month\s*:\s*(\w+\s+\d+,\s*\d+)/i;
    const currentMonthLine = lines.find((line) =>
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
        message: `unable to parse statement date: ${statementDateStr} (${message})`,
      };
    }

    const balanceRegex = /Current month balance:\s*(\$[\d,.]+)/i;
    const balanceLine = lines.find((line) => line.match(balanceRegex));
    if (!balanceLine) {
      return { type: "ParsePdfError", message: "Balance line not found" };
    }
    const balance = balanceLine.match(balanceRegex)?.[1];
    if (!balance) {
      throw new Error(
        "internal error ky4fmdxh8b: balanceRegex should have matched",
      );
    }

    return { type: this.type, statementDate, accountNumber, balance };
  }
}

class QuestradeRESPStatement extends QuestradeStatement<"QuestradeRESPStatement"> {
  constructor() {
    super("QuestradeRESPStatement", "(RESP)", "RESP");
  }
}

class QuestradeRRSPStatement extends QuestradeStatement<"QuestradeRRSPStatement"> {
  constructor() {
    super(
      "QuestradeRRSPStatement",
      "registered retirement savings plan",
      "RRSP",
    );
  }
}

class QuestradeMarginStatement extends QuestradeStatement<"QuestradeMarginStatement"> {
  constructor() {
    super(
      "QuestradeMarginStatement",
      "individual margin account",
      "Margin Account",
    );
  }
}

export const questradeRESPStatement: Readonly<
  Document<ParsedQuestradeRESPStatement, "QuestradeRESPStatement">
> = Object.freeze(new QuestradeRESPStatement());

export const questradeRRSPStatement: Readonly<
  Document<ParsedQuestradeRRSPStatement, "QuestradeRRSPStatement">
> = Object.freeze(new QuestradeRRSPStatement());

export const questradeMarginStatement: Readonly<
  Document<ParsedQuestradeMarginStatement, "QuestradeMarginStatement">
> = Object.freeze(new QuestradeMarginStatement());
