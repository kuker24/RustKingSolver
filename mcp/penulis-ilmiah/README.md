# Penulis Ilmiah MCP Server

Model Context Protocol (MCP) server lokal (transport `stdio`) untuk memeriksa kaidah penulisan ilmiah Bahasa Indonesia (EYD V, kata baku KBBI) dan memverifikasi rujukan ilmiah ke basis data resmi (Crossref, OpenAlex, Semantic Scholar).

## Fitur & Tools

1. **`cek_ejaan`**: Memeriksa ejaan EYD V (kata depan *di/ke/dari* menempel vs imbuhan pasif dipisah, spasi sebelum tanda baca, format tanda elipsis, integrasi opsional Hunspell `id_ID`).
2. **`cek_baku`**: Memeriksa kebakuan kata terhadap daftar pasangan kata baku KBBI (≥100 entri), cache lokal (`~/.cache/penulis-ilmiah/kbbi-cache.json`), dan lookup terbatas per-kata.
3. **`cari_rujukan`**: Mencari publikasi ilmiah di Crossref dan OpenAlex dengan filter tahun penerbitan.
4. **`verifikasi_rujukan`**: Memverifikasi keabsahan DOI, pencocokan skor kemiripan judul (ambang batas default 0.85), nama penulis, tahun, dan keaktifan URL secara *fail-closed*.
5. **`format_sitasi`**: Memformat rujukan yang telah `VALID` ke gaya sitasi APA 7th atau IEEE menggunakan `citation-js`. Menolak memformat rujukan yang gagal verifikasi.

## Menjalankan Server

```bash
# Menjalankan langsung via tsx
npx tsx src/index.ts

# Atau via build dist
npm run build
node dist/index.js
```

## Konfigurasi Lingkungan (Environment Variables)

- `CROSSREF_MAILTO`: Alamat surel untuk polite pool Crossref/OpenAlex. Isi dengan surel Anda sendiri (contoh: `your-email@example.com`). Jika kosong/tidak di-set, server memakai default `open-code-highend@users.noreply.github.com`.
- `OPENALEX_API_KEY`: Kunci API opsional untuk OpenAlex.
- `KBBI_RATE_PER_MIN`: Batas maksimal pencarian online KBBI per menit (default: 20).
- `PENULIS_CACHE_DIR`: Direktori penyimpanan cache (default: `~/.cache/penulis-ilmiah`).

## Dependensi & Pinning

Versi pustaka di-pin secara exact di `package.json` dan terkunci di `package-lock.json`:
- `@modelcontextprotocol/sdk`: `1.32.1`
- `citation-js`: `0.7.22`
- `zod`: `3.25.76`
