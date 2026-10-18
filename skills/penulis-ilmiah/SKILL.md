---
name: penulis-ilmiah
description: Menulis dan memeriksa teks ilmiah Bahasa Indonesia (EYD V, kata baku KBBI) untuk esai, skripsi, jurnal SINTA, abstrak Scopus, dan proposal lomba; mencari serta memverifikasi rujukan (anti DOI/halu). Gunakan saat butuh draf ilmiah ID yang lolos ejaan/baku dan daftar pustaka terverifikasi. Bukan untuk Turnitin evasion, bukan pengganti skill academic English-first peer review penuh, bukan OCR (smartdoc).
compatibility: opencode
license: MIT
metadata:
  lang: id
  mcp: penulis-ilmiah
---

# Penulis Ilmiah

Spesialis penulisan dan penyuntingan naskah ilmiah berbahasa Indonesia berstandar EYD V dan kata baku KBBI dengan verifikasi rujukan mutlak (*fail-closed* / anti-halu sitasi).

---

## Kapan Dipakai

- Menyusun atau menyunting esai ilmiah, bab skripsi, artikel jurnal nasional (SINTA), dan proposal lomba ilmiah/kreatif berbahasa Indonesia.
- Menyusun abstrak berbahasa Inggris untuk target indeksasi Scopus **berdasarkan klaim faktual yang telah terverifikasi sumbernya**.
- Memeriksa ejaan kata depan, imbuhan, tanda baca, serta kebakuan kata Bahasa Indonesia.
- Mencari dan memverifikasi rujukan ilmiah ke Crossref, OpenAlex, atau Semantic Scholar secara sahih.

---

## Batas Tanggung Jawab

| Kebutuhan Pengguna | Rute Spesialis |
|---|---|
| Telaah metodologi, sintesis literatur global, manuskrip English-first IMRaD, dan telaah sejawat (*peer critique*) | `academic` |
| Pembersihan klise atau gaya teks AI pada prosa umum non-ilmiah | `humanizer` / `/unslop` |
| Ingest berkas (PDF/DOCX), ekstraksi tabel, OCR, dan rendering layout PDF/DOCX | `smartdoc` |
| Pengumpulan data web langsung atau dokumentasi API resmi | `research` |
| Penulisan ilmiah Bahasa Indonesia (EYD V, kata baku KBBI, anti-halu rujukan) | **`penulis-ilmiah`** |

---

## Alur Kerja (Workflow)

1. **Penentuan Format & Muat Panduan Gaya**:
   - Tentukan jenis tulisan (skripsi, esai, SINTA, proposal lomba, atau Scopus) dan rujuk panduan pada [references/gaya_tulisan.md](references/gaya_tulisan.md).
2. **Penyusunan Kerangka & Draf**:
   - Tulis draf secara lugas, objektif, dan terstruktur. Hindari frasa bergaya AI yang tercantum pada [references/frasa_terlarang.md](references/frasa_terlarang.md).
3. **Pemeriksaan Ejaan & Kebakuan Kata**:
   - Panggil tool MCP `cek_ejaan` untuk mendeteksi penulisan kata depan menempel (*di, ke, dari*), spasi sebelum tanda baca, dan elipsis sesuai kaidah [references/eyd/](references/eyd/).
   - Panggil tool MCP `cek_baku` untuk memeriksa kata tidak baku terhadap daftar [references/kata_baku.md](references/kata_baku.md).
4. **Verifikasi Rujukan (Fail-Closed)**:
   - Setiap klaim faktual, angka statistik, atau kutipan harus memiliki rujukan kandidat.
   - Panggil tool MCP `verifikasi_rujukan` untuk setiap rujukan kandidat.
   - **Hanya rujukan berstatus `VALID` yang diizinkan masuk ke dalam teks dokumen dan daftar pustaka.**
   - Rujukan berstatus `TIDAK_COCOK` atau `TIDAK_DITEMUKAN` wajib dikeluarkan dari naskah dan dimasukkan ke dalam laporan rujukan yang ditolak.
5. **Pemformatan Sitasi**:
   - Panggil tool MCP `format_sitasi` dengan gaya `apa7` atau `ieee` sesuai [references/gaya_sitasi.md](references/gaya_sitasi.md). Tool menolak memformat data yang belum lolos verifikasi (`wajib_terverifikasi=true`).
6. **Penyajian Luaran**:
   - Sajikan dokumen, daftar pustaka, dan laporan pemeriksaan secara terpisah.

---

## Aturan Keras (Hard Rules)

1. **Anti-Halu Rujukan Mutlak**:
   - Dilarang keras mengarang DOI, judul artikel, nama pengarang, tahun penerbitan, volume, halaman, atau angka data statistik.
2. **Fail-Closed Sitasi**:
   - Rujukan yang gagal verifikasi (`TIDAK_COCOK` atau `TIDAK_DITEMUKAN`) **tidak boleh** dimasukkan ke dalam daftar pustaka akhir dokumen. Cantumkan rujukan tersebut pada seksi laporan penolakan.
3. **Klaim Tanpa Sumber Wajib Ditolak atau Ditandai**:
   - Jika suatu klaim data atau kutipan tidak memiliki rujukan yang valid, hapus klaim tersebut atau tandai secara eksplisit dengan `[UNVERIFIED]` untuk diverifikasi oleh pengguna.
4. **Kebijakan KBBI On-Demand**:
   - Tidak melakukan dump kamus KBBI massal ke penyimpanan permanen. Lookup dilakukan per kata dan disimpan dalam cache lokal sementara.
5. **Tanpa Evasion Turnitin**:
   - Modul ini tidak menyediakan jalan pintas untuk memanipulasi deteksi plagiarisme atau skor Turnitin. Integritas akademis adalah prioritas utama.
6. **Status Server MCP**:
   - Jika server MCP `penulis-ilmiah` tidak terdaftar atau tidak aktif, laporkan status `NOT_CONFIGURED`. Jangan berpura-pura telah melakukan verifikasi eksternal.

---

## Format Luaran Standar

```markdown
## Dokumen
[Naskah ilmiah hasil penulisan atau penyuntingan yang bersih dari frasa klise AI dan mematuhi kaidah EYD V]

## Daftar Pustaka
[Daftar rujukan berformat APA 7th atau IEEE yang hanya memuat sumber dengan status VALID]

## Laporan Pemeriksaan
- **Temuan EYD V**: [Daftar perbaikan ejaan dan tanda baca]
- **Temuan Kata Baku**: [Daftar konversi kata baku KBBI]
- **Rujukan Terverifikasi (VALID)**: [Daftar DOI dan judul yang cocok]
- **Rujukan Ditolak (NON-VALID)**: [Daftar rujukan fiktif/tidak cocok yang disingkirkan]
- **Perlu Cek Manusia**: [Tanda [PERLU_CEK_MANUSIA] untuk konteks khusus]
```
