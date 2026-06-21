export function messageForError(e: unknown): string {
  const code = propertyFromUnknown(e, "code");
  const message = propertyFromUnknown(e, "message");
  if (code === "ENOENT") {
    return "file not found";
  } else if (code === "EACCES") {
    return "insufficient permissions to read file";
  } else if (typeof message === "string" && message.trim().length > 0) {
    return message.trim();
  } else {
    return `unknown error (${Bun.inspect(e)})`;
  }
}

function propertyFromUnknown(obj: unknown, propertyName: string): unknown {
  return typeof obj === "object" && obj !== null && propertyName in obj
    ? (obj as Record<string, unknown>)[propertyName]
    : undefined;
}
