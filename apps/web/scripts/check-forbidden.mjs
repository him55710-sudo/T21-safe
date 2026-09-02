import { readdir, readFile } from "node:fs/promises";
import { extname, join } from "node:path";

const outputRoot = join(process.cwd(), ".next");
const phrases = [
  ["reduce", "propofol"].join(" "),
  ["administer", "atropine"].join(" "),
  ["safe", "to", "proceed"].join(" "),
  ["clinical", "diagnosis"].join(" "),
  ["dosing", "recommendation"].join(" "),
];

async function files(root) {
  const entries = await readdir(root, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map((entry) =>
      entry.isDirectory() ? files(join(root, entry.name)) : [join(root, entry.name)],
    ),
  );
  return nested.flat();
}

const buildFiles = (await files(outputRoot)).filter((file) =>
  [".js", ".html", ".json"].includes(extname(file)),
);
const violations = [];
for (const file of buildFiles) {
  const content = (await readFile(file, "utf8")).toLowerCase();
  for (const phrase of phrases) {
    if (content.includes(phrase)) violations.push(`${file}: ${phrase}`);
  }
}
if (violations.length) {
  throw new Error(
    `Forbidden patient-care language found in production output:\n${violations.join("\n")}`,
  );
}
console.log(`Forbidden-language check passed (${buildFiles.length} production files scanned).`);
