import { VerifikasiRujukanInput, VerifikasiRujukanOutput } from '../lib/types.js';
import { fetchCrossrefWork, searchCrossrefWorks } from '../lib/crossref.js';
import { titleSimilarity, authorFamilyMatch } from '../lib/similarity.js';

export async function verifikasiRujukan(input: VerifikasiRujukanInput): Promise<VerifikasiRujukanOutput> {
  const { doi, judul, penulis, tahun, url, ambang_judul } = input;

  let urlHidup = true;
  if (url) {
    try {
      const res = await fetch(url, {
        method: 'HEAD',
        headers: { 'User-Agent': 'OpenCodeHighEnd-PenulisIlmiah/0.1.18' },
        signal: AbortSignal.timeout(4000)
      });
      urlHidup = res.status >= 200 && res.status < 400;
    } catch {
      urlHidup = false;
    }
  }

  // JALUR 1: Memiliki DOI
  if (doi) {
    const cleanDoi = doi.replace(/^https?:\/\/doi\.org\//i, '').replace(/^doi:\s*/i, '').trim();
    const work = await fetchCrossrefWork(cleanDoi);

    if (!work) {
      return {
        status: 'TIDAK_DITEMUKAN',
        doi: cleanDoi,
        kecocokan: { url_hidup: urlHidup },
        alasan: `DOI '${cleanDoi}' tidak terdaftar atau tidak ditemukan di Crossref.`
      };
    }

    const canonicalTitle = work.title?.[0] || '';
    const workAuthors = work.author?.map(a => `${a.family || ''}, ${a.given || ''}`.trim()).filter(Boolean) || [];
    const workYear = work.issued?.['date-parts']?.[0]?.[0] || work.created?.['date-parts']?.[0]?.[0] || null;
    const canonicalUrl = work.resource?.primary?.URL || work.URL || `https://doi.org/${cleanDoi}`;
    const venue = work['container-title']?.[0] || '';

    let judulScore = 1.0;
    if (judul && canonicalTitle) {
      judulScore = titleSimilarity(judul, canonicalTitle);
      if (judulScore < ambang_judul) {
        return {
          status: 'TIDAK_COCOK',
          doi: cleanDoi,
          metadata: {
            judul: canonicalTitle,
            penulis: workAuthors,
            tahun: workYear,
            url: canonicalUrl,
            venue
          },
          kecocokan: {
            judul_score: Number(judulScore.toFixed(3)),
            penulis_score: penulis ? authorFamilyMatch(penulis, workAuthors) : 1.0,
            tahun_cocok: tahun && workYear ? Math.abs(tahun - workYear) <= 1 : true,
            url_hidup: urlHidup
          },
          alasan: `Judul klaim ('${judul}') tidak cocok dengan judul resmi DOI ('${canonicalTitle}'). Skor kemiripan: ${judulScore.toFixed(2)} (ambang: ${ambang_judul}).`
        };
      }
    }

    const penulisScore = penulis ? authorFamilyMatch(penulis, workAuthors) : 1.0;
    const tahunCocok = tahun && workYear ? Math.abs(tahun - workYear) <= 1 : true;

    return {
      status: 'VALID',
      doi: cleanDoi,
      metadata: {
        judul: canonicalTitle,
        penulis: workAuthors,
        tahun: workYear,
        url: canonicalUrl,
        venue
      },
      kecocokan: {
        judul_score: Number(judulScore.toFixed(3)),
        penulis_score: penulisScore,
        tahun_cocok: tahunCocok,
        url_hidup: urlHidup
      },
      alasan: 'Rujukan terverifikasi secara sahih dan metadata selaras di Crossref.'
    };
  }

  // JALUR 2: Tanpa DOI, mencari via judul & penulis
  if (judul) {
    const candidates = await searchCrossrefWorks(judul, 5, tahun ? tahun - 1 : undefined, tahun ? tahun + 1 : undefined);

    for (const cand of candidates) {
      if (cand.judul) {
        const score = titleSimilarity(judul, cand.judul);
        if (score >= ambang_judul) {
          const pScore = penulis ? authorFamilyMatch(penulis, cand.penulis) : 1.0;
          return {
            status: 'VALID',
            doi: cand.doi,
            metadata: {
              judul: cand.judul,
              penulis: cand.penulis,
              tahun: cand.tahun,
              url: cand.url,
              venue: cand.venue
            },
            kecocokan: {
              judul_score: Number(score.toFixed(3)),
              penulis_score: pScore,
              tahun_cocok: true,
              url_hidup: urlHidup
            },
            alasan: 'Rujukan ditemukan dan terverifikasi secara sahih melalui pencarian judul di Crossref.'
          };
        }
      }
    }

    return {
      status: 'TIDAK_DITEMUKAN',
      kecocokan: { url_hidup: urlHidup },
      alasan: `Tidak ditemukan publikasi ilmiah yang cocok dengan judul '${judul}' di basis data resmi.`
    };
  }

  return {
    status: 'TIDAK_DITEMUKAN',
    alasan: 'Informasi rujukan tidak memadai untuk diverifikasi.'
  };
}
