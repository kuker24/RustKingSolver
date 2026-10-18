#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  BANK_REGISTRY,
  argValue,
  familyOf,
  getAvailableBanks,
  hasFlag,
  hueCloseness,
  overlapRatio,
  readJson,
  requireCatalogs,
  resolveBankRoot,
  tokenize,
} from "./lib.mjs";
import { fingerprint } from "./fingerprint.mjs";

const MIX_THRESHOLD = 8;
const STILLS = [".webp", ".png", ".jpg", ".jpeg", ".gif"];

function loadBrief(argv, cwd) {
  const file = argValue(argv, "brief", "");
  if (file) return readJson(path.resolve(cwd, file));
  const raw = argValue(argv, "brief-json", "");
  if (raw) return JSON.parse(raw);
  return fingerprint({
    cwd,
    query: argValue(argv, "query", ""),
    count: argValue(argv, "count", "3"),
    intent: argValue(argv, "intent", ""),
  });
}

function queryTokens(brief) {
  return tokenize(
    [
      brief.query,
      brief.productName,
      brief.industry,
      brief.surface,
      ...(brief.kinds || []),
      ...(brief.preferredBanks || []),
    ]
      .filter(Boolean)
      .join(" "),
  );
}

function addReason(reasons, code, detail) {
  if (!detail) return;
  if (reasons.some((r) => r.code === code && r.detail === detail)) return;
  reasons.push({ code, detail });
}

function scoreRefero(style, brief, qTokens) {
  const reasons = [];
  let score = 0;
  const kinds = brief.kinds || [];
  if (kinds.includes(style.kind)) {
    score += 24;
    addReason(reasons, "kind", style.kind);
  } else if ((style.tags || []).some((t) => kinds.includes(t))) {
    score += 12;
    const tag = style.tags.find((t) => kinds.includes(t));
    addReason(reasons, "kind", tag);
  }

  if (brief.surface === "dashboard" || brief.surface === "landing-page") {
    score += 18;
    addReason(reasons, "surface", `refero:${brief.surface}`);
  }

  if (brief.theme && brief.theme !== "unknown") {
    if (style.theme === brief.theme) {
      score += 20;
      addReason(reasons, "theme", style.theme);
    } else if (style.theme && style.theme !== brief.theme) {
      score -= 8;
    }
  }

  const doc = tokenize(
    [style.name, style.northStar, ...(style.tags || []), ...(style.fonts || []), style.industry]
      .filter(Boolean)
      .join(" "),
  );
  const tokenPts = overlapRatio(qTokens, doc) * 24;
  if (tokenPts >= 3) {
    score += tokenPts;
    addReason(reasons, "tokens", style.northStar || style.name);
  }

  if (brief.industry && style.industry) {
    const a = tokenize(brief.industry);
    const b = tokenize(style.industry);
    if (overlapRatio(a, b) > 0 || String(style.industry).toLowerCase().includes(brief.industry)) {
      score += 12;
      addReason(reasons, "industry", style.industry);
    }
  }

  const itemHexes = (style.colors || []).map((c) => c.hex).filter(Boolean);
  const hue = hueCloseness(brief.hexes || [], itemHexes);
  if (hue > 0) {
    score += hue * 10;
    addReason(reasons, "hue", "accent");
  }

  const rank = [style.trendingRank, style.popularRank].find((n) => Number.isFinite(n));
  if (Number.isFinite(rank) && rank >= 1 && rank <= 20) {
    score += 4 * ((21 - rank) / 20);
    addReason(reasons, "rank", String(rank));
  }

  if (style.thumbMissing) score -= 15;
  return { score, reasons };
}

function surfaceHit(item, surface) {
  const bag = new Set(
    [item.jenis, item.page_type, ...(item.types_source || [])].filter(Boolean),
  );
  if (bag.has(surface)) return "exact";
  if (
    (surface === "hero" && bag.has("landing-page")) ||
    (surface === "landing-page" && bag.has("hero"))
  ) {
    return "related";
  }
  return "";
}

