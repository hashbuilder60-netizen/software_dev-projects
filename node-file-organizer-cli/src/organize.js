import { mkdirSync, renameSync, readdirSync, statSync } from "node:fs";
import { extname, join, resolve } from "node:path";

export function organize(targetPath, dryRun = false) {
  const absolute = resolve(targetPath);
  const entries = readdirSync(absolute);
  const moves = [];

  for (const name of entries) {
    const source = join(absolute, name);
    if (!statSync(source).isFile()) {
      continue;
    }
    const ext = extname(name).toLowerCase().replace(".", "") || "no-extension";
    const folder = join(absolute, ext);
    const destination = join(folder, name);

    moves.push({ source, destination, folder });
    if (!dryRun) {
      mkdirSync(folder, { recursive: true });
      renameSync(source, destination);
    }
  }

  return moves;
}