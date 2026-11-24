# Catatan Gerbang 0: Verifikasi README Dataset (Jalur A2)
**Kelompok:** A2 (Pencarian Sumber Titik: TXS 0506+056 & PKS 1424+240)
**Penanggung Jawab:** Analis Fisika & Analis Data
**Dataset:** All-sky point-source IceCube data: years 2008–2018 (`PS-IC40-IC86_VII`)
**Dokumen Pendamping:** `arXiv:2101.09836`

---

## Jawaban 8 Pertanyaan Wajib Gerbang 0 (Bab 7.5 Panduan)

| No | Pertanyaan Gerbang 0 | Jawaban Berdasarkan Panduan & Dokumen Rilis (`arXiv:2101.09836`) | Status Verifikasi `README` Lokal |
| :--- | :--- | :--- | :--- |
| **1** | **Berapa berkas, apa pembagiannya (per musim/periode), dan berapa baris tiap berkas?** | Dataset terbagi menjadi **10 berkas event** (satu berkas per musim pengamatan dari April 2008 hingga Juli 2018, yakni konfigurasi IC40, IC59, IC79, dan IC86-I sampai IC86-VII), ditambah berkas luas efektif ($A_{\text{eff}}$), matriks respons detektor terbinning (*smearing matrix*), dan waktu pengamatan (*livetime*). | `[VERIFIKASI ANALIS DATA: isi jumlah baris/event eksak per berkas dari README]` |
| **2** | **Apa nama dan satuan tiap kolom?** | Posisi langit (**RA** dan **Deklinasi** dalam satuan **derajat**), galat sudut (**derajat**), energi terekonstruksi (umumnya dalam **$\log_{10}(E_{\text{reco}}/\text{GeV})$**), waktu datang (**MJD** / *Modified Julian Date*), serta koordinat lokal detektor (**Azimut** dan **Zenit** dalam **derajat**). | `[VERIFIKASI ANALIS DATA: salin nama header kolom persis & satuan dari README]` |
| **3** | **Apa makna kolom galat sudut? (1$\sigma$, radius 50%, atau lainnya?)** | Kolom galat sudut (`ang_err`) menyatakan ketidakpastian rekonstruksi arah lintasan muon. Definisi persis pada `README` wajib dipastikan (apakah standar deviasi Gaussian 2D $1\sigma$ atau radius penampung $50\%$, di mana $R_{50\%} \approx 1,177\sigma$), karena memengaruhi lebar distribusi sinyal $S_i$. | `[VERIFIKASI ANALIS DATA: pastikan keterangan 1-sigma vs 50% containment di README]` |
| **4** | **Apakah energi yang tercantum adalah energi sejati neutrino, energi terekonstruksi muon, atau energi terdeposit?** | Energi pada tabel event adalah **energi terekonstruksi muon** (proksi energi yang diprediksi dari kehilangan energi muon di dalam detektor), **bukan** energi sejati neutrino ($E_\nu$). Energi sejati neutrino hanya digunakan sebagai sumbu bin pada tabel luas efektif dan matriks respons. | Dikonfirmasi (Bab 5.2 & 7.5 Panduan) |
| **5** | **Sistem koordinat apa yang dipakai?** | Posisi sumber dan arah datang event dinyatakan dalam sistem koordinat **Ekuatorial J2000** (Right Ascension $\alpha$ dan Deklinasi $\delta$). Koordinat lokal detektor (Zenit $\theta_z$ dan Azimut) juga tersedia sebagai variabel tambahan. | Dikonfirmasi (Bab 7.5 & 8.2 Panduan) |
| **6** | **Satuan luas efektif ($\text{cm}^2$ atau $\text{m}^2$) dan definisi bin energi serta deklinasi?** | Luas efektif $A_{\text{eff}}(E_\nu, \delta)$ dirilis dalam bentuk terbinning terhadap **energi sejati neutrino** ($\log_{10} E_\nu$) dan **deklinasi** ($\sin\delta$ atau $\delta$). Satuan luas efektif pada rilis publik IceCube umumnya dalam **$\text{cm}^2$** (atau $\text{m}^2$ tergantung tabel spesifik). | `[VERIFIKASI ANALIS DATA: cek satuan cm^2 atau m^2 & batas bin pada header file A_eff]` |
| **7** | **Apakah ada keterbatasan penggunaan yang dinyatakan?** | 1. Dirancang khusus untuk **pencarian sumber titik** dan **tidak boleh** dipakai untuk analisis spektrum fluks difus.<br>2. **Dilarang digabung** dengan rilis data IceCube lainnya (termasuk rilis khusus TXS 0506+056 *Science* 2018 atau `IceTracks-DR2`).<br>3. Respons detektor dirilis dalam bentuk **terbinning kasar** (bukan simulasi Monte Carlo penuh). | Dikonfirmasi (Bab 7.2 Panduan) |
| **8** | **Apakah ada skrip, hasil acuan, atau angka benchmark untuk validasi?** | Dokumen pendamping (`arXiv:2101.09836` dan *PRL* 124, 051103) menyatakan sampel 10 tahun ini memperlihatkan **kelebihan kumulatif $3,3\sigma$** pada katalog 110 sumber potensial yang didorong oleh NGC 1068, **TXS 0506+056**, **PKS 1424+240**, dan GB6 J1542+6129. Selain itu, pembaruan pemrosesan event periode **April 2012 – Mei 2015** mengubah nilai signifikansi TXS 0506+056 dibanding analisis sebelumnya. | Dikonfirmasi (Bab 9.2 Panduan) |

---

## Checklist Keputusan Gerbang G0
- [ ] Seluruh berkas data titik sumber 2008–2018 dapat dibuka dan terbaca tanpa galat.
- [ ] Variabel wajib (`RA`, `Dec`, `ang_err`, `MJD`, `log10E`) lengkap tersedia.
- [ ] Satuan dan definisi `ang_err` pada `README` sudah diverifikasi 100% sebelum kode *likelihood* dijalankan.
- [ ] Seluruh anggota tim memahami larangan menggabung dataset dengan rilis lain.
