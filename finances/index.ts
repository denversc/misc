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

async function parsePdfAndExtractAwardId(filePath: string): Promise<void> {
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const result = await parser.getText();
  
  const match = result.text.match(/Award ID:\s*([^\r\n]+)/i);
  if (match) {
    console.log(match[1].trim());
  } else {
    console.error("Error: Could not find Award ID in the PDF.");
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
  .description('extract the Award ID from the PDF file and print it')
  .argument('<file-path>', 'path to the PDF file')
  .action(parsePdfAndExtractAwardId);

program.parse(process.argv);