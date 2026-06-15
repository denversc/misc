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

interface ParsedGasBill {
  preAuthorizedWithdrawal: string;
  issueDate: string;
}

async function extractInfoFromPdf(filePath: string): Promise<ParsedGasBill> {
  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  await parser.destroy();

  const withdrawalMatch = result.text.match(
    /Pre-authorized Withdrawal:\s*([\d.]+)/i,
  );
  const issueDateMatch = result.text.match(
    /Issue Date:\s*([A-Za-z]+)\s*(\d{1,2})\s*(\d{4})/i,
  );

  if (withdrawalMatch && issueDateMatch) {
    const formattedDate = formatDate(
      issueDateMatch[1]!,
      issueDateMatch[2]!,
      issueDateMatch[3]!,
    );
    return {
      preAuthorizedWithdrawal: `$${parseFloat(withdrawalMatch[1]!).toFixed(2)}`,
      issueDate: formattedDate,
    };
  } else {
    const missingFields: string[] = [];
    if (!withdrawalMatch) missingFields.push("Pre-authorized Withdrawal");
    if (!issueDateMatch) missingFields.push("Issue Date");
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

  console.log(`Pre-authorized Withdrawal: ${parsed.preAuthorizedWithdrawal}`);
  console.log(`Issue Date: ${parsed.issueDate}`);
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

program
  .command("parse")
  .description(
    "extract financial record information from the PDF file and print it",
  )
  .argument("<file-path>", "path to the PDF file")
  .action(parsePdfAndExtractInfo);

program.parse(process.argv);
