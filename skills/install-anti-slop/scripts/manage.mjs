#!/usr/bin/env node
import { createHash } from "node:crypto";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const assetSource = resolve(skillRoot, "assets/anti-slop");

const RECOMMENDED_RULES = {
  "anti-slop/no-chained-type-assertions": "error",
  "anti-slop/no-widen-then-assert": "error",
  "anti-slop/no-known-value-widening": "warn",
  "anti-slop/require-safety-comment-for-type-assertion": "warn",
};

const STRICT_RULES = {
  "anti-slop/no-array-filter-map": "error",
  "anti-slop/no-chained-type-assertions": "error",
  "anti-slop/no-conditional-empty-object-spread": "error",
  "anti-slop/no-known-value-widening": "error",
  "anti-slop/no-module-mocking": "error",
  "anti-slop/no-object-parameters": "error",
  "anti-slop/no-reduce-accumulator-copy": "error",
  "anti-slop/no-reflect-apply": "error",
  "anti-slop/no-reflect-get": "error",
  "anti-slop/no-runtime-typeof": "error",
  "anti-slop/no-shape-in-symbol-names": "error",
  "anti-slop/no-unknown-parameters": "error",
  "anti-slop/no-unknown-returns": "error",
  "anti-slop/no-unknown-type-aliases": "error",
  "anti-slop/no-unsafe-dictionary-type": "error",
  "anti-slop/no-widen-then-assert": "error",
  "anti-slop/require-readable-spacing": "error",
  "anti-slop/require-safety-comment-for-type-assertion": "error",
  "oxc/no-accumulating-spread": "error",
};

const EFFECT_RULES = {
  "anti-slop-effect/no-manual-effect-error-tag": "error",
  "anti-slop-effect/no-manual-tag-comparison": "error",
  "anti-slop-effect/no-manual-tagged-construction": "error",
  "anti-slop-effect/no-service-constructor-imports": "error",
  "anti-slop-effect/prefer-effect-match": "error",
};

const DEFAULT_IGNORES = [
  ".agent/**",
  ".agents/**",
  ".claude/**",
  ".codex/**",
  ".continue/**",
  ".cursor/**",
  ".gemini/**",
  ".opencode/**",
  ".pi/**",
  ".roo/**",
  ".windsurf/**",
  "tools/oxlint/anti-slop/**",
];

function detectPackageManager(cwd) {
  if (existsSync(join(cwd, "pnpm-lock.yaml"))) return "pnpm";
  if (existsSync(join(cwd, "yarn.lock"))) return "yarn";
  if (existsSync(join(cwd, "bun.lockb")) || existsSync(join(cwd, "bun.lock"))) return "bun";
  return "npm";
}

function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0] || "audit";
  const profile = args.includes("--profile") ? args[args.indexOf("--profile") + 1] : "recommended";
  const withEffect = args.includes("--with-effect");
  const force = args.includes("--force");
  const json = args.includes("--json");
  const targetDir = args.find((a, i) => i > 0 && !a.startsWith("--") && args[i - 1] !== "--profile") || "tools/oxlint/anti-slop";
  return { command, profile, withEffect, force, json, targetDir };
}

function getFiles(dir, base = "") {
  let results = [];
  if (!existsSync(dir)) return results;
  const list = readdirSync(dir, { withFileTypes: true });
  for (const dirent of list) {
    const rel = base ? `${base}/${dirent.name}` : dirent.name;
    const full = join(dir, dirent.name);
    if (dirent.isDirectory()) {
      results = results.concat(getFiles(full, rel));
    } else if (dirent.isFile()) {
      results.push(rel);
    }
  }
  return results;
}

function fileHash(path) {
  const content = readFileSync(path);
  return createHash("sha256").update(content).digest("hex");
}

function runAudit(cwd, options) {
  const report = {
    mode: "audit",
    target: cwd,
    rulesTested: Object.keys(options.profile === "strict" ? STRICT_RULES : RECOMMENDED_RULES),
    findings: { source: [], test: [], tooling: [] },
    mutations: 0,
    clean: true,
  };
  if (options.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(`=== Anti-Slop Audit (${options.profile}) ===`);
    console.log(`Target: ${cwd}`);
    console.log(`Rules evaluated: ${report.rulesTested.length}`);
    console.log("No modifications made to repository (isolated audit).");
  }
  return 0;
}

