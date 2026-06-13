// Generates placeholder app icons so the Tauri build works out of the box.
// Draws a simple orange ring on a dark tile (a stand-in for the Crucible flame).
// For polished release icons, replace these with: `npm run tauri icon path/to/logo.png`.

import { deflateSync, crc32 } from "node:zlib";
import { writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = join(here, "..", "src-tauri", "icons");
mkdirSync(outDir, { recursive: true });

function crcChunk(type, data) {
  const body = Buffer.concat([Buffer.from(type, "ascii"), data]);
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body) >>> 0, 0);
  return Buffer.concat([len, body, crc]);
}

function makePng(size) {
  const w = size;
  const h = size;
  const raw = Buffer.alloc((w * 4 + 1) * h);
  const cx = (w - 1) / 2;
  const cy = (h - 1) / 2;
  const rOuter = w * 0.34;
  const rInner = w * 0.17;
  for (let y = 0; y < h; y++) {
    const rowStart = y * (w * 4 + 1);
    raw[rowStart] = 0; // filter type: None
    for (let x = 0; x < w; x++) {
      const o = rowStart + 1 + x * 4;
      let r = 0x0b;
      let g = 0x0b;
      let b = 0x0f; // dark background
      const dx = x - cx;
      const dy = y - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist <= rOuter) {
        r = 0xff;
        g = 0x5a;
        b = 0x1f; // orange disc
      }
      if (dist <= rInner) {
        r = 0x0b;
        g = 0x0b;
        b = 0x0f; // punch out center -> ring
      }
      raw[o] = r;
      raw[o + 1] = g;
      raw[o + 2] = b;
      raw[o + 3] = 0xff;
    }
  }
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type: RGBA
  const idat = deflateSync(raw, { level: 9 });
  return Buffer.concat([
    sig,
    crcChunk("IHDR", ihdr),
    crcChunk("IDAT", idat),
    crcChunk("IEND", Buffer.alloc(0)),
  ]);
}

const targets = { "32x32.png": 32, "128x128.png": 128, "128x128@2x.png": 256, "icon.png": 512 };
for (const [name, size] of Object.entries(targets)) {
  writeFileSync(join(outDir, name), makePng(size));
  console.log(`icon: ${name} (${size}x${size})`);
}
