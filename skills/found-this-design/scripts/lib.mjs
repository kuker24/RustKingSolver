import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function catalogsOk(root) {
  if (!root || !fs.existsSync(root)) return false;
  if (
    fs.existsSync(path.join(root, "Refero/bank/catalog.json")) &&
    fs.existsSync(path.join(root, "motionsites/library/catalog.json"))
  ) {
    return true;
  }
  let count = 0;
  for (const conf of Object.values(BANK_REGISTRY)) {
    if (fs.existsSync(path.join(root, conf.catalogRel))) count++;
  }
  return count >= 2;
}

function bankFromAdapterConfig() {
  const cfg = path.join(os.homedir(), ".omp/agent/config/design-bank.json");
  try {
    const data = JSON.parse(fs.readFileSync(cfg, "utf8"));
    if (data && typeof data.root === "string" && catalogsOk(data.root)) return data.root;
  } catch {
    /* doctor reports NOT_CONFIGURED; do not invent a path */
  }
  return "";
}

function envBank() {
  return process.env.OPENCODE_DESIGN_BANK || "";
}

function ownedShareBank() {
  return path.join(os.homedir(), ".local/share/opencode-highend/design-bank");
}

export const DEFAULT_BANK =
  envBank() ||
  bankFromAdapterConfig() ||
  (catalogsOk(ownedShareBank()) ? ownedShareBank() : "") ||
  path.join(os.homedir(), "Design");

export function resolveBankRoot(explicit) {
  if (explicit) return explicit;
  const candidates = [
    envBank(),
    bankFromAdapterConfig(),
    path.join(os.homedir(), "Design"),
    ownedShareBank(),
  ].filter(Boolean);
  for (const root of candidates) {
    if (catalogsOk(root)) return root;
  }
  return DEFAULT_BANK;
}

export const BANK_REGISTRY = {
  refero: {
    id: "refero",
    name: "Refero.design",
    tier: "identity",
    catalogRel: "Refero/bank/catalog.json",
    baseRel: "Refero",
    itemKey: "styles",
    description: "Design systems, color palettes, CSS tokens, typography",
  },
  aura: {
    id: "aura",
    name: "Aura.build",
    tier: "identity",
    catalogRel: "aura/library/catalog.json",
    baseRel: "aura",
    itemKey: "items",
    description: "Full-page landing templates and complete dashboard layouts",
  },
  motionsites: {
    id: "motionsites",
    name: "Motionsites.ai",
    tier: "motion",
    catalogRel: "motionsites/library/catalog.json",
    baseRel: "motionsites",
    itemKey: "items",
    description: "Motion UI direction, animated heroes, WebGL interactions",
  },
  scrolltide: {
    id: "scrolltide",
    name: "Scrolltide.co",
    tier: "motion",
    catalogRel: "scrolltide/library/catalog.json",
    baseRel: "scrolltide",
    itemKey: "items",
    description: "Scrollytelling, timeline pinning, scroll-driven interactive dashboards",
  },
  bencho: {
    id: "bencho",
    name: "Bencho.dev",
    tier: "motion",
    catalogRel: "bencho/library/catalog.json",
    baseRel: "bencho",
    itemKey: "items",
    description: "Micro-interactions, gooey physics, interactive widgets",
  },
  layers: {
    id: "layers",
    name: "Getlayers.ai",
    tier: "motion",
    catalogRel: "layers/library/catalog.json",
    baseRel: "layers",
    itemKey: "items",
    description: "3D Three.js scenes, WebGL shaders, animated mesh gradients",
  },
  supahero: {
    id: "supahero",
    name: "Supahero.io",
    tier: "section",
    catalogRel: "supahero/library/catalog.json",
    baseRel: "supahero",
    itemKey: "items",
    description: "High-converting SaaS hero headers, split layouts, 3D headers",
  },
  navbargallery: {
    id: "navbargallery",
    name: "Navbar.gallery",
    tier: "section",
    catalogRel: "navbargallery/library/catalog.json",
    baseRel: "navbargallery",
    itemKey: "items",
    description: "Navigation bars, mega menus, sticky headers, floating docks",
  },
  footerdesign: {
    id: "footerdesign",
    name: "Footer.design",
    tier: "section",
    catalogRel: "footerdesign/library/catalog.json",
    baseRel: "footerdesign",
    itemKey: "items",
    description: "Multi-column website footers, sitemaps, newsletters",
  },
  ctagallery: {
    id: "ctagallery",
    name: "Cta.gallery",
    tier: "section",
    catalogRel: "ctagallery/library/catalog.json",
    baseRel: "ctagallery",
    itemKey: "items",
    description: "Call-to-action sections, conversion banners, waitlist blocks",
  },
  "404sdesign": {
    id: "404sdesign",
    name: "404s.design",
    tier: "section",
    catalogRel: "404sdesign/library/catalog.json",
    baseRel: "404sdesign",
    itemKey: "items",
    description: "Playful 404 error pages, empty states, recovery flows",
  },
  "21st": {
    id: "21st",
    name: "21st.dev",
    tier: "atomic",
    catalogRel: "21st/library/catalog.json",
    baseRel: "21st",
    itemKey: "items",
    description: "Atomic UI components, React/Tailwind elements, shaders",
  },
  oversightsupply: {
    id: "oversightsupply",
    name: "Oversight Supply",
    tier: "identity",
    catalogRel: "oversightsupply/library/catalog.json",
    baseRel: "oversightsupply",
    itemKey: "items",
    description: "Handcrafted Webflow and Framer website templates from Oversight Supply",
  },
  oversightsections: {
    id: "oversightsections",
    name: "Oversight Supply Sections",
    tier: "section",
    catalogRel: "oversightsupply/library/catalog-sections.json",
    baseRel: "oversightsupply",
    itemKey: "items",
    description: "Free interactive Oversight sections: studio originals plus Evergrid blocks",
  },
};

