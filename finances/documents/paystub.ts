import type {
  Document,
  DocumentSource,
  DocumentParseError,
} from "../document.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "../date.ts";

export type PayStubType =
  | "PayStubRegularPay"
  | "PayStubGSU"
  | "PayStubShuttle"
  | "PayStubMeal";

export function isPayStubType(value: unknown): value is PayStubType {
  return (
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

  constructor(type: Type, regex: RegExp) {
    this.type = type;
    this.#regex = regex;
  }

  identify(source: Readonly<DocumentSource>): boolean {
    if (!source.lines.some((line) => line === "Pay Summary")) {
      return false;
    }

    const match = source.text.match(this.#regex);
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
    throw new Error("not implemented");
  }

  parse(
    source: Readonly<DocumentSource>,
  ): ParsedPayStub<Type> | DocumentParseError {
    throw new Error("not implemented");
  }
}

class PayStubRegularPay extends PayStub<"PayStubRegularPay"> {
  constructor() {
    super(
      "PayStubRegularPay",
      /\sRegular\s+Pay\s+\d+\.\d+\s+\$\d+\.\d+\s+(\$[\d,]+\.\d+)\s/i,
    );
  }
}

class PayStubGSU extends PayStub<"PayStubGSU"> {
  constructor() {
    super(
      "PayStubGSU",
      /\sGoogle\s+Stock\s+Un\s+0.0*\s+\$0.0*\s+(\$[\d,]+\.\d+)\s/i,
    );
  }
}

class PayStubShuttle extends PayStub<"PayStubShuttle"> {
  constructor() {
    super(
      "PayStubShuttle",
      /\sCA\s+Shuttle\s+Bus\s+\$[\d,]+\.\d+\s+(\$[\d,]+\.\d+)\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+\s/,
    );
  }
}

class PayStubMeal extends PayStub<"PayStubMeal"> {
  constructor() {
    super(
      "PayStubMeal",
      /\sMeal\s+Benefit\s+\$[\d,]+\.\d+\s+(\$[\d,]+\.\d+)\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+\s+\$[\d,]+\.\d+\s/,
    );
  }
}

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
