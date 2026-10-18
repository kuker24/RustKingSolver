import { z } from 'zod';
// Tool 1: cek_ejaan
export const CekEjaanInputSchema = z.object({
    teks: z.string().min(1, 'Teks tidak boleh kosong'),
    pakai_hunspell: z.boolean().default(false),
    bahasa: z.enum(['id']).default('id')
});
// Tool 2: cek_baku
export const CekBakuInputSchema = z.object({
    teks: z.string().min(1, 'Teks tidak boleh kosong'),
    fallback_kbbi: z.boolean().default(true),
    max_lookup: z.number().int().min(1).max(50).default(20)
});
// Tool 3: cari_rujukan
export const CariRujukanInputSchema = z.object({
    query: z.string().min(1, 'Query pencarian tidak boleh kosong'),
    sumber: z.array(z.enum(['crossref', 'openalex', 'semanticscholar'])).default(['crossref', 'openalex']),
    limit: z.number().int().min(1).max(20).default(5),
    tahun_min: z.number().int().optional(),
    tahun_max: z.number().int().optional()
});
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
