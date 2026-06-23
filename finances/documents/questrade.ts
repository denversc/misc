import type { Document, DocumentParseError } from "../document.ts";
import { isDocumentParseError } from "../document.ts";
import { yyyymmddDateFromPdf, stringFromPdf } from "../document_utils.ts";

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

  identify(pdf: string): boolean {
    const identifyRegex = /^questrade wealth management inc\.\s/im;
    if (!identifyRegex.test(pdf)) {
      return false;
    }

    const lineRegex = RegExp(
      "\\s" + RegExp.escape(this.#identifyingLine) + "\\s",
      "i",
    );
    return lineRegex.test(pdf);
  }

  calculateFileName(pdf: Readonly<ParsedQuestradeStatement<Type>>): string {
    const { statementDate, accountNumber, balance } = pdf;
    return (
      `${statementDate} Questrade ${this.#fileNameType} ` +
      `${accountNumber} Statement ${balance}.pdf`
    );
  }

  parse(pdf: string): ParsedQuestradeStatement<Type> | DocumentParseError {
    const accountNumber = stringFromPdf(pdf, /^Account\s*#\s*:\s*(\d+)\s/im);
    if (isDocumentParseError(accountNumber)) {
      return accountNumber;
    }

    const statementDate = yyyymmddDateFromPdf(
      pdf,
      /\sCurrent month\s*:\s*(\w+\s+\d+,\s*\d+)$/im,
      "MMMM D, YYYY",
    );
    if (isDocumentParseError(statementDate)) {
      return statementDate;
    }

    const balance = stringFromPdf(
      pdf,
      /^Current month balance:\s*(\$[\d,]+\.\d+)$/im,
    );
    if (isDocumentParseError(balance)) {
      return balance;
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
