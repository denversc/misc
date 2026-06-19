export function unreachable(value: never, message: string): never {
  throw new Error(`should never get here: ${message} (${Bun.inspect(value)})`);
}
