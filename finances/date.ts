import { parse as tempoParse, format as tempoFormat } from "@formkit/tempo";
import { messageForError } from "./error.ts";

export interface ParseDateError {
  type: "ParseDateError";
  message: string;
}

export function isParseDateError(e: unknown): e is ParseDateError {
  return (
    e !== null &&
    typeof e === "object" &&
    "type" in e &&
    e.type === "ParseDateError" &&
    "message" in e &&
    typeof e.message === "string"
  );
}

export function parseDateToYYYYMMDD(
  format: string,
  text: string,
): string | ParseDateError {
  let parsedDate: Date;
  try {
    parsedDate = tempoParse(text, format, "en");
  } catch (e: unknown) {
    return { type: "ParseDateError", message: messageForError(e) };
  }

  if (isNaN(parsedDate.getTime())) {
    return { type: "ParseDateError", message: "invalid date" };
  }

  return tempoFormat(parsedDate, "YYYY-MM-DD");
}
