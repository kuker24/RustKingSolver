function getMailto() {
    return process.env.CROSSREF_MAILTO || 'open-code-highend@users.noreply.github.com';
}
function getUserAgent() {
    return `OpenCodeHighEnd-PenulisIlmiah/0.1.18 (mailto:${getMailto()})`;
}
export async function fetchCrossrefWork(doi) {
    const cleanDoi = doi.replace(/^https?:\/\/doi\.org\//i, '').replace(/^doi:\s*/i, '').trim();
    const url = `https://api.crossref.org/works/${encodeURIComponent(cleanDoi)}`;
    try {
        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'User-Agent': getUserAgent(),
                'Accept': 'application/json'
            },
            signal: AbortSignal.timeout(8000)
        });
        if (res.status === 404) {
            return null;
        }
        if (res.status === 429) {
            // Tunggu sesaat jika rate limit
            await new Promise(r => setTimeout(r, 1000));
            return null;
        }
        if (!res.ok) {
            return null;
        }
        const data = await res.json();
        return data.message || null;
    }
    catch {
        return null;
    }
}
export async function searchCrossrefWorks(query, limit = 5, tahunMin, tahunMax) {
    let url = `https://api.crossref.org/works?query=${encodeURIComponent(query)}&rows=${limit}`;
    const filters = [];
    if (tahunMin)
        filters.push(`from-pub-date:${tahunMin}`);
    if (tahunMax)
        filters.push(`until-pub-date:${tahunMax}`);
    if (filters.length > 0) {
        url += `&filter=${encodeURIComponent(filters.join(','))}`;
    }
    try {
        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'User-Agent': getUserAgent(),
                'Accept': 'application/json'
            },
            signal: AbortSignal.timeout(8000)
        });
        if (!res.ok)
            return [];
        const data = await res.json();
        const items = data.message?.items || [];
        return items.map(item => {
            const year = item.issued?.['date-parts']?.[0]?.[0] || item.created?.['date-parts']?.[0]?.[0] || null;
            const authors = item.author?.map(a => `${a.family || ''}, ${a.given || ''}`.trim()).filter(Boolean) || [];
            return {
                judul: item.title?.[0] || '',
                penulis: authors,
                tahun: year,
                doi: item.DOI,
                url: item.resource?.primary?.URL || item.URL || (item.DOI ? `https://doi.org/${item.DOI}` : undefined),
                sumber: 'crossref',
                venue: item['container-title']?.[0]
            };
        });
    }
    catch {
        return [];
    }
}
