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

function formatDate(dateStr: string): string {
  const parts = dateStr.split("-");
  if (parts.length !== 3) {
    throw new Error(`Invalid date format (expected DD-MMM-YYYY): "${dateStr}"`);
  }
  const [dayStr, monthStrRaw, yearStr] = parts as [string, string, string];
  const day = dayStr.padStart(2, "0");
  const monthStr = monthStrRaw.toLowerCase();
  const year = yearStr;

  const month = MONTH_MAP[monthStr];
  if (!month) {
    throw new Error(`Invalid month name in date: "${dateStr}"`);
  }

  return `${year}-${month}-${day}`;
}

interface ParsedPdf {
  awardId: string;
  settlementDate: string;
  vestedValue: string;
  saleAmount: string;
  sharesSold: string;
  salePrice: string;
}

async function extractInfoFromPdf(filePath: string): Promise<ParsedPdf> {
  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  await parser.destroy();

  const awardIdMatch = result.text.match(/Award ID:\s*([^\r\n]+)/i);
  const settlementDateMatch = result.text.match(
    /Settlement Date:\s*([^\r\n]+)/i,
  );
  const vestedValueMatch = result.text.match(
    /Total Gain \(FMV x Quantity Released\):\s*([^\r\n]+)/i,
  );
  const saleAmountMatch = result.text.match(
    /Sale PricexQuantity Sold:\s*\(?([^)\r\n]+)\)?/i,
  );
  const sharesSoldMatch = result.text.match(/Quantity Sold:\s*\(?([\d.]+)\)?/i);
  const salePriceMatch = result.text.match(/shares at \$([\d.]+) per share/i);

  if (
    awardIdMatch &&
    settlementDateMatch &&
    vestedValueMatch &&
    saleAmountMatch &&
    sharesSoldMatch &&
    salePriceMatch
  ) {
    const rawSettlementDate = settlementDateMatch[1]!.trim();
    const formattedSettlementDate = formatDate(rawSettlementDate);
    const formattedSalePrice = parseFloat(salePriceMatch[1]!).toFixed(4);

    return {
      awardId: awardIdMatch[1]!.trim(),
      settlementDate: formattedSettlementDate,
      vestedValue: vestedValueMatch[1]!.trim(),
      saleAmount: saleAmountMatch[1]!.trim(),
      sharesSold: sharesSoldMatch[1]!.trim(),
      salePrice: `$${formattedSalePrice}`,
    };
  } else {
    const missingFields: string[] = [];
    if (!awardIdMatch) missingFields.push("Award ID");
    if (!settlementDateMatch) missingFields.push("Settlement Date");
    if (!vestedValueMatch) missingFields.push("Vested Value");
    if (!saleAmountMatch) missingFields.push("Sale Amount");
    if (!sharesSoldMatch) missingFields.push("Shares Sold");
    if (!salePriceMatch) missingFields.push("Sale Price");
    throw new Error(
      `Failed to parse PDF. Missing fields: ${missingFields.join(", ")}`,
    );
  }
}

async function parsePdfAndExtractInfo(filePath: string): Promise<void> {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  const parsed = await extractInfoFromPdf(filePath);

  console.log(`Award ID: ${parsed.awardId}`);
  console.log(`Settlement Date: ${parsed.settlementDate}`);
  console.log(`Vested Value: ${parsed.vestedValue}`);
  console.log(`Sale Amount: ${parsed.saleAmount}`);
  console.log(`Shares Sold: ${parsed.sharesSold}`);
  console.log(`Sale Price: ${parsed.salePrice}`);
}

function getNewFilename(parsed: ParsedPdf): string {
  return (
    `${parsed.settlementDate} Morgan Stanley Release Confirmation ` +
    `${parsed.awardId} ${parsed.sharesSold} shares vested for ` +
    `${parsed.vestedValue} sold for ${parsed.saleAmount} ` +
    `(${parsed.salePrice} per share)`
  );
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
  .name("mspdf")
  .description(
    'Reads a "Release Confirmation" PDF from Morgan Stanley and extracts ' +
      "information from it relevant for income tax reporting",
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
