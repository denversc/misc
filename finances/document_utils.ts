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
  const line = lines.find((line) => regex.test(line));
  if (!line) {
    return {
      type: "DocumentParseError",
      message: `line not found matching regex: ${regex.source}`,
    };
  }

  const matchingString = line.match(regex)?.[1];
  if (!matchingString) {
    throw new Error(
      `internal error stdp7xw6rb: regex should have matched line; ` +
        `regex=${regex.source}, line=${line}`,
    );
  }

  return matchingStringWithStringFromLinesOptionsApplied(
    matchingString,
    options,
  );
}

function matchingStringWithStringFromLinesOptionsApplied(
  matchingString: string,
  options: Partial<StringFromLinesOptions> | undefined,
): string {
  const resultPrefix = options?.resultPrefix;
  if (typeof resultPrefix === "undefined") {
    return matchingString;
  }
  return resultPrefix + matchingString;
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
