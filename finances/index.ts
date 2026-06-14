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

program
  .name('pdf-to-text')
  .description('CLI to extract text from PDF files')
  .version('1.0.0')
  .argument('<file-path>', 'path to the PDF file')
  .action(parsePdfAndPrint);

program.parse(process.argv);