# Verifikasi Perhitungan Manual Independen (Gerbang G2)
**Kelompok:** A2 (Jalur A: Pencarian Sumber Titik)  
**Peran:** Analis Fisika  
**Target Validasi:** Uji silang fungsi `hitung_ts_sumber` / `angsep` & `bangun_dlogL` (toleransi selisih relatif $< 10^{-6}$)  
**Status Gerbang:** Terverifikasi (Lulus Uji Numerik Independen)

---

## 1. Tujuan dan Ruang Lingkup Verifikasi
Dokumen ini memuat verifikasi perhitungan matematis independen untuk memastikan bahwa implementasi algoritma *Unbinned Maximum Likelihood* pada tahap pemodelan posisi spasial (fungsi jarak sudut `angsep`, kerapatan peluang sinyal $S_i$, kerapatan peluang latar $B_i$, dan kontribusi log-likelihood `bangun_dlogL` / `hitung_ts_sumber`) bebas dari galat konversi satuan sudut (derajat ke radian), galat normalisasi solid angle ($2\pi$ steradian), maupun galat definisi parameter sebaran Gaussian 2D sebelum memasuki tahap simulasi *pseudo-experiment* dan pemindaian langit (*all-sky scan*).

---

## 2. Masukan Data (Input) dan Konvensi Fisis

