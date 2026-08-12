#!/usr/bin/env node
/**
 * Render a single Mermaid diagram to a standalone SVG using mermaid-cli
 * (real Chrome via Puppeteer — not the jsdom shim used by mermaid_validate's
 * syntax checker, which doesn't do real text layout and can't be trusted for
 * actual visual output).
 *
 * Usage: node render.mjs INPUT.mmd OUTPUT.svg
 * Exit code: 0 on success, 1 on failure (missing deps, no usable Chrome
 * found, or mermaid-cli itself failing) — always with a clear stderr reason,
 * since the caller (chat_report.py) treats failure as "fall back to the
 * live mermaid fence," not a hard error.
 *
 * Chrome discovery: mermaid-cli's own bundled Puppeteer Chrome has been
 * observed to fail to launch on ARM64 (exec format error from
 * chrome-headless-shell) — this looks for a system-installed Chrome/Chromium
 * first and only falls back to Puppeteer's bundled browser if none is found.
 * Honors PUPPETEER_EXECUTABLE_PATH if the caller has already set it.
 */
import { execFileSync, execFile } from "node:child_process";
import { writeFileSync, unlinkSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import os from "node:os";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CANDIDATE_BROWSERS = [
  "google-chrome-stable",
  "google-chrome",
  "chromium-browser",
  "chromium",
  "chrome",
];

function findSystemChrome() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }
  for (const name of CANDIDATE_BROWSERS) {
    try {
      const found = execFileSync("which", [name], { encoding: "utf8" }).trim();
      if (found) return found;
    } catch {
      // not found under this name, try the next
    }
  }
  return null;
}

function findMmdc() {
  const local = path.join(__dirname, "node_modules", ".bin", "mmdc");
  if (existsSync(local)) return local;
  return null;
}

const [, , input, output] = process.argv;
if (!input || !output) {
  console.error("Usage: node render.mjs INPUT.mmd OUTPUT.svg");
  process.exit(2);
}

const mmdc = findMmdc();
if (!mmdc) {
  console.error(
    `mermaid-cli not installed — run 'npm install' in ${__dirname} first.`
  );
  process.exit(1);
}

const args = ["-i", input, "-o", output, "-q"];

const chromePath = findSystemChrome();
let puppeteerConfigPath = null;
if (chromePath) {
  puppeteerConfigPath = path.join(os.tmpdir(), `mmdc-puppeteer-${process.pid}.json`);
  writeFileSync(
    puppeteerConfigPath,
    JSON.stringify({ executablePath: chromePath, args: ["--no-sandbox", "--disable-dev-shm-usage"] })
  );
  args.push("-p", puppeteerConfigPath);
} else {
  console.error(
    "No system Chrome/Chromium found (checked: " + CANDIDATE_BROWSERS.join(", ") +
    ", and PUPPETEER_EXECUTABLE_PATH) — falling back to mermaid-cli's bundled " +
    "browser, which has been unreliable on some platforms (e.g. ARM64)."
  );
}

execFile(mmdc, args, (err, stdout, stderr) => {
  if (puppeteerConfigPath) {
    try { unlinkSync(puppeteerConfigPath); } catch {}
  }
  if (err) {
    console.error(`mermaid-cli render failed: ${err.message}`);
    if (stderr) console.error(stderr);
    process.exit(1);
  }
  console.log(`Wrote ${output}`);
});
