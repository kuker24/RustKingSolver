import { CekBakuInput, CekBakuOutput, BakuTemuan } from '../lib/types.js';
import { loadKataBaku } from '../lib/dictionary.js';
import { getCachedWord, lookupKbbiOnline } from '../lib/kbbi.js';

export async function cekBaku(input: CekBakuInput): Promise<CekBakuOutput> {
  const { teks, fallback_kbbi, max_lookup } = input;
  const { map: dictMap, phrases } = loadKataBaku();

  const temuanMap = new Map<string, BakuTemuan>();
  const checkedSpans: Array<[number, number]> = [];

  const isSpanChecked = (start: number, end: number): boolean => {
    return checkedSpans.some(([s, e]) => (start >= s && start < e) || (end > s && end <= e));
  };

  // 1. Periksa frasa majemuk terlebih dahulu (misal: "merubah variabel", "web site", dll.)
  const lowerTeks = teks.toLowerCase();
  for (const phraseEntry of phrases) {
    const phrase = phraseEntry.tidak_baku.toLowerCase();
    let idx = lowerTeks.indexOf(phrase);
    while (idx !== -1) {
      const endIdx = idx + phrase.length;
      if (!isSpanChecked(idx, endIdx)) {
        checkedSpans.push([idx, endIdx]);
        const originalWord = teks.substring(idx, endIdx);
        const status = phraseEntry.cek_manusia ? 'perlu_cek_manusia' : 'tidak_baku';

        temuanMap.set(phrase, {
          kata: originalWord,
          status,
          saran_baku: phraseEntry.baku,
          sumber: 'daftar_lokal',
          url_kbbi: phraseEntry.url_kbbi
        });
      }
      idx = lowerTeks.indexOf(phrase, idx + 1);
    }
  }

  // 2. Tokenisasi kata individual
  const wordRegex = /\b[\p{L}\p{N}'-]+\b/gu;
  let match: RegExpExecArray | null;
  const wordsToLookup: string[] = [];

  while ((match = wordRegex.exec(teks)) !== null) {
    const word = match[0];
    const start = match.index;
    const end = start + word.length;

    if (isSpanChecked(start, end)) {
      continue;
    }

    const lowerWord = word.toLowerCase();

    // Hapus akhiran partikel/klitika umum untuk pemeriksaan (seperti -nya pada "supportnya")
    let baseWord = lowerWord;
    let suffix = '';
    if (baseWord.endsWith('nya') && baseWord.length > 5) {
      baseWord = baseWord.slice(0, -3);
      suffix = 'nya';
    }

    // Cek daftar lokal
    const localEntry = dictMap.get(lowerWord) || (baseWord !== lowerWord ? dictMap.get(baseWord) : undefined);
    if (localEntry) {
      const isMismatch = localEntry.tidak_baku.toLowerCase() !== localEntry.baku.toLowerCase();
      if (isMismatch || localEntry.cek_manusia) {
        const saran = suffix && !localEntry.baku.includes(' ') ? `${localEntry.baku}${suffix}` : localEntry.baku;
        temuanMap.set(lowerWord, {
          kata: word,
          status: localEntry.cek_manusia ? 'perlu_cek_manusia' : 'tidak_baku',
          saran_baku: saran,
          sumber: 'daftar_lokal',
          url_kbbi: localEntry.url_kbbi
        });
      }
      continue;
    }

    // Cek cache lokal
    const cached = getCachedWord(lowerWord);
    if (cached) {
      if (cached.status === 'tidak_baku' || cached.status === 'perlu_cek_manusia') {
        temuanMap.set(lowerWord, {
          kata: word,
          status: cached.status,
          saran_baku: cached.saran_baku,
          sumber: 'cache',
          url_kbbi: cached.url_kbbi
        });
      }
      continue;
    }

    // Kata belum diketahui, simpan kandidat lookup jika huruf cukup panjang
    if (fallback_kbbi && lowerWord.length > 3 && !/^\d+$/.test(lowerWord)) {
      if (!wordsToLookup.includes(lowerWord) && wordsToLookup.length < max_lookup) {
        wordsToLookup.push(lowerWord);
      }
    }
  }

  // 3. Fallback online lookup jika diminta
  let lookupTertunda = 0;
  if (fallback_kbbi && wordsToLookup.length > 0) {
    for (const w of wordsToLookup) {
      try {
        const res = await lookupKbbiOnline(w);
        if (res.status === 'tidak_baku' || res.status === 'perlu_cek_manusia') {
          temuanMap.set(w, {
            kata: w,
            status: res.status,
            saran_baku: res.saran_baku,
            sumber: 'kbbi_lookup',
            url_kbbi: res.url_kbbi
          });
        }
      } catch {
        lookupTertunda++;
      }
    }
  }

  const temuan = Array.from(temuanMap.values());
  const ok = !temuan.some(t => t.status === 'tidak_baku');

  return {
    ok,
    temuan,
    lookup_tertunda: lookupTertunda
  };
}
