/**
 * Modul pembanding kemiripan teks untuk verifikasi judul & nama penulis
 */

export function normalizeString(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function levenshteinDistance(s1: string, s2: string): number {
  const m = s1.length;
  const n = s2.length;
  if (m === 0) return n;
  if (n === 0) return m;

  const d: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));

  for (let i = 0; i <= m; i++) d[i][0] = i;
  for (let j = 0; j <= n; j++) d[0][j] = j;

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = s1[i - 1] === s2[j - 1] ? 0 : 1;
      d[i][j] = Math.min(
        d[i - 1][j] + 1,      // deletion
        d[i][j - 1] + 1,      // insertion
        d[i - 1][j - 1] + cost // substitution
      );
    }
  }

  return d[m][n];
}

export function levenshteinSimilarity(s1: string, s2: string): number {
  const norm1 = normalizeString(s1);
  const norm2 = normalizeString(s2);
  if (norm1 === norm2) return 1.0;
  if (norm1.length === 0 || norm2.length === 0) return 0.0;

  const maxLen = Math.max(norm1.length, norm2.length);
  const dist = levenshteinDistance(norm1, norm2);
  return Math.max(0, 1 - dist / maxLen);
}

export function tokenJaccardSimilarity(s1: string, s2: string): number {
  const tokens1 = new Set(normalizeString(s1).split(/\s+/).filter(Boolean));
  const tokens2 = new Set(normalizeString(s2).split(/\s+/).filter(Boolean));

  if (tokens1.size === 0 && tokens2.size === 0) return 1.0;
  if (tokens1.size === 0 || tokens2.size === 0) return 0.0;

  let intersection = 0;
  for (const t of tokens1) {
    if (tokens2.has(t)) intersection++;
  }

  const union = tokens1.size + tokens2.size - intersection;
  return union === 0 ? 1.0 : intersection / union;
}

/**
 * Menghitung skor kemiripan komposit antara dua judul
 */
export function titleSimilarity(title1: string, title2: string): number {
  const norm1 = normalizeString(title1);
  const norm2 = normalizeString(title2);

  if (norm1 === norm2) return 1.0;
  if (norm1.length === 0 || norm2.length === 0) return 0.0;

  // Jika satu judul terkandung penuh dalam judul lainnya
  if (norm1.includes(norm2) || norm2.includes(norm1)) {
    const minLen = Math.min(norm1.length, norm2.length);
    const maxLen = Math.max(norm1.length, norm2.length);
    if (minLen / maxLen >= 0.7) {
      return 0.95;
    }
  }

  const jaccard = tokenJaccardSimilarity(norm1, norm2);
  const lev = levenshteinSimilarity(norm1, norm2);

  // Kombinasi berbobot: Jaccard 60%, Levenshtein 40%
  return jaccard * 0.6 + lev * 0.4;
}

/**
 * Memeriksa kecocokan nama keluarga penulis
 */
export function authorFamilyMatch(authors1: string[], authors2: string[]): number {
  if (!authors1.length || !authors2.length) return 1.0; // Anggap netral jika salah satu tidak tersedia

  const extractFamilies = (arr: string[]): Set<string> => {
    const families = new Set<string>();
    for (const a of arr) {
      const parts = a.split(/[, ]+/).filter(Boolean);
      for (const p of parts) {
        if (p.length > 2) {
          families.add(normalizeString(p));
        }
      }
    }
    return families;
  };

  const f1 = extractFamilies(authors1);
  const f2 = extractFamilies(authors2);

  let match = 0;
  for (const item of f1) {
    if (f2.has(item)) match++;
  }

  return match > 0 ? 1.0 : 0.0;
}
