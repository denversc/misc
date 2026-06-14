import * as fs from 'fs';
import { PDFParse } from 'pdf-parse';

async function main() {
  // Bun.argv contains: [bunExecutable, scriptPath, ...arguments]
  const filePath = Bun.argv[2];

  if (!filePath) {
    console.error("Error: Please provide the path to a PDF file.");
    console.error("Usage: bun run index.ts <path-to-pdf-file>");
    process.exit(1);
  }

  if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found at path "${filePath}"`);
    process.exit(1);
  }

  try {
    const dataBuffer = fs.readFileSync(filePath);
    const parser = new PDFParse({ data: dataBuffer });
    const result = await parser.getText();
    console.log(result.text);
    await parser.destroy();
  } catch (error) {
    console.error("Error reading or parsing PDF file:", error);
    process.exit(1);
  }
}

main();