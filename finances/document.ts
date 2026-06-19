export interface DocumentParseError {
  type: "DocumentParseError";
  message: string;
}

export function isDocumentParseError(e: unknown): e is DocumentParseError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "DocumentParseError" &&
    "message" in e &&
    typeof e.message === "string"
  );
}

export interface ParsedDocument<TypeName extends string> {
  readonly type: TypeName;
}

export interface Document<
  ParsedDocumentT extends ParsedDocument<TypeName>,
  TypeName extends string,
> {
  readonly type: TypeName;

  identify(lines: readonly string[]): boolean;

  parse(lines: readonly string[]): ParsedDocumentT | DocumentParseError;

  calculateFileName(pdf: Readonly<ParsedDocumentT>): string;
}