export function getAvailableBanks(bankRoot) {
  const available = {};
  for (const [key, conf] of Object.entries(BANK_REGISTRY)) {
    const p = path.join(bankRoot, conf.catalogRel);
    if (fs.existsSync(p)) {
      available[key] = {
        ...conf,
        catalogPath: p,
        baseDir: path.join(bankRoot, conf.baseRel),
      };
    }
  }
  return available;
}

export const REFERO_KINDS = [
  "dark-mode",
  "editorial",
  "playful",
  "monochrome",
  "high-contrast",
  "soft-gradients",
  "brutalist",
  "minimal",
  "lainnya",
];

export const MOTION_JENIS = [
  "hero",
  "landing-page",
  "features",
  "about",
  "footer",
  "cta",
  "pricing",
  "404",
  "mobile-app",
  "testimonials",
  "stats",
  "blog",
  "carousel",
  "3d-website",
];

const STOP = new Set([
  "the",
  "a",
  "an",
  "and",
  "or",
  "of",
  "for",
  "to",
  "in",
  "on",
  "with",
  "from",
  "this",
  "that",
  "its",
  "into",
  "over",
  "under",
  "your",
  "our",
  "web",
  "website",
  "page",
  "app",
  "site",
  "design",
  "desain",
  "dari",
  "yang",
  "untuk",
  "dan",
  "atau",
  "ini",
  "itu",
  "dengan",
  "pada",
  "sebuah",
  "sebagai",
  "adalah",
]);

export function catalogPaths(bankRoot) {
  return {
    refero: path.join(bankRoot, "Refero", "bank", "catalog.json"),
    motion: path.join(bankRoot, "motionsites", "library", "catalog.json"),
    referoRoot: path.join(bankRoot, "Refero"),
    motionRoot: path.join(bankRoot, "motionsites", "library"),
  };
}

export function requireCatalogs(bankRoot) {
  const available = getAvailableBanks(bankRoot);
  const paths = catalogPaths(bankRoot);
  if (Object.keys(available).length === 0) {
    const missing = [];
    if (!fs.existsSync(paths.refero)) missing.push(paths.refero);
    if (!fs.existsSync(paths.motion)) missing.push(paths.motion);
    const err = new Error(`Design bank catalogs missing:\n${missing.join("\n")}`);
    err.code = "BANK_MISSING";
    err.missing = missing;
    throw err;
  }
  return {
    ...paths,
    available,
  };
}

export function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

export function tokenize(text) {
  if (!text) return [];
  const raw = String(text)
    .toLowerCase()
    .replace(/[#./:_]+/g, " ")
    .match(/[a-z0-9]{3,}/g);
  if (!raw) return [];
  const out = [];
  const seen = new Set();
  for (const w of raw) {
    if (STOP.has(w) || seen.has(w)) continue;
    seen.add(w);
    out.push(w);
  }
  return out;
}

export function overlapRatio(queryTokens, docTokens) {
  if (!queryTokens.length || !docTokens.length) return 0;
  const set = new Set(docTokens);
  let hits = 0;
  for (const t of queryTokens) if (set.has(t)) hits += 1;
  return hits / queryTokens.length;
}

export function parseHex(hex) {
  if (!hex) return null;
  const m = String(hex).trim().match(/^#?([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (!m) return null;
  let h = m[1];
  if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  };
}

export function hexToHsl(hex) {
  const rgb = parseHex(hex);
  if (!rgb) return null;
  const r = rgb.r / 255;
  const g = rgb.g / 255;
  const b = rgb.b / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  const d = max - min;
  if (d === 0) return { h: 0, s: 0, l };
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h = 0;
  if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
  else if (max === g) h = (b - r) / d + 2;
  else h = (r - g) / d + 4;
  return { h: h * 60, s, l };
}

export function isAccent(hsl) {
  if (!hsl) return false;
  if (hsl.s < 0.12) return false;
  if (hsl.l < 0.08 || hsl.l > 0.92) return false;
  return true;
}

export function hueCloseness(aHexes, bHexes) {
  const a = (aHexes || []).map(hexToHsl).filter(isAccent);
  const b = (bHexes || []).map(hexToHsl).filter(isAccent);
  if (!a.length || !b.length) return 0;
  let best = 0;
  for (const x of a) {
    for (const y of b) {
      const dh = Math.min(Math.abs(x.h - y.h), 360 - Math.abs(x.h - y.h));
      if (dh <= 30) best = Math.max(best, 1 - dh / 30);
    }
  }
  return best;
}

export function familyOf(slug) {
  return String(slug || "")
    .toLowerCase()
    .replace(/-[0-9a-f]{8}$/i, "")
    .replace(/-hero$/, "");
}

export function extractHexes(text) {
  if (!text) return [];
  const found = String(text).match(/#(?:[0-9a-f]{3}|[0-9a-f]{6})\b/gi) || [];
  const out = [];
  const seen = new Set();
  for (const hex of found) {
    const key = hex.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(key.startsWith("#") ? key : `#${key}`);
  }
  return out;
}

export function argValue(argv, name, fallback = null) {
  const i = argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  const v = argv[i + 1];
  return v && !v.startsWith("--") ? v : fallback;
}

export function hasFlag(argv, name) {
  return argv.includes(`--${name}`);
}
