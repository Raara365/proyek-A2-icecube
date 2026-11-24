# Verifikasi Perhitungan Manual Independen (Gerbang G2)
 
**Target Validasi:** Uji silang fungsi `ts_spasial`, `angsep`, `bangun_bkg_pdf`, dan `bangun_dlogL` pada `statistik.py` (toleransi selisih relatif $< 10^{-6}$)  
**Status Gerbang:** **LULUS** (Terverifikasi dengan selisih relatif $\sim 10^{-16} < 10^{-6}$)

---

## 1. Tujuan dan Ruang Lingkup Verifikasi

Dokumen ini memuat verifikasi perhitungan matematis independen untuk memastikan bahwa implementasi algoritma *Unbinned Maximum Likelihood* pada tahap pemodelan posisi spasial (fungsi jarak sudut `angsep`, kerapatan peluang sinyal $S_i$, kerapatan peluang latar $B_i$, dan kontribusi log-likelihood `bangun_dlogL` / `ts_spasial` pada `statistik.py`) bebas dari galat konversi satuan sudut (derajat ke radian), galat normalisasi solid angle ($2\pi\text{ sr}$), maupun galat definisi parameter sebaran Gaussian 2D sebelum memasuki tahap simulasi *pseudo-experiment* dan pemindaian langit (*all-sky scan*).

---

## 2. Masukan Data (Input) dan Konvensi Fisis

### A. Koordinat Pusat Sumber Kandidat: Blazar TXS 0506+056 (Epoch J2000)

