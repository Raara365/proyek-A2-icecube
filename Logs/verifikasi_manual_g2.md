# Verifikasi Perhitungan Manual Independen (Gerbang G2)
**Target Validasi:** Uji silang fungsi `hitung_ts_sumber` / `angsep` & `bangun_dlogL` (selisih relatif $< 10^{-6}$)

---

## 1. Masukan Data (Input)
* **Koordinat Pusat Sumber TXS 0506+056 (J2000):**
  * $\alpha_s = 77,358185^\circ$
  * $\delta_s = +5,693148^\circ$
* **Data 1 Event Nyata Terdekat dari Dataset (`[isi musim, mis. IC86-I]`):**
  * $\alpha_1 = \text{[isi RA event dalam derajat]}^\circ$
  * $\delta_1 = \text{[isi Dec event dalam derajat]}^\circ$
  * $\sigma_1 = \text{[isi ang\_err dalam derajat]}^\circ$ *(pastikan konversi dari README jika kolom berupa radius 50%)*
  * Nilai densitas latar pada bin deklinasi $\delta_1$: $h(\sin\delta_1) = \text{[isi nilai h dari histogram latar]}$

---

## 2. Langkah-Langkah Perhitungan Manual

### Langkah 1: Jarak Sudut ($\psi_1$)
Menggunakan hukum kosinus bola:
$$\cos\psi_1 = \sin\delta_1 \sin\delta_s + \cos\delta_1 \cos\delta_s \cos(\alpha_1 - \alpha_s)$$
* $\sin(\delta_1) = \text{[hitung]}$
* $\sin(+5,693148^\circ) = 0,0992038$
* $\cos(\delta_1) = \text{[hitung]}$
* $\cos(+5,693148^\circ) = 0,9950671$
* $\cos(\alpha_1 - 77,358185^\circ) = \text{[hitung]}$
* $\cos\psi_1 = \text{[jumlahkan hasil perkalian]}$
* **Hasil $\psi_1$ (derajat):** $\psi_1 = \arccos(\cos\psi_1) = \text{[hasil]}^\circ$

### Langkah 2: Konversi Sudut ke Radian
Menggunakan faktor konversi $\frac{\pi}{180^\circ}$ ($\pi \approx 3,14159265359$):
* **Jarak sudut ($\psi_1$):**
  $$\psi_{1,\text{rad}} = \psi_{1,\text{deg}} \times \frac{\pi}{180^\circ} = \text{[hasil]}\text{ rad}$$
* **Galat sudut ($\sigma_1$):**
  $$\sigma_{1,\text{rad}} = \sigma_{1,\text{deg}} \times \frac{\pi}{180^\circ} = \text{[hasil]}\text{ rad}$$

### Langkah 3: Kerapatan Peluang Sinyal Gaussian 2D ($S_1$)
$$S_1 = \frac{1}{2\pi\sigma_{1,\text{rad}}^2} \exp\left(-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2}\right)$$
* $2\pi\sigma_{1,\text{rad}}^2 = \text{[hasil]}\text{ sr}$
* $-\frac{\psi_{1,\text{rad}}^2}{2\sigma_{1,\text{rad}}^2} = \text{[hasil]}$
* **Hasil $S_1$:** $\text{[hasil]}\text{ sr}^{-1}$

### Langkah 4: Kerapatan Peluang Latar ($B_1$)
$$B_1 = \frac{h(\sin\delta_1)}{2\pi}$$
* **Hasil $B_1$:** $\frac{\text{[nilai h]}}{6,28318530718} = \text{[hasil]}\text{ sr}^{-1}$

### Langkah 5: Rasio Sinyal terhadap Latar ($S_1/B_1$)
$$\frac{S_1}{B_1} = \frac{\text{[hasil } S_1\text{]}}{\text{[hasil } B_1\text{]}} = \text{[hasil rasio]}$$

---

## 3. Tabel Perbandingan Manual vs Kode Python (Gerbang G2)

| Kuantitas | Hasil Hitung Manual | Keluaran Kode Python (`hitung_ts_sumber`) | Selisih Relatif $\left|\frac{X_{\text{kode}} - X_{\text{manual}}}{X_{\text{manual}}}\right|$ | Status ($< 10^{-6}$) |
| :--- | :--- | :--- | :--- | :--- |
| $\psi_1$ (derajat) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| $\psi_1$ (radian) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| $S_1$ ($\text{sr}^{-1}$) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| $B_1$ ($\text{sr}^{-1}$) | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |
| Rasio $S_1 / B_1$ | `[isi]` | `[isi]` | `[isi]` | `[Cocok / Tidak]` |

**Kesimpulan Gerbang G2:** `[Nyatakan bahwa fungsi likelihood posisi pada kode Python telah terverifikasi secara numerik dan siap digunakan untuk pseudo-experiment.]`
