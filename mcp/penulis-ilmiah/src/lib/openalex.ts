import { RujukanItem } from './types.js';

function getMailto(): string {
  return process.env.CROSSREF_MAILTO || 'open-code-highend@users.noreply.github.com';
}

interface OpenAlexWork {
  id?: string;
  doi?: string;
  title?: string;
  display_name?: string;
  publication_year?: number;
  authorships?: Array<{ author?: { display_name?: string } }>;
  primary_location?: {
    landing_page_url?: string;
    source?: { display_name?: string };
  };
}

export async function searchOpenAlexWorks(
  query: string,
  limit: number = 5,
  tahunMin?: number,
  tahunMax?: number
): Promise<RujukanItem[]> {
  let url = `https://api.openalex.org/works?search=${encodeURIComponent(query)}&per-page=${limit}&mailto=${encodeURIComponent(getMailto())}`;

  if (process.env.OPENALEX_API_KEY) {
    url += `&api_key=${encodeURIComponent(process.env.OPENALEX_API_KEY)}`;
  }

  const filters: string[] = [];
  if (tahunMin) filters.push(`from_publication_date:${tahunMin}-01-01`);
  if (tahunMax) filters.push(`to_publication_date:${tahunMax}-12-31`);
  if (filters.length > 0) {
    url += `&filter=${encodeURIComponent(filters.join(','))}`;
  }

  try {
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'User-Agent': `OpenCodeHighEnd-PenulisIlmiah/0.1.18 (mailto:${getMailto()})`
      },
      signal: AbortSignal.timeout(8000)
    });

    if (!res.ok) return [];

    const data = await res.json() as { results?: OpenAlexWork[] };
    const results = data.results || [];

    return results.map(item => {
      const cleanDoi = item.doi ? item.doi.replace(/^https?:\/\/doi\.org\//i, '') : undefined;
      const authors = item.authorships?.map(a => a.author?.display_name || '').filter(Boolean) || [];

      return {
        judul: item.display_name || item.title || '',
        penulis: authors,
        tahun: item.publication_year || null,
        doi: cleanDoi,
        url: item.doi || item.primary_location?.landing_page_url || (cleanDoi ? `https://doi.org/${cleanDoi}` : undefined),
        sumber: 'openalex',
        venue: item.primary_location?.source?.display_name
      };
    });
  } catch {
    return [];
  }
}