function scoreMotion(item, brief, qTokens) {
  const reasons = [];
  let score = 0;
  const hit = surfaceHit(item, brief.surface);
  if (hit === "exact") {
    score += 28;
    addReason(reasons, "surface", item.jenis || brief.surface);
  } else if (hit === "related") {
    score += 16;
    addReason(reasons, "surface", `${item.jenis}~${brief.surface}`);
  }

  const industryBlob = [item.industry, item.category_source].filter(Boolean).join(" ");
  if (brief.industry && industryBlob) {
    const a = tokenize(brief.industry);
    const b = tokenize(industryBlob);
    if (
      overlapRatio(a, b) > 0 ||
      industryBlob.toLowerCase().includes(String(brief.industry).toLowerCase())
    ) {
      score += 20;
      addReason(reasons, "industry", item.industry || item.category_source);
    }
  }

  const tokenPts =
    overlapRatio(qTokens, tokenize([item.title, item.id, industryBlob].join(" "))) * 16;
  if (tokenPts >= 2) {
    score += tokenPts;
    addReason(reasons, "tokens", item.title);
  }

  if (item.featured) {
    score += 4;
    addReason(reasons, "featured", "featured");
  }
  if (Number.isFinite(item.popular_score) && item.popular_score > 0) {
    score += Math.min(4, item.popular_score / 8);
  }
  return { score, reasons };
}

function scoreGeneric(item, bankId, tier, brief, qTokens) {
  const reasons = [];
  let score = 0;
  const surface = String(brief.surface || "").toLowerCase();
  const cat = String(item.category || item.jenis || "").toLowerCase();
  const title = String(item.title || item.name || item.id || "").toLowerCase();
  const desc = String(item.description || "").toLowerCase();
  const tags = (item.tags || []).map((t) => String(t).toLowerCase());

  // Surface specialist boost
  const isSpecialist =
    (surface === "hero" && (bankId === "supahero" || bankId === "motionsites")) ||
    (surface === "navigation" && bankId === "navbargallery") ||
    (surface === "footer" && bankId === "footerdesign") ||
    (surface === "cta" && bankId === "ctagallery") ||
    (surface === "404" && bankId === "404sdesign") ||
    (surface === "scrollytelling" && bankId === "scrolltide") ||
    (surface === "micro-interaction" && bankId === "bencho") ||
    (surface === "3d-website" && bankId === "layers") ||
    (surface === "dashboard" && bankId === "aura") ||
    (surface === "landing-page" &&
      (bankId === "aura" || bankId === "motionsites" || bankId === "oversightsupply"));

  if (isSpecialist) {
    score += 20;
    addReason(reasons, "specialist", `${bankId}:${surface}`);
  } else if (cat && (cat === surface || cat.includes(surface) || surface.includes(cat))) {
    score += 14;
    addReason(reasons, "surface", cat);
  }

  // Token relevance
  const docTokens = tokenize([title, desc, ...tags, cat, item.author].filter(Boolean).join(" "));
  const tokenPts = overlapRatio(qTokens, docTokens) * 22;
  if (tokenPts >= 2) {
    score += tokenPts;
    addReason(reasons, "tokens", title || item.id);
  }

  // Industry match
  if (brief.industry) {
    const indTokens = tokenize(brief.industry);
    if (
      overlapRatio(indTokens, docTokens) > 0 ||
      desc.includes(brief.industry) ||
      tags.includes(brief.industry)
    ) {
      score += 16;
      addReason(reasons, "industry", brief.industry);
    }
  }

  // Style / Kind match
  const kinds = brief.kinds || [];
  for (const k of kinds) {
    if (tags.includes(k) || title.includes(k) || desc.includes(k)) {
      score += 12;
      addReason(reasons, "kind", k);
      break;
    }
  }

  // Popular rank bonus
  if (Number.isFinite(item.popular_rank) && item.popular_rank >= 1 && item.popular_rank <= 50) {
    score += Math.max(1, 4 * ((51 - item.popular_rank) / 50));
    addReason(reasons, "rank", `#${item.popular_rank}`);
  } else if (Number.isFinite(item.popular_score) && item.popular_score > 0) {
    score += Math.min(4, item.popular_score / 15);
  }

  return { score, reasons };
}

