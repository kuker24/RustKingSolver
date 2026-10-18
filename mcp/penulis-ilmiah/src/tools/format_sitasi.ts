import Cite from 'citation-js';
import { FormatSitasiInput, FormatSitasiOutput } from '../lib/types.js';
import { verifikasiRujukan } from './verifikasi_rujukan.js';

export async function formatSitasi(input: FormatSitasiInput): Promise<FormatSitasiOutput | { error: { code: string; message: string } }> {
  const { gaya, item, wajib_terverifikasi } = input;

  // 1. Guard Fail-Closed: Verifikasi rujukan jika diwajibkan
  if (wajib_terverifikasi) {
    if (!item.doi && !item.judul) {
      return {
        error: {
          code: 'REF_NOT_VERIFIED',
          message: 'Rujukan belum diverifikasi (tidak ada DOI atau judul yang dapat divalidasi). Sitasi ditolak demi menjaga integritas ilmiah.'
        }
      };
    }

    const verif = await verifikasiRujukan({
      doi: item.doi,
      judul: item.judul,
      penulis: item.penulis,
      tahun: item.tahun,
      url: item.url,
      ambang_judul: 0.85
    });

    if (verif.status !== 'VALID') {
      return {
        error: {
          code: 'REF_NOT_VERIFIED',
          message: `Rujukan berstatus ${verif.status} (${verif.alasan}). Sitasi ditolak sesuai aturan fail-closed.`
        }
      };
    }

    // Perkaya item dari metadata terverifikasi jika tersedia
    if (verif.metadata) {
      if (!item.judul && verif.metadata.judul) item.judul = verif.metadata.judul;
      if ((!item.penulis || item.penulis.length === 0) && verif.metadata.penulis) item.penulis = verif.metadata.penulis;
      if (!item.tahun && verif.metadata.tahun) item.tahun = verif.metadata.tahun;
      if (!item.venue && verif.metadata.venue) item.venue = verif.metadata.venue;
      if (!item.url && verif.metadata.url) item.url = verif.metadata.url;
    }
  }

  // 2. Susun CSL-JSON
  const parsedAuthors = (item.penulis || []).map(p => {
    const parts = p.split(/[, ]+/).filter(Boolean);
    if (parts.length >= 2) {
      return { family: parts[0], given: parts.slice(1).join(' ') };
    }
    return { family: p };
  });

  const cslJson: Record<string, unknown> = {
    id: item.doi || 'ref-1',
    type: 'article-journal',
    title: item.judul || 'Untitled',
    author: parsedAuthors.length > 0 ? parsedAuthors : [{ family: 'Anonim' }],
    issued: item.tahun ? { 'date-parts': [[item.tahun]] } : undefined,
    'container-title': item.venue,
    volume: item.volume,
    issue: item.issue,
    page: item.halaman,
    DOI: item.doi,
    URL: item.url
  };

  try {
    const cite = new Cite(cslJson);
    const template = gaya === 'apa7' ? 'apa' : 'ieee';

    const sitasi = cite.format('bibliography', {
      format: 'text',
      template
    }).trim();

    let inText = '';
    if (gaya === 'apa7') {
      inText = cite.format('citation', { template: 'apa' }).trim();
    } else {
      inText = '[1]';
    }

    return {
      sitasi,
      in_text: inText,
      gaya,
      csl_json: cslJson
    };
  } catch (err) {
    return {
      error: {
        code: 'UPSTREAM',
        message: `Gagal memformat sitasi via citation-js: ${err instanceof Error ? err.message : String(err)}`
      }
    };
  }
}
