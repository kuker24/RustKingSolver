import { FormatSitasiInput, FormatSitasiOutput } from '../lib/types.js';
export declare function formatSitasi(input: FormatSitasiInput): Promise<FormatSitasiOutput | {
    error: {
        code: string;
        message: string;
    };
}>;