function referoAbs(referoRoot, rel) {
  if (!rel) return null;
  return path.join(referoRoot, rel.replace(/^\//, ""));
}

function firstExisting(candidates) {
  for (const p of candidates) {
    if (p && fs.existsSync(p)) return p;
  }
  return candidates[0] || null;
}

function motionPreview(dir, previewField) {
  const named = previewField ? path.join(dir, previewField) : null;
  const fallbacks = STILLS.map((ext) => path.join(dir, `preview${ext}`));
  return firstExisting([named, ...fallbacks]);
}

function shapeRefero(style, scored, paths) {
  const design = referoAbs(paths.referoRoot, style.files?.design);
  const tokens = referoAbs(paths.referoRoot, style.files?.tokens);
  const tailwind = referoAbs(paths.referoRoot, style.files?.tailwind);
  const thumb = referoAbs(paths.referoRoot, style.thumb);
  const dir = design ? path.dirname(design) : null;
  return {
    id: style.slug || style.id,
    bank: "refero",
    name: style.name,
    lane: "identity",
    score: Number(scored.score.toFixed(2)),
    reasons: scored.reasons,
    theme: style.theme || null,
    kind: style.kind || null,
    jenis: null,
    northStar: style.northStar || null,
    industry: style.industry || null,
    fonts: style.fonts || [],
    hexes: (style.colors || []).map((c) => c.hex).filter(Boolean).slice(0, 8),
    preview: thumb,
    files: {
      design,
      tokens,
      tailwind,
      meta: dir ? path.join(dir, "meta.json") : null,
      prompt: null,
      source: null,
    },
  };
}

function shapeMotion(item, scored, paths) {
  const dir = path.join(paths.motionRoot, item.jenis, item.id);
  return {
    id: item.id,
    bank: "motion",
    name: item.title || item.id,
    lane: "section",
    score: Number(scored.score.toFixed(2)),
    reasons: scored.reasons,
    theme: null,
    kind: null,
    jenis: item.jenis,
    northStar: null,
    industry: item.industry || item.category_source || null,
    fonts: [],
    hexes: [],
    preview: motionPreview(dir, item.preview),
    files: {
      design: null,
      tokens: null,
      tailwind: null,
      meta: path.join(dir, "meta.json"),
      prompt: path.join(dir, "prompt.md"),
      source: null,
    },
  };
}

function shapeGeneric(item, bankId, conf, scored) {
  const cat = item.category || item.jenis || conf.tier;
  const itemDir = path.join(conf.baseDir, "library", cat, item.id);
  const namedPreview = item.preview ? path.join(itemDir, item.preview) : null;
  const fallbacks = STILLS.map((ext) => path.join(itemDir, `preview${ext}`));
  const preview = firstExisting([namedPreview, ...fallbacks]);

  const textContext = `${item.title || ""} ${item.description || ""} ${(item.tags || []).join(" ")}`.toLowerCase();
  let theme = item.theme || null;
  if (!theme) {
    if (/\b(dark|dark-mode|midnight|black|dim)\b/.test(textContext)) theme = "dark";
    else if (/\b(light|white|paper|clean light)\b/.test(textContext)) theme = "light";
  }

  let kind = item.kind || null;
  if (!kind || kind === "component" || kind === "landing-template") {
    if (/\b(dark-mode|dark)\b/.test(textContext)) kind = "dark-mode";
    else if (/\bminimal\b/.test(textContext)) kind = "minimal";
    else if (/\beditorial\b/.test(textContext)) kind = "editorial";
    else if (/\bplayful\b/.test(textContext)) kind = "playful";
    else if (/\bbrutalist\b/.test(textContext)) kind = "brutalist";
  }

  return {
    id: item.id,
    bank: bankId,
    name: item.title || item.name || item.id,
    lane: conf.tier,
    category: cat,
    score: Number(scored.score.toFixed(2)),
    reasons: scored.reasons,
    theme,
    kind,
    jenis: item.jenis || cat,
    northStar: item.description || null,
    industry: item.industry || null,
    fonts: item.fonts || [],
    hexes: (item.colors || []).map((c) => c.hex || c).filter(Boolean),
    preview,
    files: {
      folder: itemDir,
      meta: path.join(itemDir, "meta.json"),
      prompt: path.join(itemDir, "prompt.md"),
      design: null,
      tokens: null,
      tailwind: null,
      source: path.join(itemDir, "source.html"),
    },
  };
}

function takeDiverse(sorted, count, used) {
  const out = [];
  for (const item of sorted) {
    if (out.length >= count) break;
    const fam = familyOf(item.id);
    if (used.has(fam)) continue;
    used.add(fam);
    out.push(item);
  }
  return out;
}

function pickShortlist(grouped, count, lane) {
  const used = new Set();
  const identityItems = (grouped.identity || []).sort((a, b) => b.score - a.score);
  const sectionItems = (grouped.section || []).sort((a, b) => b.score - a.score);
  const motionItems = (grouped.motion || []).sort((a, b) => b.score - a.score);
  const atomicItems = (grouped.atomic || []).sort((a, b) => b.score - a.score);

  if (lane === "identity") {
    return takeDiverse(identityItems, count, used);
  }
  if (lane === "section") {
    const combined = [...sectionItems, ...motionItems].sort((a, b) => b.score - a.score);
    return takeDiverse(combined, count, used);
  }
  if (lane === "motion") {
    return takeDiverse(motionItems, count, used);
  }
  if (lane === "atomic") {
    return takeDiverse(atomicItems, count, used);
  }

  // Lane "both" or "all": Balanced synthesis across identity and dynamic surfaces
  const out = [];
  const referoHits = (grouped.identity || []).filter(
    (x) => x.bank === "refero" && x.score >= MIX_THRESHOLD,
  );
  const motionHits = [
    ...(grouped.motion || []),
    ...(grouped.section || []),
  ].filter((x) => x.bank === "motion" && x.score >= MIX_THRESHOLD);

  if (referoHits.length) {
    out.push(...takeDiverse(referoHits, 1, used));
  }
  if (motionHits.length) {
    out.push(...takeDiverse(motionHits, 1, used));
  }

  const allItems = [
    ...identityItems,
    ...sectionItems,
    ...motionItems,
    ...atomicItems,
  ].sort((a, b) => b.score - a.score);

  for (const item of allItems) {
    if (out.length >= count) break;
    if (out.includes(item)) continue;
    const fam = familyOf(item.id);
    if (used.has(fam)) continue;
    used.add(fam);
    out.push(item);
  }

  return out.sort((a, b) => b.score - a.score);
}

export function search({ brief, bankRoot, lane, exclude = [], bankFilter = "all" }) {
  const root = resolveBankRoot(bankRoot);
  const paths = requireCatalogs(root);
  const available = paths.available || getAvailableBanks(root);
  const qTokens = queryTokens(brief);
  const skip = new Set((exclude || []).map((s) => String(s).toLowerCase()));
  const resolvedLane = lane || brief.laneHint || "both";

  const grouped = {
    identity: [],
    section: [],
    motion: [],
    atomic: [],
  };

  for (const [bankId, conf] of Object.entries(available)) {
    if (bankFilter !== "all" && bankFilter !== bankId) continue;

    try {
      const catData = readJson(conf.catalogPath);

      if (bankId === "refero") {
        for (const style of catData.styles || []) {
          const id = style.slug || style.id;
          if (skip.has(String(id).toLowerCase())) continue;
          const scored = scoreRefero(style, brief, qTokens);
          grouped.identity.push(shapeRefero(style, scored, paths));
        }
      } else if (bankId === "motionsites") {
        for (const item of catData.items || []) {
          if (skip.has(String(item.id).toLowerCase())) continue;
          const scored = scoreMotion(item, brief, qTokens);
          const shaped = shapeMotion(item, scored, paths);
          grouped.motion.push(shaped);
          // Motionsites items also serve as sections
          grouped.section.push(shaped);
        }
      } else {
        const items = catData.items || catData.styles || [];
        const tier = conf.tier || "section";
        for (const item of items) {
          const id = item.id || item.slug;
          if (!id || skip.has(String(id).toLowerCase())) continue;
          const scored = scoreGeneric(item, bankId, tier, brief, qTokens);
          const shaped = shapeGeneric(item, bankId, conf, scored);
          if (grouped[tier]) {
            grouped[tier].push(shaped);
          } else {
            grouped.section.push(shaped);
          }
        }
      }
    } catch {
      // Gracefully continue if an individual optional catalog has parse error
    }
  }

  const count = Number(brief.count) === 5 ? 5 : 3;
  const items = pickShortlist(grouped, count, resolvedLane);

  return {
    bankRoot: root,
    lane: resolvedLane,
    count,
    availableBanks: Object.keys(available),
    brief: {
      intent: brief.intent,
      mode: brief.mode,
      surface: brief.surface,
      industry: brief.industry,
      theme: brief.theme,
      kinds: brief.kinds,
      productName: brief.productName,
    },
    items,
  };
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function selfTest(bankRoot) {
  const fixturesDir = path.join(path.dirname(fileURLToPath(import.meta.url)), "fixtures");
  const saas = readJson(path.join(fixturesDir, "saas-dark-dashboard.json"));
  const wellness = readJson(path.join(fixturesDir, "wellness-hero.json"));

  const saasHit = search({ brief: saas, bankRoot, lane: "identity" });
  assert(saasHit.items.length === 3, `saas expected 3, got ${saasHit.items.length}`);
  const darkish = saasHit.items.filter(
    (i) =>
      i.theme === "dark" ||
      i.kind === "dark-mode" ||
      (i.kind === "minimal" && i.theme === "dark"),
  );
  assert(
    darkish.length >= 2,
    `saas dark dashboard should lean Refero dark/minimal, got ${saasHit.items.map((i) => `${i.id}:${i.kind}/${i.theme}`).join(", ")}`,
  );

  const well = search({ brief: wellness, bankRoot, lane: "section" });
  assert(well.items.length === 3, `wellness expected 3, got ${well.items.length}`);
  const motionOk = well.items.filter(
    (i) =>
      i.bank === "motion" &&
      (i.jenis === "hero" ||
        i.jenis === "landing-page" ||
        /well|health|heal|mind|body/i.test(i.id + i.name)),
  );
  assert(
    motionOk.length >= 2,
    `wellness hero should lean Motion hero/landing, got ${well.items.map((i) => `${i.id}:${i.jenis}`).join(", ")}`,
  );

  const five = search({ brief: { ...saas, count: 5 }, bankRoot, lane: "both" });
  assert(five.items.length === 5, `count 5 expected 5, got ${five.items.length}`);
  const banks = new Set(five.items.map((i) => i.bank));
  assert(banks.has("refero") && banks.has("motion"), "lane both should mix banks");

  const missingRoot = path.join(path.dirname(fixturesDir), "missing-bank-should-not-exist");
  let failed = false;
  try {
    search({ brief: saas, bankRoot: missingRoot });
  } catch (err) {
    failed = err.code === "BANK_MISSING";
  }
  assert(failed, "missing catalog should exit with BANK_MISSING");

  process.stdout.write("self-test ok\n");
}

const isMain =
  process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);

if (isMain) {
  const argv = process.argv.slice(2);
  const cwd = argValue(argv, "cwd", process.cwd());
  const rawBank = argValue(argv, "bank", "");
  const isBankName =
    rawBank && Object.keys(BANK_REGISTRY).includes(rawBank.toLowerCase());
  const bankFilter = isBankName
    ? rawBank.toLowerCase()
    : argValue(argv, "bank-filter", "all");
  const explicitBankRoot = !isBankName
    ? argValue(argv, "bank-root", "") || rawBank
    : argValue(argv, "bank-root", "");
  const bankRoot = resolveBankRoot(explicitBankRoot);

  try {
    if (hasFlag(argv, "self-test")) {
      selfTest(bankRoot);
      process.exit(0);
    }
    const brief = loadBrief(argv, cwd);
    const countOverride = argValue(argv, "count", "");
    if (countOverride) brief.count = Number(countOverride) === 5 ? 5 : 3;
    const exclude = (argValue(argv, "exclude", "") || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const result = search({
      brief,
      bankRoot,
      lane: argValue(argv, "lane", brief.laneHint || "both"),
      exclude,
      bankFilter,
    });
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } catch (err) {
    process.stderr.write(`${err.message}\n`);
    process.exit(err.code === "BANK_MISSING" ? 2 : 1);
  }
}
