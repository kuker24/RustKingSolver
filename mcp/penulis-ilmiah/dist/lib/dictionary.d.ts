export interface KataBakuEntry {
    tidak_baku: string;
    baku: string;
    url_kbbi: string;
    catatan: string;
    cek_manusia: boolean;
}
/**
 * Memuat dan mengurai isi kata_baku.md
 */
export declare function loadKataBaku(): {
    map: Map<string, KataBakuEntry>;
    phrases: KataBakuEntry[];
};
