import { z } from 'zod';
export declare const CekEjaanInputSchema: z.ZodObject<{
    teks: z.ZodString;
    pakai_hunspell: z.ZodDefault<z.ZodBoolean>;
    bahasa: z.ZodDefault<z.ZodEnum<["id"]>>;
}, "strip", z.ZodTypeAny, {
    teks: string;
    pakai_hunspell: boolean;
    bahasa: "id";
}, {
    teks: string;
    pakai_hunspell?: boolean | undefined;
    bahasa?: "id" | undefined;
}>;
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
export declare const CekBakuInputSchema: z.ZodObject<{
    teks: z.ZodString;
    fallback_kbbi: z.ZodDefault<z.ZodBoolean>;
    max_lookup: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    teks: string;
    fallback_kbbi: boolean;
    max_lookup: number;
}, {
    teks: string;
    fallback_kbbi?: boolean | undefined;
    max_lookup?: number | undefined;
}>;
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
export declare const CariRujukanInputSchema: z.ZodObject<{
    query: z.ZodString;
    sumber: z.ZodDefault<z.ZodArray<z.ZodEnum<["crossref", "openalex", "semanticscholar"]>, "many">>;
    limit: z.ZodDefault<z.ZodNumber>;
    tahun_min: z.ZodOptional<z.ZodNumber>;
    tahun_max: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    query: string;
    sumber: ("crossref" | "openalex" | "semanticscholar")[];
    limit: number;
    tahun_min?: number | undefined;
    tahun_max?: number | undefined;
}, {
    query: string;
    sumber?: ("crossref" | "openalex" | "semanticscholar")[] | undefined;
    limit?: number | undefined;
    tahun_min?: number | undefined;
    tahun_max?: number | undefined;
}>;
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
export declare const VerifikasiRujukanInputSchema: z.ZodEffects<z.ZodObject<{
    doi: z.ZodOptional<z.ZodString>;
    judul: z.ZodOptional<z.ZodString>;
    penulis: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    tahun: z.ZodOptional<z.ZodNumber>;
    url: z.ZodOptional<z.ZodString>;
    ambang_judul: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    ambang_judul: number;
    doi?: string | undefined;
    judul?: string | undefined;
    penulis?: string[] | undefined;
    tahun?: number | undefined;
    url?: string | undefined;
}, {
    doi?: string | undefined;
    judul?: string | undefined;
    penulis?: string[] | undefined;
    tahun?: number | undefined;
    url?: string | undefined;
    ambang_judul?: number | undefined;
}>, {
    ambang_judul: number;
    doi?: string | undefined;
    judul?: string | undefined;
    penulis?: string[] | undefined;
    tahun?: number | undefined;
    url?: string | undefined;
}, {
    doi?: string | undefined;
    judul?: string | undefined;
    penulis?: string[] | undefined;
    tahun?: number | undefined;
    url?: string | undefined;
    ambang_judul?: number | undefined;
}>;
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
export declare const FormatSitasiInputSchema: z.ZodObject<{
    gaya: z.ZodEnum<["apa7", "ieee"]>;
    item: z.ZodObject<{
        doi: z.ZodOptional<z.ZodString>;
        judul: z.ZodOptional<z.ZodString>;
        penulis: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        tahun: z.ZodOptional<z.ZodNumber>;
        venue: z.ZodOptional<z.ZodString>;
        volume: z.ZodOptional<z.ZodString>;
        issue: z.ZodOptional<z.ZodString>;
        halaman: z.ZodOptional<z.ZodString>;
        url: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        doi?: string | undefined;
        judul?: string | undefined;
        penulis?: string[] | undefined;
        tahun?: number | undefined;
        url?: string | undefined;
        venue?: string | undefined;
        volume?: string | undefined;
        issue?: string | undefined;
        halaman?: string | undefined;
    }, {
        doi?: string | undefined;
        judul?: string | undefined;
        penulis?: string[] | undefined;
        tahun?: number | undefined;
        url?: string | undefined;
        venue?: string | undefined;
        volume?: string | undefined;
        issue?: string | undefined;
        halaman?: string | undefined;
    }>;
    wajib_terverifikasi: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    gaya: "apa7" | "ieee";
    item: {
        doi?: string | undefined;
        judul?: string | undefined;
        penulis?: string[] | undefined;
        tahun?: number | undefined;
        url?: string | undefined;
        venue?: string | undefined;
        volume?: string | undefined;
        issue?: string | undefined;
        halaman?: string | undefined;
    };
    wajib_terverifikasi: boolean;
}, {
    gaya: "apa7" | "ieee";
    item: {
        doi?: string | undefined;
        judul?: string | undefined;
        penulis?: string[] | undefined;
        tahun?: number | undefined;
        url?: string | undefined;
        venue?: string | undefined;
        volume?: string | undefined;
        issue?: string | undefined;
        halaman?: string | undefined;
    };
    wajib_terverifikasi?: boolean | undefined;
}>;
export type FormatSitasiInput = z.infer<typeof FormatSitasiInputSchema>;
export interface FormatSitasiOutput {
    sitasi: string;
    in_text: string;
    gaya: string;
    csl_json: Record<string, unknown>;
}
export interface McpErrorEnvelope {
    error: {
        code: 'RATE_LIMITED' | 'REF_NOT_VERIFIED' | 'INVALID_INPUT' | 'UPSTREAM' | 'CACHE';
        message: string;
        retry_after_ms?: number;
    };
}
