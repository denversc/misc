import * as fs from "fs";
import { Command } from "commander";
import { PDFParse } from "pdf-parse";

const program = new Command();

async function parsePdfAndPrint(filePath: string): Promise<void> {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  console.log(result.text);
  await parser.destroy();
}

program
  .name("gasbill")
  .description(
    "Reads a Kitchener Utilities gas bill PDF and extracts " +
      "information from it relevant for financial record keeping",
  )
  .version("1.0.0");

program
  .command("print")
  .description("load a PDF and print its text to stdout")
  .argument("<file-path>", "path to the PDF file")
  .action(parsePdfAndPrint);

program.parse(process.argv);
