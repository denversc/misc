import * as fs from 'fs';
import { Command } from 'commander';
import { PDFParse } from 'pdf-parse';

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
  jan: '01', feb: '02', mar: '03', apr: '04', may: '05', jun: '06',
  jul: '07', aug: '08', sep: '09', oct: '10', nov: '11', dec: '12'
};

function formatDate(dateStr: string): string {
  const parts = dateStr.split('-');
  if (parts.length !== 3) {
    throw new Error(`Invalid date format (expected DD-MMM-YYYY): "${dateStr}"`);
  }
  const day = parts[0].padStart(2, '0');
  const monthStr = parts[1].toLowerCase();
  const year = parts[2];
  
  const month = MONTH_MAP[monthStr];
  if (!month) {
    throw new Error(`Invalid month name in date: "${dateStr}"`);
  }
  
  return `${year}-${month}-${day}`;
}

async function parsePdfAndExtractInfo(filePath: string): Promise<void> {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  
  const awardIdMatch = result.text.match(/Award ID:\s*([^\r\n]+)/i);
  const settlementDateMatch = result.text.match(/Settlement Date:\s*([^\r\n]+)/i);
  const vestedValueMatch = result.text.match(/Total Gain \(FMV x Quantity Released\):\s*([^\r\n]+)/i);
  const saleAmountMatch = result.text.match(/Sale PricexQuantity Sold:\s*\(?([^\)\r\n]+)\)?/i);
  const sharesSoldMatch = result.text.match(/Quantity Sold:\s*\(?([\d\.]+)\)?/i);
  const salePriceMatch = result.text.match(/shares at \$([\d\.]+) per share/i);

  if (awardIdMatch && settlementDateMatch && vestedValueMatch && saleAmountMatch && sharesSoldMatch && salePriceMatch) {
    const rawSettlementDate = settlementDateMatch[1].trim();
    const formattedSettlementDate = formatDate(rawSettlementDate);
    const formattedSalePrice = parseFloat(salePriceMatch[1]).toFixed(4);
    
    console.log(`Award ID: ${awardIdMatch[1].trim()}`);
    console.log(`Settlement Date: ${formattedSettlementDate}`);
    console.log(`Vested Value: ${vestedValueMatch[1].trim()}`);
    console.log(`Sale Amount: ${saleAmountMatch[1].trim()}`);
    console.log(`Shares Sold: ${sharesSoldMatch[1].trim()}`);
    console.log(`Sale Price: $${formattedSalePrice}`);
  } else {
    if (!awardIdMatch) {
      console.error("Error: Could not find Award ID in the PDF.");
    }
    if (!settlementDateMatch) {
      console.error("Error: Could not find Settlement Date in the PDF.");
    }
    if (!vestedValueMatch) {
      console.error("Error: Could not find Vested Value in the PDF.");
    }
    if (!saleAmountMatch) {
      console.error("Error: Could not find Sale Amount in the PDF.");
    }
    if (!sharesSoldMatch) {
      console.error("Error: Could not find Shares Sold in the PDF.");
    }
    if (!salePriceMatch) {
      console.error("Error: Could not find Sale Price in the PDF.");
    }
    process.exit(1);
  }
  
  await parser.destroy();
}

program
  .name('pdf-to-text')
  .description('CLI to extract text and info from PDF files')
  .version('1.0.0');

program
  .command('print')
  .description('load a PDF and print its text to stdout')
  .argument('<file-path>', 'path to the PDF file')
  .action(parsePdfAndPrint);

program
  .command('parse')
  .description('extract the Award ID and Settlement Date from the PDF file and print them')
  .argument('<file-path>', 'path to the PDF file')
  .action(parsePdfAndExtractInfo);

program.parse(process.argv);