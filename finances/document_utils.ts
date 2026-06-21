import { isDocumentParseError, type DocumentParseError } from "./document.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";

interface StringFromLinesOptions {
  resultPrefix: string;
}

export function stringFromLines(
  lines: readonly string[],
  regex: RegExp,
  options?: Partial<StringFromLinesOptions>,
): string | DocumentParseError {
  for (const line of lines) {
    const trimmedLine = line.trim();
    const match = trimmedLine.match(regex);
    if (!match) {
      continue;
    }

    const matchingString = match[1];
    if (typeof matchingString === "undefined") {
      throw new Error(
        `internal error stdp7xw6rb: regex should have matched line; ` +
          `regex=${regex.source}, line=${trimmedLine}`,
      );
    }

    const resultPrefix = options?.resultPrefix;
    if (typeof resultPrefix === "undefined") {
      return matchingString;
    } else {
      return resultPrefix + matchingString;
    }
  }

  return {
    type: "DocumentParseError",
    message: `line not found matching regex: ${regex.source}`,
  };
}

export function yyyymmddDateFromLines(
  lines: readonly string[],
  regex: RegExp,
  dateFormat: string,
): string | DocumentParseError {
  const dateStr = stringFromLines(lines, regex);
  if (isDocumentParseError(dateStr)) {
    return dateStr;
  }

  const date = parseDateToYYYYMMDD(dateFormat, dateStr);
  if (isParseDateError(date)) {
    const { message } = date;
    return {
      type: "DocumentParseError",
      message:
        `unable to parse date "${dateStr}" ` +
        `using format "${dateFormat}": ${message}`,
    };
  }

  return date;
}