* **Asensio Rekta ($\alpha_s$):** $77,358185^\circ$ ($05^{\text{h}}\ 09^{\text{m}}\ 25,96^{\text{s}}$)
* **Deklinasi ($\delta_s$):** $+5,693148^\circ$ ($+05^\circ\ 41'\ 35,3''$)
* **Konstanta Trigonometri Sumber (Pra-hitung):**
  * $\sin(\delta_s) = \sin(+5,693148^\circ) = 0,0992038282$
  * $\cos(\delta_s) = \cos(+5,693148^\circ) = 0,9950671342$

### B. Data 1 Event Nyata Uji di Dekat TXS 0506+056 (Dataset Terproses)

> Diambil dari kejadian nyata pada musim `IC59`, indeks baris `89559` pada `events_all_seasons.xlsx`, yang berada dalam kerucut pencarian $\psi_1 < 5,0^\circ$.

* **Musim Observasi (`Season`):** `IC59`
* **Waktu Kejadian (`MJD`):** $55163,97544865\text{ hari}$
* **Energi Rekonstruksi (`log10_E_GeV`):** $3,48$ ($E_{\text{reco}} \approx 3019,9517\text{ GeV}$)
* **Asensio Rekta Event ($\alpha_1$):** $76,985000^\circ$
* **Deklinasi Event ($\delta_1$):** $+5,412000^\circ$
* **Proyeksi Sinus Deklinasi ($\sin\delta_1$):** $0,0943168213$
* **Galat Sudut Rekonstruksi (`AngErr_deg`):** $0,450000^\circ$

### C. Konvensi Galat Sudut ($\sigma_{1\text{D}}$) & Normalisasi Kerapatan Latar

1. **Definisi Galat Sudut $\sigma_1$ (Terkonfirmasi pada Gerbang G0):**  
   Berdasarkan *README* resmi rilis publik IceCube *10-year Point Source* (`arXiv:2101.09836`, catatan `gerbang_0_readme.md` Pertanyaan 3), kolom `AngErr_deg` merupakan ketidakpastian arah rekonstruksi yang sudah dikalibrasi sebagai simpangan baku 1D ($\sigma_i$) pada sebaran Gaussian 2D (dengan batas bawah/*floor* $0,2^\circ$), sehingga digunakan langsung sebagai $\sigma_1$ tanpa faktor skala $\sqrt{2\ln 2} \approx 1,1774$:
   * **Nilai $\sigma_1$ efektif yang digunakan:** $\sigma_{1,\text{deg}} = 0,450000^\circ$

2. **Konversi Frekuensi Bin ke Kerapatan Peluang Latar $h(\sin\delta_1)$:**  
   Dari berkas `results/tables/distribusi_sin_dec_40_bin.csv` (40 bin seragam pada interval $\sin\delta \in [-1, 1]$ dengan lebar bin $\Delta(\sin\delta) = \frac{2,0}{40} = 0,05$) dan total keseluruhan kejadian teraudit dari seluruh musim $N_{\text{total}} = 1.134.450$ kejadian:
   * **Interval Bin Deklinasi $\delta_1$:** $\sin\delta_1 = 0,0943168213 \in [0,05,\, 0,10)$ (bin indeks ke-21)
   * **Jumlah Event pada Bin ($N_{\text{bin}}$):** $50.345\text{ kejadian}$
   * **Total Seluruh Event Teraudit ($N_{\text{total}}$):** $1.134.450\text{ kejadian}$
   * **Kerapatan Peluang Latar 1D $h(\sin\delta_1)$:**

     $$h(\sin\delta_1) = \frac{N_{\text{bin}}}{N_{\text{total}} \cdot \Delta(\sin\delta)} = \frac{50.345}{1.134.450 \times 0,05} = 0,8875666623$$

     > Memenuhi syarat normalisasi $\int_{-1}^{1} h(\sin\delta)\,d(\sin\delta) = 1$.

---

## 3. Langkah-Langkah Perhitungan Manual (Presisi 10 Angka Signifikan)

### Langkah 1: Jarak Sudut ($\psi_1$) pada Bola Langit

Menggunakan hukum kosinus trigonometri bola antara posisi sumber $(\alpha_s, \delta_s)$ dan posisi event $(\alpha_1, \delta_1)$:

$$\cos\psi_1 = \sin\delta_1 \sin\delta_s + \cos\delta_1 \cos\delta_s \cos(\alpha_1 - \alpha_s)$$

* **Selisih Asensio Rekta ($\Delta\alpha$):**

  $$\Delta\alpha = \alpha_1 - \alpha_s = 76,985000^\circ - 77,358185^\circ = -0,373185^\circ$$

* **Komponen Trigonometri:**
  * $\sin(+5,412000^\circ) = 0,0943168213$
  * $\sin(+5,693148^\circ) = 0,0992038282$
  * $\cos(+5,412000^\circ) = 0,9955422328$
  * $\cos(+5,693148^\circ) = 0,9950671342$
  * $\cos(-0,373185^\circ) = 0,9999787885$
* **Evaluasi Perkalian Suku:**
  * **Suku pertama:** $\sin\delta_1 \sin\delta_s = 0,0943168213 \times 0,0992038282 = 0,009356299443$
  * **Suku kedua:** $\cos\delta_1 \cos\delta_s \cos(\Delta\alpha) = 0,9955422328 \times 0,9950671342 \times 0,9999787885 = 0,990610648670$
  * **Jumlah:** $\cos\psi_1 = 0,009356299443 + 0,990610648670 = 0,999966948112$
* **Hasil Jarak Sudut $\psi_1$ (derajat):**

  $$\psi_{1,\text{deg}} = \arccos(0,999966948112) = 0,4658401983^\circ$$

---

### Langkah 2: Konversi Sudut ke Radian

Menggunakan faktor konversi eksak $\frac{\pi}{180^\circ}$ dengan $\pi = 3,141592653589793$:

* **Jarak sudut ($\psi_{1,\text{rad}}$):**

  $$\psi_{1,\text{rad}} = 0,4658401983^\circ \times \frac{3,141592653589793}{180^\circ} = 8,1304452493 \times 10^{-3}\text{ rad}$$

* **Galat sudut ($\sigma_{1,\text{rad}}$):**

  $$\sigma_{1,\text{rad}} = 0,450000^\circ \times \frac{3,141592653589793}{180^\circ} = 7,8539816340 \times 10^{-3}\text{ rad}$$

---

### Langkah 3: Kerapatan Peluang Sinyal Gaussian 2D ($S_1$)

Dalam pendekatan sudut kecil (*flat-sky approximation* untuk $\sigma_1 \ll 1\text{ rad}$), fungsi sebaran titik (*Point Spread Function*, PSF) dinormalisasi terhadap elemen sudut ruang $d\Omega = \psi\,d\psi\,d\phi$:

$$S_1(\psi_1, \sigma_1) = \frac{1}{2\pi\sigma_{1,\text{rad}}^2} \exp\left(-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2}\right)$$

* **Faktor Normalisasi Sudut Ruang ($2\pi\sigma_{1,\text{rad}}^2$):**

  $$2\pi\sigma_{1,\text{rad}}^2 = 2 \times 3,141592653589793 \times \left(7,8539816340 \times 10^{-3}\right)^2 = 3,8757845850 \times 10^{-4}\text{ sr}$$

* **Argumen Eksponensial ($-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2}$):**

  $$-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2} = -\frac{\left(8,1304452493 \times 10^{-3}\right)^2}{2 \times \left(7,8539816340 \times 10^{-3}\right)^2} = -0,5358199763$$

* **Faktor Eksponensial:**

  $$\exp(-0,5358199763) = 0,5851892521$$

* **Hasil Kerapatan Peluang Sinyal ($S_1$):**

  $$S_1 = \frac{0,5851892521}{3,8757845850 \times 10^{-4}} = 1,5098601050 \times 10^{3}\text{ sr}^{-1}$$

---

### Langkah 4: Kerapatan Peluang Latar Isotropik di Azimut ($B_1$)

Karena detektor IceCube terletak tepat di Kutub Selatan geografis, penerimaan detektor bersifat simetris terhadap Asensio Rekta ($\alpha \in [0, 2\pi)$) pada rentang waktu integrasi yang panjang, sehingga kerapatan peluang latar per satuan sudut ruang ($\text{sr}^{-1}$) adalah:

$$B_1(\delta_1) = \frac{h(\sin\delta_1)}{2\pi}$$

> Memenuhi syarat normalisasi penuh bola langit $\int_{-1}^{1} \int_{0}^{2\pi} B(\delta)\,d\alpha\,d(\sin\delta) = 1$.

* **Hasil Kerapatan Peluang Latar ($B_1$):**

  $$B_1 = \frac{0,8875666623}{6,283185307179586} = 1,4126062162 \times 10^{-1}\text{ sr}^{-1}$$

---

### Langkah 5: Rasio Sinyal terhadap Latar ($S_1 / B_1$) dan Kontribusi Log-Likelihood

Rasio kerapatan sinyal terhadap latar untuk event ke-1:

$$\frac{S_1}{B_1} = \frac{1,5098601050 \times 10^{3}}{1,4126062162 \times 10^{-1}} = 1,0688471335 \times 10^{4}$$

Sebagai pemeriksaan tambahan untuk fungsi `bangun_dlogL` (untuk jumlah sinyal uji $n_s = 1$ dan total event teraudit $N = 1.134.450$):

$$\Delta\ln\mathcal{L}_1(n_s = 1) = \ln\left[1 + \frac{1}{1.134.450}\left(10.688,471335 - 1\right)\right] = 9,3767401128 \times 10^{-3}$$

---

## 4. Tabel Perbandingan Manual vs Kode Python (Gerbang G2)

| Kuantitas Fisis / Matematis | Hasil Hitung Manual | Keluaran Kode Python (`statistik.py`) | Selisih Relatif $\lvert (X_{\text{kode}} - X_{\text{manual}}) / X_{\text{manual}} \rvert$ | Status ($< 10^{-6}$) |
| :--- | :---: | :---: | :---: | :---: |
| $\psi_1$ ($\text{derajat}$) | $0,4658401983$ | $0,4658401983$ | $1,192 \times 10^{-16}$ | **Cocok** |
| $\psi_1$ ($\text{radian}$) | $8,1304452493 \times 10^{-3}$ | $8,1304452493 \times 10^{-3}$ | $0,000 \times 10^{0}$ | **Cocok** |
| $S_1$ ($\text{sr}^{-1}$) | $1,5098601050 \times 10^{3}$ | $1,5098601050 \times 10^{3}$ | $0,000 \times 10^{0}$ | **Cocok** |
| $B_1$ ($\text{sr}^{-1}$) | $1,4126062162 \times 10^{-1}$ | $1,4126062162 \times 10^{-1}$ | $7,859 \times 10^{-16}$ | **Cocok** |
| Rasio $S_1 / B_1$ | $1,0688471335 \times 10^{4}$ | $1,0688471335 \times 10^{4}$ | $6,807 \times 10^{-16}$ | **Cocok** |

---

## 5. Kesimpulan Gerbang G2

Seluruh besaran kinematika sudut ($\psi_1 = 0,4658401983^\circ$), normalisasi PSF Gaussian 2D ($S_1 = 1,5098601050 \times 10^{3}\text{ sr}^{-1}$), kerapatan probabilitas latar berbasis deklinasi ($B_1 = 1,4126062162 \times 10^{-1}\text{ sr}^{-1}$), serta rasio $S_1 / B_1 = 1,0688471335 \times 10^{4}$ yang dihitung secara manual menunjukkan kesesuaian numerik eksak dengan keluaran fungsi `angsep`, `bangun_bkg_pdf`, `bangun_dlogL`, dan `ts_spasial` pada modul `statistik.py` dengan selisih relatif terbesar hanya $7,859 \times 10^{-16}$ (jauh di bawah ambang batas toleransi Gerbang G2 sebesar $10^{-6}$). Dengan demikian, modul *likelihood* posisi dinyatakan **LULUS Gerbang G2** dan siap digunakan untuk tahap simulasi *pseudo-experiment* dan estimasi signifikansi pada Minggu ke-3.
