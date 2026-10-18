import { RujukanItem } from './types.js';
export interface CrossrefWorkItem {
    DOI?: string;
    title?: string[];
    author?: Array<{
        family?: string;
        given?: string;
    }>;
    issued?: {
        'date-parts'?: number[][];
    };
    created?: {
        'date-parts'?: number[][];
    };
    'container-title'?: string[];
    volume?: string;
    issue?: string;
    page?: string;
    resource?: {
        primary?: {
            URL?: string;
        };
    };
    URL?: string;
}
export declare function fetchCrossrefWork(doi: string): Promise<CrossrefWorkItem | null>;
export declare function searchCrossrefWorks(query: string, limit?: number, tahunMin?: number, tahunMax?: number): Promise<RujukanItem[]>;
