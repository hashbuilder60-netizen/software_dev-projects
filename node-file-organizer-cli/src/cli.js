#!/usr/bin/env node
import { organize } from "./organize.js";

const args = process.argv.slice(2);
const getArg = (name, fallback = undefined) => {
  const idx = args.indexOf(name);
  return idx >= 0 ? args[idx + 1] : fallback;
};

const targetPath = getArg("--path", ".");
const dryRun = args.includes("--dry-run");

const moves = organize(targetPath, dryRun);
if (moves.length === 0) {
  console.log("No files to organize.");
  process.exit(0);
}

for (const move of moves) {
  console.log(`${dryRun ? "[dry-run] " : ""}${move.source} -> ${move.destination}`);
}