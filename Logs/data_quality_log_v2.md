# Data Quality Log v2 — IceCube A2

## Identitas
- Peran: Analis Data
- Tahap: Minggu 2
- Dataset: All-sky point-source IceCube data, 2008–2018, Version 2.0
- Cakupan: 10 musim, IC40 sampai IC86_VII
- Total event: 1.134.450

## 1. Pemuatan dan penggabungan
Sepuluh berkas event berhasil dibaca dan digabungkan menggunakan `SRC/data_loader.py`.
Jumlah event per musim:
| Musim | Jumlah event |
|---|---:|
| IC40 | 36.900 |
| IC59 | 107.011 |
| IC79 | 93.133 |
| IC86_I | 136.244 |
| IC86_II | 112.858 |
| IC86_III | 122.541 |
| IC86_IV | 127.045 |
| IC86_V | 129.311 |
| IC86_VI | 123.657 |
| IC86_VII | 145.750 |
| **Total** | **1.134.450** |

Jumlah tersebut konsisten dengan hasil audit gabungan Minggu 1.

## 2. Transformasi
- Kolom `Season` ditambahkan untuk mengidentifikasi asal musim setiap event.
- Kolom `sin_dec` dihitung menggunakan `sin(deg2rad(Dec_deg))`.
- Nilai RA=360° dan Azimuth=360° dinormalisasi menjadi 0° karena koordinat sudut tersebut periodik dan kedua nilai ekuivalen secara geometris.
- `AngErr_deg` dipertahankan dalam satuan derajat. Tidak dilakukan konversi menjadi sigma karena definisi statistik yang diperlukan belum terverifikasi.

## 3. Validasi yang dijalankan
Hasil keluaran terminal:
- Nilai kosong pada seluruh kolom yang diperiksa: 0.
- Nilai non-finite pada seluruh kolom numerik: 0.
- Temuan validasi dari pemeriksaan yang diterapkan script: 0 baris-temuan.

Pemeriksaan mencakup kelengkapan/non-finite, AngErr positif, rentang RA, Dec, Azimuth, dan Zenith. Hasil ini tidak menggantikan audit event terhadap interval good-run yang telah dilakukan pada Minggu 1. Catatan satu event IC79 di luar interval good-run secara ketat tetap dipertahankan sebagai temuan audit sebelumnya.

## 4. Ringkasan per musim
Script menghasilkan `ringkasan_per_musim.csv` yang memuat jumlah event, MJD minimum/maksimum, median log10 energi, median AngErr, median Dec, median RA, dan median energi dalam GeV.

## 5. Distribusi sin(Dec)
- Jumlah bin: 40.
- Rentang: -1 sampai +1.
- Lebar setiap bin: 0,05.
- Total hitungan pada seluruh bin: 1.134.450.
- Jumlah event minimum: 17.754 (bin pertama, -1,00 sampai -0,95).
- Jumlah event maksimum: 50.345 (bin ke-22, 0,05 sampai 0,10).

Distribusi ini adalah distribusi event teramati terhadap sin(Dec), bukan model latar belakang final. Distribusi dapat dipakai sebagai bahan awal bagi Analis Statistik untuk membangun dan menguji estimasi latar belakang, termasuk prosedur RA scrambling.

## 6. Berkas keluaran
- `SRC/data_loader.py` — script pemuatan, transformasi, validasi, dan ekspor.
- `results/processed/events_all_seasons.parquet` — dataset gabungan hasil pemrosesan.
- `results/tables/ringkasan_per_musim.csv` — ringkasan statistik per musim.
- `results/tables/distribusi_sin_dec_40_bin.csv` — hitungan event per bin sin(Dec).
- `results/tables/distribusi_sin_dec_40_bin.png` — grafik distribusi sin(Dec).
- `results/logs/anomali_validasi_minggu2.csv` — keluaran tabel anomali validasi (kosong jika tidak ada temuan).
- `results/logs/data_quality_log_v2.md` — catatan kualitas data Minggu 2.

## 7. Batasan dan tindak lanjut
1. Validasi good-run tetap merujuk pada audit Minggu 1; script Minggu 2 tidak mengulang pencocokan setiap event dengan interval uptime.
2. Tumpang tindih rentang MJD antarbeberapa musim IC86 tidak otomatis berarti duplikasi atau kesalahan. Interpretasinya perlu mengikuti dokumentasi musim dan uptime.
3. Distribusi sin(Dec) belum menjadi background PDF final. Pemodelan dan pengujian statistik merupakan pekerjaan Analis Statistik.
4. Tidak ada event yang dihapus oleh pipeline ini.

## Kesimpulan
Pipeline pemuatan dan transformasi Minggu 2 berhasil dijalankan pada 10 berkas event dengan total 1.134.450 event. Tidak ditemukan nilai kosong, non-finite, atau pelanggaran rentang yang diperiksa oleh script. Dataset olahan, ringkasan per musim, tabel distribusi sin(Dec), grafik, dan log validasi berhasil dihasilkan.
