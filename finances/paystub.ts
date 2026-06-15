/* eslint-disable @typescript-eslint/no-unused-vars */
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

export type Classification = "regpay" | "gsu" | "shuttle" | "meal";

function classifyText(text: string): Classification {
  // Split on "Deductions" to only process the Earnings section
  const parts = text.split(/\r?\nDeductions/);
  const earningsSection = parts[0] || text;

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

async function classify(filePath: string): Promise<Classification> {
  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  await parser.destroy();

  return classifyText(result.text);
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

export interface ParsedPaystub {
  payDate: string;
  classification: Classification;
  gsuAmount?: string;
}

async function extractInfoFromPdf(filePath: string): Promise<ParsedPaystub> {
  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  await parser.destroy();

  const payDateMatch = result.text.match(
    /Pay Date\s+(\d{4})\s+(\d{2})\s+(\d{2})/i,
  );
  if (!payDateMatch) {
    throw new Error("Failed to parse PDF. Missing field: Pay Date");
  }

  const [, year, month, day] = payDateMatch as [string, string, string, string];
  const payDate = `${year}-${month}-${day}`;
  const classification = classifyText(result.text);

  let gsuAmount: string | undefined;
  if (classification === "gsu") {
    // Split on "Deductions" to only process the Earnings section
    const parts = result.text.split(/\r?\nDeductions/);
    const earningsSection = parts[0] || result.text;
    const gsuMatch = earningsSection.match(
      /Google Stock Un\s+([\d,.]+)\s+\$([\d,.]+)\s+\$([\d,.]+)\s+\$([\d,.]+)/i,
    );
    if (gsuMatch && gsuMatch[3]) {
      gsuAmount = `$${gsuMatch[3]}`;
    }
  }

  return {
    payDate,
    classification,
    gsuAmount,
  };
}

async function parsePdfAndExtractInfo(filePath: string): Promise<void> {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  try {
    const parsed = await extractInfoFromPdf(filePath);
    console.log(`Pay Date: ${parsed.payDate}`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Error: ${message}`);
    process.exit(1);
  }
}

function getNewFilename(parsed: ParsedPaystub): string {
  if (parsed.classification === "gsu") {
    return `${parsed.payDate} Google Pay Stub (GSU Vest ${parsed.gsuAmount} CAD)`;
  }
  const suffixMap: Record<Exclude<Classification, "gsu">, string> = {
    regpay: "Regular Pay",
    shuttle: "Shuttle Bus",
    meal: "Meal Benefit",
  };
  const suffix = suffixMap[parsed.classification];
  return `${parsed.payDate} Google Pay Stub (${suffix})`;
}

async function generateFilenames(filePaths: string[]): Promise<void> {
  for (const filePath of filePaths) {
    if (!fs.existsSync(filePath)) {
      console.error(`Error: File not found at path "${filePath}"`);
      process.exit(1);
    }

    try {
      const parsed = await extractInfoFromPdf(filePath);
      const ext = path.extname(filePath);
      const filename = `${getNewFilename(parsed)}${ext}`;
      console.log(filename);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`Error: ${message}`);
      process.exit(1);
    }
  }
}

interface ProposedRename {
  filePath: string;
  parsed: ParsedPaystub;
  dir: string;
  ext: string;
  baseNewName: string;
}

function disambiguateFilenames(
  proposed: ProposedRename[],
): Map<string, string> {
  const groups = new Map<string, ProposedRename[]>();

  for (const item of proposed) {
    const targetPath = path.join(item.dir, `${item.baseNewName}${item.ext}`);
    const list = groups.get(targetPath) || [];
    list.push(item);
    groups.set(targetPath, list);
  }

  const result = new Map<string, string>();

  for (const [targetPath, list] of groups.entries()) {
    if (list.length === 1) {
      result.set(list[0]!.filePath, targetPath);
    } else {
      list.forEach((item, index) => {
        const counter = index + 1;
        let baseNewName = item.baseNewName;
        if (baseNewName.endsWith(")")) {
          baseNewName = `${baseNewName.slice(0, -1)} ${counter})`;
        } else {
          baseNewName = `${baseNewName} ${counter}`;
        }
        const newPath = path.join(item.dir, `${baseNewName}${item.ext}`);
        result.set(item.filePath, newPath);
      });
    }
  }

  return result;
}

async function renameFiles(filePaths: string[]): Promise<void> {
  const uniqueFilePaths = Array.from(new Set(filePaths));
  const proposedRenames: ProposedRename[] = [];

  for (const filePath of uniqueFilePaths) {
    if (!fs.existsSync(filePath)) {
      console.error(`Error: File not found at path "${filePath}"`);
      process.exit(1);
    }

    try {
      const parsed = await extractInfoFromPdf(filePath);
      const baseNewName = getNewFilename(parsed);
      const dir = path.dirname(filePath);
      const ext = path.extname(filePath);

      proposedRenames.push({
        filePath,
        parsed,
        dir,
        ext,
        baseNewName,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`Error: ${message}`);
      process.exit(1);
    }
  }

  const disambiguated = disambiguateFilenames(proposedRenames);

  for (const item of proposedRenames) {
    const newPath = disambiguated.get(item.filePath)!;
    const newFilename = path.basename(newPath);

    try {
      console.log(`Renaming ${item.filePath} to ${newFilename}`);
      fs.renameSync(item.filePath, newPath);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`Error: ${message}`);
      process.exit(1);
    }
  }
}

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
