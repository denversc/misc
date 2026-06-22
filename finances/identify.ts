import { type DocumentSource } from "./document.ts";
import { allDocuments, type Documents } from "./documents.ts";

export interface IdentifyError {
  type: "IdentifyError";
  message: string;
}

export function isIdentifyError(e: unknown): e is IdentifyError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "IdentifyError" &&
    "message" in e &&
    typeof e.message === "string"
  );
}

export function identify(
  source: Readonly<DocumentSource>,
): Documents | IdentifyError | undefined {
  const filteredDocuments = allDocuments.filter((document) =>
    document.identify(source),
  );

  if (filteredDocuments.length > 1) {
    const types = filteredDocuments.map((document) => document.type);
    const typesStr = types.sort().join();
    return {
      type: "IdentifyError",
      message:
        `Unable to uniquely identify the PDF type; ` +
        `the PDF matched ${filteredDocuments.length} types: ${typesStr}`,
    };
  }

  return filteredDocuments[0];
}
