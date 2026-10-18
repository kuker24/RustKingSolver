/**
 * Modul pembanding kemiripan teks untuk verifikasi judul & nama penulis
 */
export declare function normalizeString(str: string): string;
export declare function levenshteinDistance(s1: string, s2: string): number;
export declare function levenshteinSimilarity(s1: string, s2: string): number;
export declare function tokenJaccardSimilarity(s1: string, s2: string): number;
/**
 * Menghitung skor kemiripan komposit antara dua judul
 */
export declare function titleSimilarity(title1: string, title2: string): number;
/**
 * Memeriksa kecocokan nama keluarga penulis
 */
export declare function authorFamilyMatch(authors1: string[], authors2: string[]): number;
