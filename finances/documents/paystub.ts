import type { Document, DocumentParseError } from "../document.ts";
import { isDocumentParseError } from "../document.ts";
import { yyyymmddDateFromPdf } from "../document_utils.ts";

export type PayStubType =
  | "PayStubAnnualBonus"
  | "PayStubRegularPay"
  | "PayStubGSU"
  | "PayStubShuttle"
  | "PayStubMeal";

export function isPayStubType(value: unknown): value is PayStubType {
  return (
    value === "PayStubAnnualBonus" ||
    value === "PayStubRegularPay" ||
    value === "PayStubGSU" ||
    value === "PayStubShuttle" ||
    value === "PayStubMeal"
  );
}

export interface ParsedPayStub<Type extends PayStubType> {
  type: Type;
  payDate: string;
  amount: string;
}

export type ParsedPayStubAnnualBonus = ParsedPayStub<"PayStubAnnualBonus">;
export type ParsedPayStubRegularPay = ParsedPayStub<"PayStubRegularPay">;
export type ParsedPayStubGSU = ParsedPayStub<"PayStubGSU">;
export type ParsedPayStubShuttle = ParsedPayStub<"PayStubShuttle">;
export type ParsedPayStubMeal = ParsedPayStub<"PayStubMeal">;

const zeroDollarsRegex = /\$[0,]+\.0+/;

class PayStub<Type extends PayStubType> implements Document<
  ParsedPayStub<Type>,
  Type
> {
  readonly type: Type;
  readonly #regex: RegExp;
  readonly #filenameTemplate: string;

  constructor(type: Type, regex: RegExp, filenameTemplate: string) {
    this.type = type;
    this.#regex = regex;
    this.#filenameTemplate = filenameTemplate;
  }

  identify(pdf: string): boolean {
    const identifyRegex = /^Pay Summary$/im;
    if (!identifyRegex.test(pdf)) {
      return false;
    }

    const match = pdf.match(this.#regex);
    if (!match) {
      return false;
    }

    const amount = match[1];
    if (typeof amount === "undefined") {
      throw new Error(
        `internal error vkwqspedkb: matching text should not be undefined; ` +
          `regex=${this.#regex.source}, match=${match[0]}`,
      );
    }

    return !zeroDollarsRegex.test(amount);
  }

  calculateFileName(pdf: Readonly<ParsedPayStub<Type>>): string {
    const parentheticalText = this.#filenameTemplate.replace(
      "__AMOUNT__",
      pdf.amount,
    );
    return `${pdf.payDate} Google Pay Stub (${parentheticalText}).pdf`;
  }

  parse(pdf: string): ParsedPayStub<Type> | DocumentParseError {
    const payDate = yyyymmddDateFromPdf(
      pdf,
      /^Pay\s+Date\s+(\d+\s+\d+\s+\d+)$/im,
      "YYYY MM DD",
    );
    if (isDocumentParseError(payDate)) {
      return payDate;
    }

    const match = pdf.match(this.#regex);
    if (!match) {
      return {
        type: "DocumentParseError",
        message: `no match found for regex: ${this.#regex.source}`,
      };
    }

    const amount = match[1];
    if (typeof amount === "undefined") {
      throw new Error(
        `internal error vkwqspedkb: regex should have matched line; ` +
          `regex=${this.#regex.source}, match=${match[0]}`,
      );
    }

    return { type: this.type, payDate, amount };
  }
}

class PayStubAnnualBonus extends PayStub<"PayStubAnnualBonus"> {
  constructor() {
    super(
      "PayStubAnnualBonus",
      /^Annual\s+Bonus\s+(\$[\d,]+\.\d+)\s+\$[\d,]+\.\d+$/im,
      "Annual Bonus",
    );
  }
}

class PayStubRegularPay extends PayStub<"PayStubRegularPay"> {
  constructor() {
    super(
      "PayStubRegularPay",
      /^Regular\s+Pay\s+\d+\.\d+\s+\$\d+\.\d+\s+(\$[\d,]+\.\d+)\s/im,
      "Regular Pay",
    );
  }
}

class PayStubGSU extends PayStub<"PayStubGSU"> {
  constructor() {
    super(
      "PayStubGSU",
      /^Google\s+Stock\s+Un\s+0.0*\s+\$0.0*\s+(\$[\d,]+\.\d+)\s/im,
      "GSU Vest __AMOUNT__ CAD",
    );
  }
}

class PayStubShuttle extends PayStub<"PayStubShuttle"> {
  constructor() {
    super(
      "PayStubShuttle",
      /^CA\s+Shuttle\s+Bus\s+\$[\d,]+\.\d+\s+(\$[\d,]+\.\d+)\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+$/im,
      "Shuttle Bus",
    );
  }
}

class PayStubMeal extends PayStub<"PayStubMeal"> {
  constructor() {
    super(
      "PayStubMeal",
      /^Meal\s+Benefit\s+\$[\d,]+\.\d+\s+(\$[\d,]+\.\d+)\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+$/im,
      "Meal Benefit",
    );
  }
}

export const payStubAnnualBonus: Readonly<
  Document<ParsedPayStubAnnualBonus, "PayStubAnnualBonus">
> = Object.freeze(new PayStubAnnualBonus());

export const payStubRegularPay: Readonly<
  Document<ParsedPayStubRegularPay, "PayStubRegularPay">
> = Object.freeze(new PayStubRegularPay());

export const payStubGSU: Readonly<Document<ParsedPayStubGSU, "PayStubGSU">> =
  Object.freeze(new PayStubGSU());

export const payStubShuttle: Readonly<
  Document<ParsedPayStubShuttle, "PayStubShuttle">
> = Object.freeze(new PayStubShuttle());

export const payStubMeal: Readonly<Document<ParsedPayStubMeal, "PayStubMeal">> =
  Object.freeze(new PayStubMeal());
