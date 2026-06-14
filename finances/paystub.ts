/* eslint-disable @typescript-eslint/no-unused-vars */
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

const MONTH_MAP: Record<string, string> = {
  jan: "01",
  feb: "02",
  mar: "03",
  apr: "04",
  may: "05",
  jun: "06",
  jul: "07",
  aug: "08",
  sep: "09",
  oct: "10",
  nov: "11",
  dec: "12",
};

export type Classification = "regpay" | "gsu" | "shuttle" | "meal";

async function classify(filePath: string): Promise<Classification> {
  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  await parser.destroy();

  // Split on "Deductions" to only process the Earnings section
  const parts = result.text.split(/\r?\nDeductions/);
  const earningsSection = parts[0] || result.text;

  const mealMatches = earningsSection.matchAll(
    /Meal Bene[fi\s]+t\s+(?:([\d.]+)\s+\$([\d.]+)\s+)?\$([\d,.]+)\s+\$([\d,.]+)/gi,
  );
  for (const match of mealMatches) {
    if (match[3]) {
      const currentVal = parseFloat(match[3].replace(/,/g, ""));
      if (currentVal > 0) {
        return "meal";
      }
    }
  }

  const shuttleMatch = earningsSection.match(
    /CA Shuttle Bus\s+(?:([\d.]+)\s+\$([\d.]+)\s+)?\$([\d,.]+)\s+\$([\d,.]+)/i,
  );
  if (shuttleMatch && shuttleMatch[3]) {
    const currentVal = parseFloat(shuttleMatch[3].replace(/,/g, ""));
    if (currentVal > 0) {
      return "shuttle";
    }
  }

  const gsuMatch = earningsSection.match(
    /Google Stock Un\s+([\d,.]+)\s+\$([\d,.]+)\s+\$([\d,.]+)\s+\$([\d,.]+)/i,
  );
  if (gsuMatch && gsuMatch[3]) {
    const currentVal = parseFloat(gsuMatch[3].replace(/,/g, ""));
    if (currentVal > 0) {
      return "gsu";
    }
  }

  const regPayMatch = earningsSection.match(
    /Regular Pay\s+([\d,.]+)\s+\$([\d,.]+)\s+\$([\d,.]+)\s+\$([\d,.]+)/i,
  );
  if (regPayMatch && regPayMatch[3]) {
    const currentVal = parseFloat(regPayMatch[3].replace(/,/g, ""));
    if (currentVal > 0) {
      return "regpay";
    }
  }

  throw new Error("Unable to determine pay stub classification");
}

async function classifyCommand(filePath: string): Promise<void> {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  try {
    const classification = await classify(filePath);
    console.log(classification);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Error: ${message}`);
    process.exit(1);
  }
}

async function extractInfoFromPdf(filePath: string): Promise<void> {}

async function parsePdfAndExtractInfo(filePath: string): Promise<void> {}

function getNewFilename(parsed: void): string {
  return "";
}

async function generateFilenames(filePaths: string[]): Promise<void> {}

async function renameFiles(filePaths: string[]): Promise<void> {}

program
  .name("mspdf")
  .description(
    'Reads a "Pay Stub" PDF and extracts ' +
      "information from it relevant for income tax reporting",
  )
  .version("1.0.0");

program
  .command("classify")
  .description("determine what kind of pay stub the given file is")
  .argument("<file-path>", "path to the PDF file")
  .action(classifyCommand);

program
  .command("print")
  .description("load a PDF and print its text to stdout")
  .argument("<file-path>", "path to the PDF file")
  .action(parsePdfAndPrint);

program
  .command("parse")
  .description(
    "extract tax reporting information from the PDF file and print it",
  )
  .argument("<file-path>", "path to the PDF file")
  .action(parsePdfAndExtractInfo);

program
  .command("filename")
  .description("generate standardized filenames from the PDF data")
  .argument("<file-paths...>", "paths to the PDF files")
  .action(generateFilenames);

program
  .command("rename")
  .description(
    "rename the PDF files to standardized filenames based on their content",
  )
  .argument("<file-paths...>", "paths to the PDF files")
  .action(renameFiles);

program.parse(process.argv);
