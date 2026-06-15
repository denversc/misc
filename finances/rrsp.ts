import * as fs from "fs";
import * as path from "path";
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

function formatDate(
  monthStrRaw: string,
  dayStr: string,
  yearStr: string,
): string {
  const day = dayStr.padStart(2, "0");
  const monthKey = monthStrRaw.toLowerCase().substring(0, 3);
  const month = MONTH_MAP[monthKey];
  if (!month) {
    throw new Error(`Invalid month name in date: "${monthStrRaw}"`);
  }
  return `${yearStr}-${month}-${day}`;
}

interface ParsedRrsp {
  lastDate: string;
  value: string;
}

async function extractInfoFromPdf(filePath: string): Promise<ParsedRrsp> {
  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  await parser.destroy();

  const balanceMatch = result.text.match(
    /([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\s+Balance\s+([\d,.]+)/i,
  );

  if (balanceMatch) {
    const formattedDate = formatDate(
      balanceMatch[1]!,
      balanceMatch[2]!,
      balanceMatch[3]!,
    );
    return {
      lastDate: formattedDate,
      value: balanceMatch[4]!.trim(),
    };
  } else {
    throw new Error("Failed to parse PDF. Missing Balance line.");
  }
}

async function parsePdfAndExtractInfo(filePath: string): Promise<void> {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  try {
    const parsed = await extractInfoFromPdf(filePath);
    console.log(`Last Date: ${parsed.lastDate}`);
    console.log(`Value: ${parsed.value}`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Error: ${message}`);
    process.exit(1);
  }
}

function getNewFilename(parsed: ParsedRrsp): string {
  const yearMonth = parsed.lastDate.substring(0, 7); // "YYYY-MM"
  return `${yearMonth} Manulife RRSP Google Transactions ($${parsed.value})`;
}

async function generateFilenames(filePaths: string[]): Promise<void> {
  for (const filePath of filePaths) {
    if (!fs.existsSync(filePath)) {
      console.error(`Error: File not found at path "${filePath}"`);
      process.exit(1);
    }

    const parsed = await extractInfoFromPdf(filePath);
    const filename = getNewFilename(parsed);
    console.log(filename);
  }
}

async function renameFiles(filePaths: string[]): Promise<void> {
  for (const filePath of filePaths) {
    if (!fs.existsSync(filePath)) {
      console.error(`Error: File not found at path "${filePath}"`);
      process.exit(1);
    }

    const parsed = await extractInfoFromPdf(filePath);
    const baseNewName = getNewFilename(parsed);

    const dir = path.dirname(filePath);
    const ext = path.extname(filePath);
    const newFilename = `${baseNewName}${ext}`;
    const newPath = path.join(dir, newFilename);

    console.log(`Renaming ${filePath} to ${newFilename}`);
    fs.renameSync(filePath, newPath);
  }
}

program
  .name("rrsp")
  .description(
    "Reads a Manulife RRSP statement PDF and extracts " +
      "information from it relevant for financial record keeping",
  )
  .version("1.0.0");

program
  .command("print")
  .description("load a PDF and print its text to stdout")
  .argument("<file-path>", "path to the PDF file")
  .action(parsePdfAndPrint);

program
  .command("parse")
  .description(
    "extract RRSP summary information from the PDF file and print it",
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
