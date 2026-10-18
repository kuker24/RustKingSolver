import { execSync } from 'node:child_process';
import { CekEjaanInput, CekEjaanOutput, EjaanTemuan } from '../lib/types.js';

const TEMPAT_ARAH_ROOTS = [
  'kantor', 'rumah', 'sekolah', 'kampus', 'dalam', 'atas', 'bawah',
  'sana', 'sini', 'situ', 'mana', 'antara', 'depan', 'belakang',
  'samping', 'sebelah', 'seberang', 'tengah', 'bagian', 'ruangan',
  'kota', 'desa', 'negeri', 'daerah', 'pusat', 'sisi', 'darat', 'laut', 'udara'
];

const KATA_KERJA_PASIF_ROOTS = [
  'tulis', 'ambil', 'buat', 'baca', 'lakukan', 'kerjakan', 'temukan', 'sebut',
  'pakai', 'gunakan', 'jelaskan', 'hitung', 'uji', 'susun', 'simpulkan',
  'bandingkan', 'teliti', 'kaji', 'olah', 'ubah', 'kelola', 'analisis',
  'terapkan', 'pilih', 'cantumkan', 'sajikan', 'berikan', 'buka', 'tutup',
  'kirim', 'terima', 'mulai', 'tentukan', 'dapat', 'peroleh', 'laksanakan',
  'selesaikan', 'bentuk', 'capai', 'hasilkan', 'tinjau', 'laporkan'
];

export async function cekEjaan(input: CekEjaanInput): Promise<CekEjaanOutput> {
  const { teks, pakai_hunspell } = input;
  const temuan: EjaanTemuan[] = [];
  const mesin: string[] = ['aturan_lokal'];

  // 1. Kata depan 'di' menempel pada penunjuk tempat/arah
  const diTempatRegex = new RegExp(`\\bdi(${TEMPAT_ARAH_ROOTS.join('|')})\\b`, 'gi');
  let match: RegExpExecArray | null;
  while ((match = diTempatRegex.exec(teks)) !== null) {
    const cuplikan = match[0];
    const root = match[1];
    temuan.push({
      span: {
        mulai: match.index,
        akhir: match.index + cuplikan.length,
        cuplikan
      },
      aturan_id: 'EYD.kata_depan.di',
      pesan: `Kata depan 'di' yang menunjukkan tempat atau arah harus ditulis terpisah dari kata '${root}'.`,
      saran: [`di ${root}`],
      url_aturan: 'https://ejaan.kemendikdasmen.go.id/eyd/penulisan-kata/kata-depan/',
      keparahan: 'error'
    });
  }

  // 2. Awalan pasif 'di-' yang salah dipisah (mis. 'di tulis' -> 'ditulis')
  const diPasifRegex = new RegExp(`\\bdi\\s+(${KATA_KERJA_PASIF_ROOTS.join('|')})\\b`, 'gi');
  while ((match = diPasifRegex.exec(teks)) !== null) {
    const cuplikan = match[0];
    const verb = match[1];
    temuan.push({
      span: {
        mulai: match.index,
        akhir: match.index + cuplikan.length,
        cuplikan
      },
      aturan_id: 'EYD.imbuhan.di',
      pesan: `Awalan 'di-' pembentuk kata kerja pasif harus ditulis serangkai dengan kata '${verb}'.`,
      saran: [`di${verb}`],
      url_aturan: 'https://ejaan.kemendikdasmen.go.id/eyd/penulisan-kata/kata-turunan/',
      keparahan: 'error'
    });
  }

  // 3. Kata depan 'ke' menempel pada penunjuk arah/tujuan (hati-hati: 'keluar' adalah verba yang valid)
  const keArahRegex = new RegExp(`\\bke(${TEMPAT_ARAH_ROOTS.join('|')})\\b`, 'gi');
  while ((match = keArahRegex.exec(teks)) !== null) {
    const cuplikan = match[0];
    const root = match[1];
    temuan.push({
      span: {
        mulai: match.index,
        akhir: match.index + cuplikan.length,
        cuplikan
      },
      aturan_id: 'EYD.kata_depan.ke',
      pesan: `Kata depan 'ke' yang menunjukkan tujuan atau arah harus ditulis terpisah dari kata '${root}'.`,
      saran: [`ke ${root}`],
      url_aturan: 'https://ejaan.kemendikdasmen.go.id/eyd/penulisan-kata/kata-depan/',
      keparahan: 'error'
    });
  }

  // 4. Kata depan 'dari' menempel pada penunjuk asal (kecuali 'daripada')
  const dariAsalRegex = new RegExp(`\\bdari(${TEMPAT_ARAH_ROOTS.join('|')})\\b`, 'gi');
  while ((match = dariAsalRegex.exec(teks)) !== null) {
    const cuplikan = match[0];
    const root = match[1];
    temuan.push({
      span: {
        mulai: match.index,
        akhir: match.index + cuplikan.length,
        cuplikan
      },
      aturan_id: 'EYD.kata_depan.dari',
      pesan: `Kata depan 'dari' yang menunjukkan asal harus ditulis terpisah dari kata '${root}'.`,
      saran: [`dari ${root}`],
      url_aturan: 'https://ejaan.kemendikdasmen.go.id/eyd/penulisan-kata/kata-depan/',
      keparahan: 'error'
    });
  }

  // 5. Spasi sebelum tanda baca (mis. " ," atau " .")
  const spasiTandaBacaRegex = /\s+([,.:;?!])/g;
  while ((match = spasiTandaBacaRegex.exec(teks)) !== null) {
    const cuplikan = match[0];
    const tanda = match[1];
    temuan.push({
      span: {
        mulai: match.index,
        akhir: match.index + cuplikan.length,
        cuplikan
      },
      aturan_id: 'EYD.tanda_baca.spasi',
      pesan: `Tanda baca '${tanda}' tidak boleh didahului oleh spasi.`,
      saran: [tanda],
      url_aturan: 'https://ejaan.kemendikdasmen.go.id/eyd/tanda-baca/',
      keparahan: 'error'
    });
  }

  // 6. Elipsis (tiga titik tanpa karakter elipsis)
  const elipsisRegex = /\.{3,}/g;
  while ((match = elipsisRegex.exec(teks)) !== null) {
    const cuplikan = match[0];
    temuan.push({
      span: {
        mulai: match.index,
        akhir: match.index + cuplikan.length,
        cuplikan
      },
      aturan_id: 'EYD.tanda_baca.elipsis',
      pesan: "Disarankan menggunakan karakter elipsis tunggal '…' atau memastikan spasi sesuai kaidah EYD.",
      saran: ['…'],
      url_aturan: 'https://ejaan.kemendikdasmen.go.id/eyd/tanda-baca/tanda-elipsis/',
      keparahan: 'info'
    });
  }

  // 7. Hunspell id_ID opsional
  if (pakai_hunspell) {
    try {
      execSync('hunspell -d id_ID -v', { stdio: 'ignore' });
      mesin.push('hunspell_id');
    } catch {
      mesin.push('hunspell_unavailable');
    }
  }

  const ok = !temuan.some(t => t.keparahan === 'error');

  return {
    ok,
    ringkas: {
      jumlah_temuan: temuan.length,
      mesin
    },
    temuan
  };
}
