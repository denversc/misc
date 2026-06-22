export interface DocumentParseError {
  type: "DocumentParseError";
  message: string;
}

export interface DocumentSource {
  text: string;
  lines: readonly string[];
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

  identify(source: Readonly<DocumentSource>): boolean;

  parse(source: Readonly<DocumentSource>): ParsedDocumentT | DocumentParseError;

  calculateFileName(pdf: Readonly<ParsedDocumentT>): string;
}
