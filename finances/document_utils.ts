import { isDocumentParseError, type DocumentParseError } from "./document.ts";
import { parseDateToYYYYMMDD, isParseDateError } from "./date.ts";

interface StringFromLinesOptions {
  resultTransform: (matchingString: string) => string | DocumentParseError;
}

export function stringFromPdf(
  pdf: string,
  regex: RegExp,
  options?: Partial<StringFromLinesOptions>,
): string | DocumentParseError {
  const match = pdf.match(regex);
  if (!match) {
    return {
      type: "DocumentParseError",
      message: `regular expression was not matched: ${regex.source}`,
    };
  }

  const matchingString = match[1];
  if (typeof matchingString === "undefined") {
    throw new Error(
      `internal error stdp7xw6rb: regex should have had a matching group: ` +
        regex.source,
    );
  }

  const resultTransform = options?.resultTransform;
  if (typeof resultTransform !== "undefined") {
    return resultTransform(matchingString);
  } else {
    return matchingString;
  }
}

export function yyyymmddDateFromPdf(
  pdf: string,
  regex: RegExp,
  dateFormat: string,
  options?: Partial<StringFromLinesOptions>,
): string | DocumentParseError {
  const dateStr = stringFromPdf(pdf, regex, options);
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
