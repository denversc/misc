import { type ParsePdfError } from "./parse_pdf_error.ts";

export interface ParsedDocument<TypeName extends string> {
  readonly type: TypeName;
}

export interface Document<
  ParsedPdf extends ParsedDocument<TypeName>,
  TypeName extends string,
> {
  readonly type: TypeName;

  identify(lines: readonly string[]): boolean;

  parse(lines: readonly string[]): ParsedPdf | ParsePdfError;

  calculateFileName(pdf: Readonly<ParsedPdf>): string;
}
