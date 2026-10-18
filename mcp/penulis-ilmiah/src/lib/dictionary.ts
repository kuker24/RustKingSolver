import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface KataBakuEntry {
  tidak_baku: string;
  baku: string;
  url_kbbi: string;
  catatan: string;
  cek_manusia: boolean;
}

let cachedDictionary: Map<string, KataBakuEntry> | null = null;
let cachedPhraseList: KataBakuEntry[] | null = null;

/**
 * Mencari berkas kata_baku.md di berbagai kemungkinan lokasi
 */
function findKataBakuFile(): string | null {
  const candidates = [
    // Relatif dari src/lib
    path.resolve(__dirname, '../../../../skills/penulis-ilmiah/references/kata_baku.md'),
    // Relatif dari dist/lib
    path.resolve(__dirname, '../../../skills/penulis-ilmiah/references/kata_baku.md'),
    // Relatif dari current working dir
    path.resolve(process.cwd(), 'skills/penulis-ilmiah/references/kata_baku.md'),
    path.resolve(process.cwd(), 'references/kata_baku.md'),
    // Lokasi di ~/.omp/agent
    path.resolve(process.env.HOME || '', '.omp/agent/skills/penulis-ilmiah/references/kata_baku.md')
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

/**
 * Memuat dan mengurai isi kata_baku.md
 */
export function loadKataBaku(): { map: Map<string, KataBakuEntry>; phrases: KataBakuEntry[] } {
  if (cachedDictionary && cachedPhraseList) {
    return { map: cachedDictionary, phrases: cachedPhraseList };
  }

  const dictMap = new Map<string, KataBakuEntry>();
  const phraseList: KataBakuEntry[] = [];

  const filePath = findKataBakuFile();
  if (filePath && fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith('|') || trimmed.startsWith('| #') || trimmed.startsWith('|---')) {
        continue;
      }

      const cols = trimmed.split('|').map(c => c.trim());
      // format: | # | Tidak baku / diragukan | Baku / saran | URL cek | Catatan | cek_manusia |
      if (cols.length >= 7) {
        const tidakBaku = cols[2];
        const baku = cols[3];
        const url = cols[4];
        const catatan = cols[5];
        const cekManusia = cols[6] === 'ya';

        if (tidakBaku && baku) {
          const entry: KataBakuEntry = {
            tidak_baku: tidakBaku,
            baku: baku,
            url_kbbi: url,
            catatan: catatan,
            cek_manusia: cekManusia
          };

          const key = tidakBaku.toLowerCase();
          dictMap.set(key, entry);

          if (key.includes(' ')) {
            phraseList.push(entry);
          }
        }
      }
    }
  }

  // Tambahkan fallback entri penting jika berkas tidak ditemukan
  if (dictMap.size === 0) {
    const fallbackList = [
      { tidak_baku: 'analisa', baku: 'analisis', url_kbbi: 'https://kbbi.web.id/analisis', catatan: 'umum ilmiah', cek_manusia: false },
      { tidak_baku: 'aktipitas', baku: 'aktivitas', url_kbbi: 'https://kbbi.web.id/aktivitas', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'aktifitas', baku: 'aktivitas', url_kbbi: 'https://kbbi.web.id/aktivitas', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'apotik', baku: 'apotek', url_kbbi: 'https://kbbi.web.id/apotek', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'ijin', baku: 'izin', url_kbbi: 'https://kbbi.web.id/izin', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'diijinkan', baku: 'diizinkan', url_kbbi: 'https://kbbi.web.id/diizinkan', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'obyek', baku: 'objek', url_kbbi: 'https://kbbi.web.id/objek', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'metoda', baku: 'metode', url_kbbi: 'https://kbbi.web.id/metode', catatan: 'umum ilmiah', cek_manusia: false },
      { tidak_baku: 'propinsi', baku: 'provinsi', url_kbbi: 'https://kbbi.web.id/provinsi', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'prosentase', baku: 'persentase', url_kbbi: 'https://kbbi.web.id/persentase', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'resiko', baku: 'risiko', url_kbbi: 'https://kbbi.web.id/risiko', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'silahkan', baku: 'silakan', url_kbbi: 'https://kbbi.web.id/silakan', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'merubah', baku: 'mengubah', url_kbbi: 'https://kbbi.web.id/mengubah', catatan: 'umum', cek_manusia: false },
      { tidak_baku: 'terimakasih', baku: 'terima kasih', url_kbbi: 'https://kbbi.web.id/terima', catatan: 'umum', cek_manusia: false }
    ];

    for (const fb of fallbackList) {
      dictMap.set(fb.tidak_baku.toLowerCase(), fb);
    }
  }

  // Urutkan frasa berdasarkan panjang (descending) agar frasa panjang dicocokkan terlebih dahulu
  phraseList.sort((a, b) => b.tidak_baku.length - a.tidak_baku.length);

  cachedDictionary = dictMap;
  cachedPhraseList = phraseList;

  return { map: dictMap, phrases: phraseList };
}
