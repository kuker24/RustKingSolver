import { z } from 'zod';

// Tool 1: cek_ejaan
export const CekEjaanInputSchema = z.object({
  teks: z.string().min(1, 'Teks tidak boleh kosong'),
  pakai_hunspell: z.boolean().default(false),
  bahasa: z.enum(['id']).default('id')
});

export type CekEjaanInput = z.infer<typeof CekEjaanInputSchema>;

export interface EjaanTemuan {
  span: {
    mulai: number;
    akhir: number;
    cuplikan: string;
  };
  aturan_id: string;
  pesan: string;
  saran: string[];
  url_aturan?: string;
  keparahan: 'info' | 'peringatan' | 'error';
}

export interface CekEjaanOutput {
  ok: boolean;
  ringkas: {
    jumlah_temuan: number;
    mesin: string[];
  };
  temuan: EjaanTemuan[];
}

// Tool 2: cek_baku
export const CekBakuInputSchema = z.object({
  teks: z.string().min(1, 'Teks tidak boleh kosong'),
  fallback_kbbi: z.boolean().default(true),
  max_lookup: z.number().int().min(1).max(50).default(20)
});

export type CekBakuInput = z.infer<typeof CekBakuInputSchema>;

export interface BakuTemuan {
  kata: string;
  status: 'tidak_baku' | 'baku' | 'tidak_diketahui' | 'perlu_cek_manusia';
  saran_baku: string;
  sumber: 'daftar_lokal' | 'cache' | 'kbbi_lookup';
  url_kbbi?: string;
}

export interface CekBakuOutput {
  ok: boolean;
  temuan: BakuTemuan[];
  lookup_tertunda: number;
}

// Tool 3: cari_rujukan
export const CariRujukanInputSchema = z.object({
  query: z.string().min(1, 'Query pencarian tidak boleh kosong'),
  sumber: z.array(z.enum(['crossref', 'openalex', 'semanticscholar'])).default(['crossref', 'openalex']),
  limit: z.number().int().min(1).max(20).default(5),
  tahun_min: z.number().int().optional(),
  tahun_max: z.number().int().optional()
});

export type CariRujukanInput = z.infer<typeof CariRujukanInputSchema>;

export interface RujukanItem {
  judul: string;
  penulis: string[];
  tahun?: number | null;
  doi?: string;
  url?: string;
  sumber: string;
  venue?: string;
}

export interface CariRujukanOutput {
  hasil: RujukanItem[];
  peringatan: string[];
}

// Tool 4: verifikasi_rujukan
export const VerifikasiRujukanInputSchema = z.object({
  doi: z.string().optional(),
  judul: z.string().optional(),
  penulis: z.array(z.string()).optional(),
  tahun: z.number().int().optional(),
  url: z.string().optional(),
  ambang_judul: z.number().min(0.5).max(1.0).default(0.85)
}).refine(data => data.doi || data.judul || data.url, {
  message: 'Minimal salah satu harus diberikan: doi, judul, atau url'
});

export type VerifikasiRujukanInput = z.infer<typeof VerifikasiRujukanInputSchema>;

export interface VerifikasiRujukanOutput {
  status: 'VALID' | 'TIDAK_COCOK' | 'TIDAK_DITEMUKAN';
  doi?: string;
  metadata?: {
    judul?: string;
    penulis?: string[];
    tahun?: number | null;
    url?: string;
    venue?: string;
  };
  kecocokan?: {
    judul_score?: number;
    penulis_score?: number;
    tahun_cocok?: boolean;
    url_hidup?: boolean;
  };
  alasan: string;
}

// Tool 5: format_sitasi
export const FormatSitasiInputSchema = z.object({
  gaya: z.enum(['apa7', 'ieee']),
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
  }),
  wajib_terverifikasi: z.boolean().default(true)
});

export type FormatSitasiInput = z.infer<typeof FormatSitasiInputSchema>;

export interface FormatSitasiOutput {
  sitasi: string;
  in_text: string;
  gaya: string;
  csl_json: Record<string, unknown>;
}

// Error envelope
export interface McpErrorEnvelope {
  error: {
    code: 'RATE_LIMITED' | 'REF_NOT_VERIFIED' | 'INVALID_INPUT' | 'UPSTREAM' | 'CACHE';
    message: string;
    retry_after_ms?: number;
  };
}