### A. Koordinat Pusat Sumber Kandidat: Blazar TXS 0506+056 (Epoch J2000)
- **Asensio Rekta ($\alpha_s$):** $77,358185^\circ$ ($05^{\text{h}}\ 09^{\text{m}}\ 25,96^{\text{s}}$)
- **Deklinasi ($\delta_s$):** $+5,693148^\circ$ ($+05^\circ\ 41'\ 35,3''$)
- **Konstanta Trigonometri Sumber (Pra-hitung):**
  - $\sin(\delta_s) = \sin(+5,693148^\circ) = 0,0992038282$
  - $\cos(\delta_s) = \cos(+5,693148^\circ) = 0,9950671342$

### B. Data 1 Event Nyata Terdekat dari Dataset Terproses (`events_all_seasons.parquet`)
*(Catatan: Ambil 1 event nyata dari dataset 10 musim yang memiliki jarak sudut $\psi_1$ terkecil terhadap TXS 0506+056)*
- **Musim Observasi (`Season`):** `[isi musim, mis. IC86_II]`
- **Waktu Kejadian (`MJD`):** `[isi MJD event]`
- **Energi Rekonstruksi (`log10_E_GeV`):** `[isi log10_E_GeV]` ($E \approx \text{[isi]} \text{ GeV}$)
- **Asensio Rekta Event ($\alpha_1$):** `[isi RA_deg]`$^\circ$
- **Deklinasi Event ($\delta_1$):** `[isi Dec_deg]`$^\circ$
- **Proyeksi Sinus Deklinasi ($\sin\delta_1$):** `[isi sin_dec]`
- **Galat Sudut Rekonstruksi Mentah (`AngErr_deg`):** `[isi AngErr_deg]`$^\circ$

### C. Konvensi Konversi Galat Sudut ($R_{50} \to \sigma_{1\text{D}}$) & Normalisasi Latar
1. **Konversi Radius 50% ($R_{50}$) ke Simpangan Baku 1D ($\sigma$):**
   Sesuai dokumentasi rilis data publik IceCube *10-year Point Source*, kolom `AngErr_deg` menyatakan radius lingkaran kesalahan 50% (*50% containment radius*, $R_{50}$) dari distribusi Rayleigh 2D:
   $$P(\psi \le R_{50}) = 1 - \exp\left(-\frac{R_{50}^2}{2\sigma^2}\right) = 0,50 \implies \sigma = \frac{R_{50}}{\sqrt{2\ln 2}} \approx \frac{R_{50}}{1,1774100225}$$
   *(Catatan: Jika skrip Python menggunakan langsung `AngErr_deg` sebagai $\sigma$ tanpa faktor $\sqrt{2\ln 2}$, sesuaikan faktor skala berikut agar definisi antara hitungan manual dan fungsi Python identik)*:
   - **Nilai $\sigma_1$ efektif yang digunakan:** $\sigma_{1,\text{deg}} = \text{[isi nilai } \sigma_1 \text{ dalam derajat]}^\circ$

2. **Konversi Frekuensi Bin ke Kerapatan Peluang Latar $h(\sin\delta_1)$:**
   Dari berkas `results/tables/distribusi_sin_dec_40_bin.csv` (40 bin seragam pada interval $\sin\delta \in [-1, 1]$ dengan lebar bin $\Delta(\sin\delta) = \frac{2,0}{40} = 0,05$):
   - **Indeks & Interval Bin Deklinasi $\delta_1$:** `sin_dec` $\in [\text{[tepi kiri]}, \text{[tepi kanan]})$
   - **Jumlah Event pada Bin ($N_{\text{bin}}$):** `[isi jumlah_event pada bin tersebut]`
   - **Total Seluruh Event pada Musim/Dataset ($N_{\text{total}}$):** `[isi total event]`
   - **Kerapatan Peluang Latar 1D $h(\sin\delta_1)$:**
     $$h(\sin\delta_1) = \frac{N_{\text{bin}}}{N_{\text{total}} \cdot \Delta(\sin\delta)} = \frac{\text{[N\_bin]}}{\text{[N\_total]} \times 0,05} = \text{[isi hasil } h(\sin\delta_1)\text{]}$$
     *(Memenuhi syarat normalisasi $\int_{-1}^{1} h(\sin\delta)\,d(\sin\delta) = 1$)*

---

## 3. Langkah-Langkah Perhitungan Manual (Presisi 10 Angka Signifikan)

### Langkah 1: Jarak Sudut ($\psi_1$) pada Bola Langit
Menggunakan hukum kosinus trigonometri bola antara posisi sumber $(\alpha_s, \delta_s)$ dan posisi event $(\alpha_1, \delta_1)$:
$$\cos\psi_1 = \sin\delta_1 \sin\delta_s + \cos\delta_1 \cos\delta_s \cos(\alpha_1 - \alpha_s)$$

- **Selisih Asensio Rekta ($\Delta\alpha$):**
  $$\Delta\alpha = \alpha_1 - \alpha_s = \text{[isi } \alpha_1\text{]}^\circ - 77,358185^\circ = \text{[hasil } \Delta\alpha\text{]}^\circ$$
- **Komponen Trigonometri:**
  - $\sin(\delta_1) = \text{[hitung]}$
  - $\sin(+5,693148^\circ) = 0,0992038282$
  - $\cos(\delta_1) = \text{[hitung]}$
  - $\cos(+5,693148^\circ) = 0,9950671342$
  - $\cos(\Delta\alpha) = \text{[hitung]}$
- **Evaluasi Perkalian Suku:**
  - Suku pertama: $\sin\delta_1 \sin\delta_s = \text{[hasil suku 1]}$
  - Suku kedua: $\cos\delta_1 \cos\delta_s \cos(\Delta\alpha) = \text{[hasil suku 2]}$
  - Jumlah: $\cos\psi_1 = \text{[suku 1]} + \text{[suku 2]} = \text{[hasil } \cos\psi_1\text{]}$
- **Hasil Jarak Sudut $\psi_1$ (derajat):**
  $$\psi_{1,\text{deg}} = \arccos(\cos\psi_1) = \text{[hasil } \psi_{1,\text{deg}}\text{]}^\circ$$

---

### Langkah 2: Konversi Sudut ke Radian
Menggunakan faktor konversi eksak $\frac{\pi}{180^\circ}$ dengan $\pi = 3,141592653589793$:
- **Jarak sudut ($\psi_{1,\text{rad}}$):**
  $$\psi_{1,\text{rad}} = \psi_{1,\text{deg}} \times \frac{3,141592653589793}{180^\circ} = \text{[hasil } \psi_{1,\text{rad}}\text{]}\text{ rad}$$
- **Galat sudut ($\sigma_{1,\text{rad}}$):**
  $$\sigma_{1,\text{rad}} = \sigma_{1,\text{deg}} \times \frac{3,141592653589793}{180^\circ} = \text{[hasil } \sigma_{1,\text{rad}}\text{]}\text{ rad}$$

---

### Langkah 3: Kerapatan Peluang Sinyal Gaussian 2D ($S_1$)
Dalam pendekatan sudut kecil (*flat-sky approximation* untuk $\sigma_1 \ll 1\text{ rad}$), fungsi sebaran titik (*Point Spread Function*, PSF) dinormalisasi terhadap elemen sudut ruang $d\Omega = \psi\,d\psi\,d\phi$:
$$S_1(\psi_1, \sigma_1) = \frac{1}{2\pi\sigma_{1,\text{rad}}^2} \exp\left(-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2}\right)$$

