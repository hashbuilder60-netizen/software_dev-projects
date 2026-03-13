import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { organize } from "../src/organize.js";

test("organize returns planned moves in dry-run mode", () => {
  const root = mkdtempSync(join(tmpdir(), "organizer-"));
  writeFileSync(join(root, "a.txt"), "A");
  writeFileSync(join(root, "b.md"), "B");

  const moves = organize(root, true);
  assert.equal(moves.length, 2);
  const names = readdirSync(root);
  assert.ok(names.includes("a.txt"));
  assert.ok(names.includes("b.md"));
});