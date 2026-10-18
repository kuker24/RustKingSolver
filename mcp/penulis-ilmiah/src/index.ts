#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

import { cekEjaan } from './tools/cek_ejaan.js';
import { cekBaku } from './tools/cek_baku.js';
import { cariRujukan } from './tools/cari_rujukan.js';
import { verifikasiRujukan } from './tools/verifikasi_rujukan.js';
import { formatSitasi } from './tools/format_sitasi.js';

// Pastikan transport stdio saja (larang --http, 0.0.0.0)
const args = process.argv.slice(2);
if (args.includes('--http') || args.some(a => a.includes('0.0.0.0'))) {
  console.error('ERROR: Server penulis-ilmiah hanya mendukung transport lokal stdio. Flag --http dan 0.0.0.0 dilarang.');
  process.exit(1);
}

const server = new McpServer({
  name: 'penulis-ilmiah',
  version: '0.1.0'
});

// Tool 1: cek_ejaan
server.tool(
  'cek_ejaan',
  'Memeriksa ejaan EYD V (kata depan di/ke/dari menempel, imbuhan pasif dipisah, spasi tanda baca, elipsis, integrasi Hunspell opsional)',
  {
    teks: z.string().min(1, 'Teks wajib diisi'),
    pakai_hunspell: z.boolean().default(false).describe('Gunakan Hunspell id_ID bila tersedia di sistem host'),
    bahasa: z.enum(['id']).default('id').describe('Bahasa teks (default: id)')
  },
  async (params) => {
    const result = await cekEjaan(params);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
);

// Tool 2: cek_baku
server.tool(
  'cek_baku',
  'Memeriksa kata tidak baku terhadap kamus baku KBBI lokal, cache lokal, dan fallback KBBI online',
  {
    teks: z.string().min(1, 'Teks wajib diisi'),
    fallback_kbbi: z.boolean().default(true).describe('Fallback online lookup per kata jika kata belum ada di daftar lokal'),
    max_lookup: z.number().int().min(1).max(50).default(20).describe('Batas maksimal kata yang dicari ke KBBI online per panggilan')
  },
  async (params) => {
    const result = await cekBaku(params);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
);

// Tool 3: cari_rujukan
server.tool(
  'cari_rujukan',
  'Mencari publikasi ilmiah ke Crossref, OpenAlex, atau Semantic Scholar (kandidat rujukan)',
  {
    query: z.string().min(1, 'Query pencarian rujukan'),
    sumber: z.array(z.enum(['crossref', 'openalex', 'semanticscholar'])).default(['crossref', 'openalex']).describe('Basis data sumber pencarian'),
    limit: z.number().int().min(1).max(20).default(5).describe('Jumlah hasil maksimal (1-20)'),
    tahun_min: z.number().int().optional().describe('Filter tahun penerbitan minimal'),
    tahun_max: z.number().int().optional().describe('Filter tahun penerbitan maksimal')
  },
  async (params) => {
    const result = await cariRujukan(params);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
);

// Tool 4: verifikasi_rujukan
server.tool(
  'verifikasi_rujukan',
  'Memverifikasi keaslian DOI, keselarasan judul, pengarang, tahun, dan keaktifan URL secara sahih (anti-halu)',
  {
    doi: z.string().optional().describe('DOI artikel (contoh: 10.1038/nature14539)'),
    judul: z.string().optional().describe('Judul publikasi yang diklaim'),
    penulis: z.array(z.string()).optional().describe('Daftar nama penulis'),
    tahun: z.number().int().optional().describe('Tahun penerbitan'),
    url: z.string().optional().describe('URL publikasi atau DOI'),
    ambang_judul: z.number().min(0.5).max(1.0).default(0.85).describe('Ambang batas skor kemiripan judul (0.5 - 1.0)')
  },
  async (params) => {
    if (!params.doi && !params.judul && !params.url) {
      return {
        isError: true,
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              error: {
                code: 'INVALID_INPUT',
                message: 'Minimal salah satu harus diberikan: doi, judul, atau url'
              }
            }, null, 2)
          }
        ]
      };
    }
    const result = await verifikasiRujukan(params);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
);

// Tool 5: format_sitasi
server.tool(
  'format_sitasi',
  'Memformat metadata rujukan terverifikasi menjadi sitasi daftar pustaka dan sitasi dalam teks (APA 7th atau IEEE)',
  {
    gaya: z.enum(['apa7', 'ieee']).describe('Gaya sitasi: apa7 atau ieee'),
    item: z.object({
      doi: z.string().optional(),
      judul: z.string().optional(),
      penulis: z.array(z.string()).optional(),
      tahun: z.number().int().optional(),
      venue: z.string().optional(),
      volume: z.string().optional(),
      issue: z.string().optional(),
      halaman: z.string().optional(),
      url: z.string().optional()
    }).describe('Objek metadata artikel yang telah VALID'),
    wajib_terverifikasi: z.boolean().default(true).describe('Tolak pemformatan jika rujukan belum berstatus VALID (fail-closed)')
  },
  async (params) => {
    const result = await formatSitasi(params);
    if ('error' in result) {
      return {
        isError: true,
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }
        ]
      };
    }
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error('Fatal MCP error:', err);
  process.exit(1);
});