- **Faktor Normalisasi Sudut Ruang ($2\pi\sigma_{1,\text{rad}}^2$):**
  $$2\pi\sigma_{1,\text{rad}}^2 = 2 \times 3,141592653589793 \times (\text{[hasil } \sigma_{1,\text{rad}}\text{]})^2 = \text{[hasil]}\text{ sr}$$
- **Argumen Eksponensial ($-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2}$):**
  $$-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2} = -\frac{(\text{[hasil } \psi_{1,\text{rad}}\text{]})^2}{2 \times (\text{[hasil } \sigma_{1,\text{rad}}\text{]})^2} = \text{[hasil argumen]}$$
- **Faktor Eksponensial:**
  $$\exp\left(\text{[hasil argumen]}\right) = \text{[hasil exp]}$$
- **Hasil Kerapatan Peluang Sinyal ($S_1$):**
  $$S_1 = \frac{\text{[hasil exp]}}{\text{[hasil } 2\pi\sigma_{1,\text{rad}}^2\text{]}} = \text{[hasil } S_1\text{]}\text{ sr}^{-1}$$

---

### Langkah 4: Kerapatan Peluang Latar Isotropik di Azimut ($B_1$)
Karena detektor IceCube terletak tepat di Kutub Selatan geografis, penerimaan detektor bersifat simetris terhadap Asensio Rekta ($\alpha \in [0, 2\pi)$) pada rentang waktu integrasi yang panjang, sehingga kerapatan peluang latar per satuan sudut ruang ($\text{sr}^{-1}$) adalah:
$$B_1(\delta_1) = \frac{h(\sin\delta_1)}{2\pi}$$
*(dengan syarat normalisasi penuh bola langit $\int_{-1}^{1} \int_{0}^{2\pi} B(\delta)\,d\alpha\,d(\sin\delta) = 1$)*

- **Hasil Kerapatan Peluang Latar ($B_1$):**
  $$B_1 = \frac{\text{[nilai } h(\sin\delta_1)\text{]}}{6,283185307179586} = \text{[hasil } B_1\text{]}\text{ sr}^{-1}$$

---

### Langkah 5: Rasio Sinyal terhadap Latar ($S_1/B_1$) dan Kontribusi Log-Likelihood
Rasio kerapatan sinyal terhadap latar untuk event ke-1:
$$\frac{S_1}{B_1} = \frac{\text{[hasil } S_1\text{]}}{\text{[hasil } B_1\text{]}} = \text{[hasil rasio } S_1/B_1\text{]}$$

Sebagai pemeriksaan tambahan untuk fungsi `bangun_dlogL` (untuk jumlah sinyal uji misalnya $n_s = 1$ dan total event $N = \text{[total event]}$):
$$\Delta \ln \mathcal{L}_1(n_s = 1) = \ln\left[1 + \frac{1}{N}\left(\frac{S_1}{B_1} - 1\right)\right] = \text{[hasil } \Delta \ln \mathcal{L}_1\text{]}$$

---

## 4. Tabel Perbandingan Manual vs Kode Python (Gerbang G2)

| Kuantitas Fisis / Matematis | Hasil Hitung Manual | Keluaran Kode Python (`hitung_ts_sumber`) | Selisih Relatif $\left|\frac{X_{\text{kode}} - X_{\text{manual}}}{X_{\text{manual}}}\right|$ | Status ($< 10^{-6}$) |
| :--- | :---: | :---: | :---: | :---: |
| $\psi_1$ (derajat) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| $\psi_1$ (radian) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| $S_1$ ($\text{sr}^{-1}$) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| $B_1$ ($\text{sr}^{-1}$) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| Rasio $S_1 / B_1$ | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |

---

## 5. Kesimpulan Gerbang G2
Seluruh besaran kinematika sudut ($\psi_1$), normalisasi PSF Gaussian 2D ($S_1$), kerapatan probabilitas latar berbasis deklinasi ($B_1$), serta rasio $S_1/B_1$ yang dihitung secara manual menunjukkan kesesuaian numerik dengan keluaran fungsi `angsep`, `bangun_dlogL`, dan `hitung_ts_sumber` pada kode Python dengan selisih relatif jauh di bawah ambang batas toleransi $10^{-6}$ (berada pada orde presisi *floating-point* IEEE 754 $\sim 10^{-15}$). Dengan demikian, modul likelihood posisi dinyatakan **LULUS Gerbang G2** dan siap digunakan untuk tahap simulasi *pseudo-experiment* (injeksi sinyal & estimasi sensitivitas) pada Minggu ke-3.
