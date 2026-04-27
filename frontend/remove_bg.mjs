import { removeBackground } from '@imgly/background-removal-node';
import fs from 'fs';

async function processImage() {
  console.log("Starting background removal...");
  try {
    const blob = await removeBackground('/Users/youssefbenmoussa/Desktop/Law_IA/frontend/public/lawyer_avatar.png');
    const buffer = Buffer.from(await blob.arrayBuffer());
    fs.writeFileSync('/Users/youssefbenmoussa/Desktop/Law_IA/frontend/public/lawyer_avatar_transparent.png', buffer);
    console.log("Image processed and saved successfully!");
  } catch (error) {
    console.error("Error processing image:", error);
  }
}

processImage();
