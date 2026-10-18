export interface KbbiCacheItem {
    kata: string;
    status: 'tidak_baku' | 'baku' | 'tidak_diketahui' | 'perlu_cek_manusia';
    saran_baku: string;
    url_kbbi: string;
    timestamp: number;
}
export declare function getCachedWord(kata: string): KbbiCacheItem | null;
export declare function setCachedWord(kata: string, data: Omit<KbbiCacheItem, 'timestamp'>): void;
/**
 * Melakukan lookup per-kata ke portal KBBI non-resmi cepat (kbbi.web.id)
 * CATATAN KERAS: Hanya lookup per kata; dilarang scraping massal.
 */
export declare function lookupKbbiOnline(kata: string): Promise<KbbiCacheItem>;