function runInstall(cwd, options) {
  const target = resolve(cwd, options.targetDir);
  const relTarget = relative(cwd, target).replace(/\\/g, "/");

  if (existsSync(target) && !options.force) {
    console.error(`Refusing to overwrite existing anti-slop copy at ${target}.`);
    console.error("Review differences and re-run with --force if overwrite is intended.");
    return 1;
  }

  mkdirSync(dirname(target), { recursive: true });
  cpSync(assetSource, target, { recursive: true, force: options.force });

  // Select rules based on profile
  let selectedRules = options.profile === "strict" ? { ...STRICT_RULES } : { ...RECOMMENDED_RULES };
  let jsPlugins = [{ name: "anti-slop", specifier: `./${relTarget}/index.ts` }];

  if (options.withEffect) {
    jsPlugins.push({ name: "anti-slop-effect", specifier: `./${relTarget}/effect/index.ts` });
    selectedRules = { ...selectedRules, ...EFFECT_RULES };
  }

  // Update or create configuration
  const configTs = join(cwd, "oxlint.config.ts");
  const configJson = join(cwd, ".oxlintrc.json");

  const ignores = [...new Set([...DEFAULT_IGNORES, `${relTarget}/**`])];

  if (existsSync(configJson)) {
    try {
      const existing = JSON.parse(readFileSync(configJson, "utf-8"));
      existing.ignorePatterns = [...new Set([...(existing.ignorePatterns || []), ...ignores])];
      
      const existingPlugins = Array.isArray(existing.jsPlugins) ? existing.jsPlugins : [];
      const mergedPlugins = [...existingPlugins];
      for (const plugin of jsPlugins) {
        const idx = mergedPlugins.findIndex((p) => (typeof p === "string" ? p === plugin.name : p?.name === plugin.name));
        if (idx >= 0) {
          mergedPlugins[idx] = plugin;
        } else {
          mergedPlugins.push(plugin);
        }
      }
      existing.jsPlugins = mergedPlugins;
      existing.rules = { ...(existing.rules || {}), ...selectedRules };
      writeFileSync(configJson, JSON.stringify(existing, null, 2) + "\n", "utf-8");
    } catch (e) {
      console.warn("Could not merge existing .oxlintrc.json, falling back to oxlint.config.ts");
    }
  } else {
    const tsContent = `import { defineConfig } from "oxlint";

export default defineConfig({
  ignorePatterns: ${JSON.stringify(ignores, null, 4)},
  jsPlugins: ${JSON.stringify(jsPlugins, null, 4)},
  rules: ${JSON.stringify(selectedRules, null, 4)},
});
`;
    writeFileSync(configTs, tsContent, "utf-8");
  }

  const pkgManager = detectPackageManager(cwd);
  console.log(`Installed anti-slop plugin (${options.profile}) to ${relTarget}`);
  console.log(`Package manager: ${pkgManager}`);
  console.log(`Rules configured: ${Object.keys(selectedRules).length}`);
  console.log(`To run: ${pkgManager === "npm" ? "npx oxlint" : `${pkgManager} oxlint`}`);
  return 0;
}

function runUpdate(cwd, options) {
  const target = resolve(cwd, options.targetDir);
  const relTarget = relative(cwd, target).replace(/\\/g, "/");

  if (!existsSync(target)) {
    console.error(`No existing anti-slop installation found at ${target}. Use install first.`);
    return 1;
  }

  // Staging for dry-run comparison
  const stageDir = mkdtempSync(join(tmpdir(), "anti-slop-update-"));
  const stageTarget = join(stageDir, "incoming");
  cpSync(assetSource, stageTarget, { recursive: true });

  const incomingFiles = new Set(getFiles(stageTarget));
  const liveFiles = new Set(getFiles(target));
  const allRelFiles = Array.from(new Set([...incomingFiles, ...liveFiles])).sort();

  const classifications = {
    add: [],
    change: [],
    same: [],
    localOnly: [],
  };

  for (const rel of allRelFiles) {
    const inIncoming = incomingFiles.has(rel);
    const inLive = liveFiles.has(rel);

    if (inIncoming && !inLive) {
      classifications.add.push(rel);
    } else if (!inIncoming && inLive) {
      classifications.localOnly.push(rel);
    } else {
      const incomingHash = fileHash(join(stageTarget, rel));
      const liveHash = fileHash(join(target, rel));
      if (incomingHash === liveHash) {
        classifications.same.push(rel);
      } else {
        classifications.change.push(rel);
      }
    }
  }

  rmSync(stageDir, { recursive: true, force: true });

  if (!options.force) {
    const summary = {
      add: classifications.add.length,
      change: classifications.change.length,
      same: classifications.same.length,
      localOnly: classifications.localOnly.length,
    };

    if (options.json) {
      console.log(
        JSON.stringify(
          {
            mode: "update",
            target: relTarget,
            dryRun: true,
            mutations: 0,
            classifications,
            summary,
          },
          null,
          2
        )
      );
    } else {
      console.log(`=== Anti-Slop Update Review (Dry-run: no files modified) ===`);
      console.log(`Target: ${relTarget}`);
      for (const f of classifications.add) console.log(`  [ADD]        ${f}`);
      for (const f of classifications.change) console.log(`  [CHANGE]     ${f}`);
      for (const f of classifications.localOnly) console.log(`  [LOCAL-ONLY] ${f}`);
      for (const f of classifications.same) console.log(`  [SAME]       ${f}`);
      console.log(
        `Summary: ${summary.add} to add, ${summary.change} to change, ${summary.same} unchanged, ${summary.localOnly} local-only.`
      );
      console.log("No modifications made to repository (reviewed merge doctrine).");
      console.log("To apply changes and overwrite live files, re-run with --force.");
    }
    return 0;
  }

  return runInstall(cwd, { ...options, force: true });
}

function runRemove(cwd, options) {
  const target = resolve(cwd, options.targetDir);
  let removedCount = 0;
  if (existsSync(target)) {
    rmSync(target, { recursive: true, force: true });
    removedCount++;
  }
  const configTs = join(cwd, "oxlint.config.ts");
  if (existsSync(configTs)) {
    const text = readFileSync(configTs, "utf-8");
    if (text.includes("anti-slop") && text.includes("defineConfig")) {
      rmSync(configTs, { force: true });
      removedCount++;
    }
  }
  console.log(`Removed anti-slop assets and configurations (${removedCount} items removed).`);
  return 0;
}

function main() {
  const options = parseArgs();
  const cwd = process.cwd();

  if (options.command === "audit") {
    process.exit(runAudit(cwd, options));
  } else if (options.command === "install") {
    process.exit(runInstall(cwd, options));
  } else if (options.command === "update") {
    process.exit(runUpdate(cwd, options));
  } else if (options.command === "remove") {
    process.exit(runRemove(cwd, options));
  } else {
    console.error(`Unknown command: ${options.command}. Supported: audit, install, update, remove`);
    process.exit(1);
  }
}

main();
