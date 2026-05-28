#!/usr/bin/env node
// Copies the shared design assets from frontend/ into site/ for the
// GitHub Pages deploy. Run via `npm run site:build` from frontend/.
// Idempotent. Run as often as you like.

import { cp, mkdir, readFile, writeFile, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..");

const stylesSrc = join(repoRoot, "frontend", "src", "lib", "styles");
const fontsSrc = join(repoRoot, "frontend", "static", "fonts");

const siteRoot = join(repoRoot, "site");
const assetsOut = join(siteRoot, "assets");
const fontsOut = join(siteRoot, "fonts");

const cssFiles = ["tokens.css", "fonts.css", "base.css", "components.css"];

async function main() {
  if (!existsSync(stylesSrc)) throw new Error(`missing: ${stylesSrc}`);
  if (!existsSync(fontsSrc)) throw new Error(`missing: ${fontsSrc}`);

  // Clean previous build to catch removals.
  await rm(assetsOut, { recursive: true, force: true });
  await rm(fontsOut, { recursive: true, force: true });
  await mkdir(assetsOut, { recursive: true });
  await mkdir(fontsOut, { recursive: true });

  // Copy CSS files.
  for (const name of cssFiles) {
    const src = join(stylesSrc, name);
    if (!existsSync(src)) throw new Error(`missing CSS: ${src}`);
    let body = await readFile(src, "utf8");
    // fonts.css under frontend/src/lib/styles/ references /fonts/...
    // (SvelteKit static asset root). Rewrite to ../fonts/... for site/.
    if (name === "fonts.css") {
      body = body.replace(/url\((["']?)\/fonts\//g, "url($1../fonts/");
    }
    await writeFile(join(assetsOut, name), body, "utf8");
  }

  // Copy fonts directory.
  await cp(fontsSrc, fontsOut, { recursive: true });

  console.log(`build-site-assets: ${cssFiles.length} css + fonts/ → site/`);
}

main().catch((err) => {
  console.error(`build-site-assets failed: ${err.message}`);
  process.exit(1);
});
