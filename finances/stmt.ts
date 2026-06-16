import * as fs from "node:fs/promises";
import { Command } from "commander";
import { PDFParse } from "pdf-parse";

const program = new Command();

async function readPdf(filePath: string): Promise<string> {
  const fileContents = await fs.readFile(filePath);
  const parser = new PDFParse({ data: fileContents });
  try {
    const textContents = await parser.getText();
    return textContents.text;
  } finally {
    await parser.destroy();
  }
}

async function printCommand(filePath: string): Promise<void> {
  if (!(await fs.exists(filePath))) {
    console.error(`Error: File not found: ${filePath}`);
    process.exit(1);
  }

  const text = await readPdf(filePath);
  console.log(text);
}

program
  .name("stmt")
  .description(
    "Reads PDF file and extracts information " +
      "relevant for financial record keeping",
  )
  .version("1.0.0");

program
  .command("print")
  .description("Reads a PDF file and prints its text to stdout")
  .argument("<file>", "path of the PDF file")
  .action(printCommand);

program.parse(process.argv);
