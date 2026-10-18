import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

export interface KbbiCacheItem {
  kata: string;
  status: 'tidak_baku' | 'baku' | 'tidak_diketahui' | 'perlu_cek_manusia';
  saran_baku: string;
  url_kbbi: string;
  timestamp: number;
}

interface KbbiCacheStore {
  [kata: string]: KbbiCacheItem;
}

const CACHE_TTL_MS = 30 * 24 * 60 * 60 * 1000; // 30 hari

function getCacheDir(): string {
  if (process.env.PENULIS_CACHE_DIR) {
    return process.env.PENULIS_CACHE_DIR;
  }
  return path.join(os.homedir(), '.cache', 'penulis-ilmiah');
}

function getCacheFilePath(): string {
  return path.join(getCacheDir(), 'kbbi-cache.json');
}

let memoryCache: KbbiCacheStore | null = null;

function loadCache(): KbbiCacheStore {
  if (memoryCache) return memoryCache;
  const filePath = getCacheFilePath();
  try {
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf-8');
      memoryCache = JSON.parse(data);
      return memoryCache!;
    }
  } catch {
    // Abaikan jika berkas korup
  }
  memoryCache = {};
  return memoryCache;
}

function saveCache(cache: KbbiCacheStore): void {
  try {
    const dir = getCacheDir();
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(getCacheFilePath(), JSON.stringify(cache, null, 2), 'utf-8');
  } catch {
    // Abaikan jika gagal menyimpan berkas cache
  }
}

export function getCachedWord(kata: string): KbbiCacheItem | null {
  const cache = loadCache();
  const key = kata.toLowerCase().trim();
  const item = cache[key];
  if (!item) return null;

  if (Date.now() - item.timestamp > CACHE_TTL_MS) {
    delete cache[key];
    saveCache(cache);
    return null;
  }
  return item;
}

export function setCachedWord(kata: string, data: Omit<KbbiCacheItem, 'timestamp'>): void {
  const cache = loadCache();
  const key = kata.toLowerCase().trim();
  cache[key] = {
    ...data,
    timestamp: Date.now()
  };
  saveCache(cache);
}

// Rate Limiter untuk online lookup
const rateLimitPerMin = parseInt(process.env.KBBI_RATE_PER_MIN || '20', 10);
const minIntervalMs = Math.ceil(60000 / rateLimitPerMin);
let lastRequestTime = 0;

async function waitRateLimit(): Promise<void> {
  const now = Date.now();
  const elapsed = now - lastRequestTime;
  if (elapsed < minIntervalMs) {
    await new Promise(resolve => setTimeout(resolve, minIntervalMs - elapsed));
  }
  lastRequestTime = Date.now();
}

/**
 * Melakukan lookup per-kata ke portal KBBI non-resmi cepat (kbbi.web.id)
 * CATATAN KERAS: Hanya lookup per kata; dilarang scraping massal.
 */
export async function lookupKbbiOnline(kata: string): Promise<KbbiCacheItem> {
  const cached = getCachedWord(kata);
  if (cached) return cached;

  await waitRateLimit();

  const url = `https://kbbi.web.id/${encodeURIComponent(kata)}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'OpenCodeHighEnd-PenulisIlmiah/0.1.18 (Academic Research Tool)'
      },
      signal: AbortSignal.timeout(5000)
    });

    if (res.status === 404) {
      const item: KbbiCacheItem = {
        kata,
        status: 'tidak_diketahui',
        saran_baku: kata,
        url_kbbi: url,
        timestamp: Date.now()
      };
      setCachedWord(kata, item);
      return item;
    }

    const html = await res.text();

    // Deteksi jika kbbi.web.id mengarahkan ke bentuk baku (misal: "bentuk tidak baku: apotik -> apotek")
    // Pola umum kbbi.web.id: "--> <a href="bentuk_baku">bentuk_baku</a>" atau "lihat <a href="...">"
    const matchRedirect = html.match(/(?:-->|lihat|bentuk tidak baku dari)\s*<a href="([^"]+)">([^<]+)<\/a>/i);
    if (matchRedirect) {
      const bentukBaku = matchRedirect[2].trim();
      const item: KbbiCacheItem = {
        kata,
        status: 'tidak_baku',
        saran_baku: bentukBaku,
        url_kbbi: `https://kbbi.web.id/${encodeURIComponent(bentukBaku)}`,
        timestamp: Date.now()
      };
      setCachedWord(kata, item);
      return item;
    }

    // Jika entri ditemukan langsung di KBBI
    if (html.includes('<b>' + kata.toLowerCase()) || html.includes('ditemukan')) {
      const item: KbbiCacheItem = {
        kata,
        status: 'baku',
        saran_baku: kata,
        url_kbbi: url,
        timestamp: Date.now()
      };
      setCachedWord(kata, item);
      return item;
    }

    const item: KbbiCacheItem = {
      kata,
      status: 'tidak_diketahui',
      saran_baku: kata,
      url_kbbi: url,
      timestamp: Date.now()
    };
    setCachedWord(kata, item);
    return item;
  } catch {
    return {
      kata,
      status: 'tidak_diketahui',
      saran_baku: kata,
      url_kbbi: url,
      timestamp: Date.now()
    };
  }
}
