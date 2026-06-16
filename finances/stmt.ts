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

async function printCommand(filePath: string | string[]): Promise<void> {
  if (Array.isArray(filePath)) {
    for (const currentFilePath of filePath) {
      await printCommand(currentFilePath);
    }
    return;
  }

  if (!(await fs.exists(filePath))) {
    console.error(`Error: File not found: ${filePath}`);
    process.exit(1);
  }

  const text = await readPdf(filePath);
  console.log(text);
}

type PdfType = "PublicMobileStatement";

function identify(pdfText: string): PdfType | undefined {
  const lines = pdfText.split("\n").filter((line) => line.trim());
  if (lines.includes("Public Mobile Account")) {
    return "PublicMobileStatement";
  }
  return undefined;
}

async function identifyCommand(filePath: string | string[]): Promise<void> {
  if (Array.isArray(filePath)) {
    for (const currentFilePath of filePath) {
      await identifyCommand(currentFilePath);
    }
    return;
  }

  if (!(await fs.exists(filePath))) {
    console.error(`Error: File not found: ${filePath}`);
    process.exit(1);
  }

  const text = await readPdf(filePath);
  const type = identify(text);
  console.log(type);
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
  .description("Reads PDF files and prints their text to stdout")
  .argument("<file...>", "path of the PDF file")
  .action(printCommand);

program
  .command("identify")
  .description("Reads PDF files and prints their types to stdout")
  .argument("<files...>", "path of the PDF file")
  .action(identifyCommand);

program.parse(process.argv);
