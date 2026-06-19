export interface ParsePdfError {
  type: "ParsePdfError";
  message: string;
}

export function isParsePdfError(e: unknown): e is ParsePdfError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "ParsePdfError" &&
    "message" in e &&
    typeof e.message === "string"
  );
}
