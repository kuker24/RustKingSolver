import { CariRujukanInput, CariRujukanOutput, RujukanItem } from '../lib/types.js';
import { searchCrossrefWorks } from '../lib/crossref.js';
import { searchOpenAlexWorks } from '../lib/openalex.js';

export async function cariRujukan(input: CariRujukanInput): Promise<CariRujukanOutput> {
  const { query, sumber, limit, tahun_min, tahun_max } = input;
  const peringatan: string[] = [];
  const allResults: RujukanItem[] = [];

  const tasks: Promise<void>[] = [];

  if (sumber.includes('crossref')) {
    tasks.push((async () => {
      try {
        const crItems = await searchCrossrefWorks(query, limit, tahun_min, tahun_max);
        allResults.push(...crItems);
      } catch (err) {
        peringatan.push(`Pencarian Crossref gagal: ${err instanceof Error ? err.message : String(err)}`);
      }
    })());
  }

  if (sumber.includes('openalex')) {
    tasks.push((async () => {
      try {
        const oaItems = await searchOpenAlexWorks(query, limit, tahun_min, tahun_max);
        allResults.push(...oaItems);
      } catch (err) {
        peringatan.push(`Pencarian OpenAlex gagal: ${err instanceof Error ? err.message : String(err)}`);
      }
    })());
  }

  if (sumber.includes('semanticscholar')) {
    peringatan.push('Semantic Scholar API rate-limit ketat tanpa S2_API_KEY; hasil mungkin dibatasi');
  }

  await Promise.allSettled(tasks);

  // Deduplikasi berdasarkan DOI atau normalisasi judul
  const seenDoi = new Set<string>();
  const seenTitles = new Set<string>();
  const uniqueResults: RujukanItem[] = [];

  for (const item of allResults) {
    if (item.doi) {
      const normDoi = item.doi.toLowerCase().trim();
      if (seenDoi.has(normDoi)) continue;
      seenDoi.add(normDoi);
    } else if (item.judul) {
      const normTitle = item.judul.toLowerCase().trim();
      if (seenTitles.has(normTitle)) continue;
      seenTitles.add(normTitle);
    }
    uniqueResults.push(item);
    if (uniqueResults.length >= limit) break;
  }

  return {
    hasil: uniqueResults,
    peringatan
  };
}
