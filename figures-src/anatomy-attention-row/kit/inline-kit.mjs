// Vendored from anatomy scripts/inline-kit.mjs (MIT, see LICENSE in this folder),
// upstream commit 1482e846. Local change: the kit sits beside this file, and only
// kitScript() is kept because this figure has no WebGL or 3D layer.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const KIT = dirname(fileURLToPath(import.meta.url));
const strip = (file) => readFileSync(join(KIT, file), "utf8").replace(/^export /gm, "");

export function kitScript() {
  return strip("iso-kit.mjs");
}
