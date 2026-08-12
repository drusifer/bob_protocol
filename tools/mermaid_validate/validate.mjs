#!/usr/bin/env node
/**
 * Validate every ```mermaid fenced block in the given .md file(s) by running
 * them through mermaid's real parser (not a hand-rolled character check).
 *
 * Usage: node validate.mjs FILE.md [FILE.md ...]
 * Exit code: 0 if every fenced block in every file parses, 1 otherwise.
 *
 * Runs mermaid.parse() (syntax check only, no render) under a minimal jsdom
 * shim instead of a real browser — mermaid.js expects `window`/`document` to
 * exist even for parsing, but full rendering (which needs a real browser via
 * Puppeteer) is unnecessary for syntax validation and is far less portable
 * (Puppeteer's bundled Chrome has had launch failures on ARM64 in testing).
 */
import fs from "node:fs";
import { JSDOM } from "jsdom";

const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>", { url: "http://localhost" });
global.window = dom.window;
global.document = dom.window.document;
global.SVGElement = dom.window.SVGElement;
Object.defineProperty(global, "navigator", { value: dom.window.navigator, configurable: true });

const mermaid = (await import("mermaid")).default;
mermaid.initialize({ startOnLoad: false });

const FENCE_RE = /```mermaid\n([\s\S]*?)\n```/g;

function extractFences(mdText) {
  const blocks = [];
  let m;
  while ((m = FENCE_RE.exec(mdText)) !== null) {
    blocks.push(m[1]);
  }
  return blocks;
}

async function validateFile(path) {
  const text = fs.readFileSync(path, "utf8");
  const blocks = extractFences(text);
  if (blocks.length === 0) {
    console.log(`SKIP  ${path} (no \`\`\`mermaid fence found)`);
    return true;
  }
  let ok = true;
  for (let i = 0; i < blocks.length; i++) {
    const label = blocks.length > 1 ? `${path} [block ${i + 1}/${blocks.length}]` : path;
    try {
      await mermaid.parse(blocks[i]);
      console.log(`PASS  ${label}`);
    } catch (e) {
      ok = false;
      console.log(`FAIL  ${label}`);
      console.log(
        e.message
          .split("\n")
          .map((l) => `      ${l}`)
          .join("\n")
      );
    }
  }
  return ok;
}

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error("Usage: node validate.mjs FILE.md [FILE.md ...]");
  process.exit(2);
}

let allOk = true;
for (const f of files) {
  const ok = await validateFile(f);
  allOk = allOk && ok;
}
process.exit(allOk ? 0 : 1);
