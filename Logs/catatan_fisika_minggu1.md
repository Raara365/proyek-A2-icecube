# Catatan Fisika Sumber & Perhitungan Manual Awal (Minggu 1)

---

## 1. Verifikasi Koordinat Presisi Sumber (Pra-Registrasi)
Berdasarkan penelusuran pada basis data astronomi **NASA/IPAC Extragalactic Database (NED)** pada tanggal **20 November 2026**, berikut adalah koordinat ekuatorial standar **J2000.0** dalam format derajat desimal (*Decimal Degrees*) yang dikunci sebelum perhitungan *Test Statistic* ($TS$):

| Parameter / Properti | TXS 0506+056 | PKS 1424+240 |
| :--- | :--- | :--- |
| **Nama Katalog Rujukan (NED)** | `WISEA J050925.96+054135.3` | `FBQS J142700.4+234800` |
| **Right Ascension ($\text{RA}$, J2000)** | **`77.358185°`** | **`216.751632°`** |
| **Deklinasi ($\delta$, J2000)** | **`+5.693148°`** | **`+23.800010°`** |
| **Redshift ($z$)** | $0,336500 \pm 1,00 \times 10^{-4}$ | $0,604500 \pm 2,00 \times 10^{-4}$ |
| **Klasifikasi Astrofisika** | Blazar (QSO / *Flat-Spectrum Radio Source*) | Blazar (QSO / *Flat-Spectrum Radio Source* / Objek BL Lac) |
| **Radius Pencarian Terkunci** | $5,0^\circ$ (uji kepekaan Minggu 3: $3^\circ$ dan $7^\circ$) | $5,0^\circ$ (uji kepekaan Minggu 3: $3^\circ$ dan $7^\circ$) |

---

## 2. Ringkasan Teori Astrofisika Sumber & Deteksi IceCube
1. **Mekanisme Akselerasi & Produksi Neutrino di Blazar:**
   - **TXS 0506+056** dan **PKS 1424+240** adalah *blazar*, yakni inti galaksi aktif (AGN) yang memiliki jet plasma relativistik yang mengarah hampir sejajar dengan garis pandang ke Bumi.
   - Proton atau inti atom berenergi ultra-tinggi (sinar kosmik) yang dipercepat di dalam jet bertumbukan dengan gas sekitar (interaksi hadronik $pp$) atau dengan medan foton radiasi di sekitar inti galaksi (interaksi fotohadronik $p\gamma$):
     $$pp: \quad p + p \rightarrow \pi^{\pm}, \pi^0 + X$$
     $$p\gamma: \quad p + \gamma \rightarrow \Delta^+ \rightarrow n\pi^+ \text{ atau } p\pi^0$$
   - Pion bermuatan ($\pi^\pm$) meluruh menghasilkan neutrino muon dan elektron ($\pi^+ \rightarrow \mu^+ + \nu_\mu$, diikuti $\mu^+ \rightarrow e^+ + \nu_e + \bar{\nu}_\mu$), sedangkan pion netral ($\pi^0$) meluruh menjadi sinar gamma ($\pi^0 \rightarrow \gamma\gamma$).
2. **Osilasi Neutrino Kosmik:**
   - Di sumber astrofisika, rantai peluruhan pion menghasilkan perbandingan flavor sekitar $\nu_e : \nu_\mu : \nu_\tau = 1 : 2 : 0$.
   - Karena neutrino merambat pada jarak kosmologis ($z \approx 0,34$ dan $z \approx 0,60$), osilasi neutrino mengalami perataan fase sehingga perbandingan flavor yang tiba di Bumi menjadi mendekati $1 : 1 : 1$.
3. **Deteksi Cherenkov, Topologi Track, dan Penyaringan Bumi:**
   - Dataset titik sumber 10 tahun menyeleksi event berjenis **track** dari interaksi arus bermuatan neutrino muon ($\nu_\mu + N \rightarrow \mu + X$). Muon bermuatan yang bergerak melebihi kecepatan fase cahaya di es ($\beta > 1/n$, sudut Cherenkov $\theta_c \approx 40^\circ$ pada $n \approx 1,31$) memancarkan cahaya Cherenkov biru yang direkam oleh 5.160 sensor optik IceCube.
   - Topologi *track* dipilih karena jejak muon yang panjang memberikan resolusi arah sangat presisi (orde $\sim 1^\circ$ atau lebih baik pada energi tinggi).
   - Kedua sumber terletak di belahan langit utara ($\delta > 0^\circ$). Bagi detektor IceCube di Kutub Selatan, neutrino dari langit utara datang menembus Bumi dari bawah sehingga latar belakang muon atmosfer (yang mendominasi langit selatan) sudah tersaring oleh Bumi.

---

## 3. Perhitungan Manual Awal (Referensi Validasi Kode Minggu 2)

### Bagian A: Konversi Sudut (Derajat ke Radian)
Dalam komputasi trigonometri dan rapat peluang Gaussian 2D, seluruh parameter sudut harus dikonversi dari derajat ke radian menggunakan faktor $\frac{\pi}{180^\circ}$:
1. **Koordinat TXS 0506+056:**
   $$\alpha_1 = 77,358185^\circ \times \frac{\pi}{180^\circ} = 1,350155\text{ rad}$$
   $$\delta_1 = +5,693148^\circ \times \frac{\pi}{180^\circ} = +0,099364\text{ rad}$$
2. **Koordinat PKS 1424+240:**
   $$\alpha_{\text{PKS}} = 216,751632^\circ \times \frac{\pi}{180^\circ} = 3,783030\text{ rad}$$
   $$\delta_{\text{PKS}} = +23,800010^\circ \times \frac{\pi}{180^\circ} = +0,415389\text{ rad}$$
3. **Contoh Galat Sudut Event ($\sigma_i = 0,80^\circ$):**
   $$\sigma_i = 0,80^\circ \times \frac{\pi}{180^\circ} = 0,0139626\text{ rad}$$

---

### Bagian B: Panjang Interaksi Neutrino dan Opasitas Bumi (Bab 5.1)
Untuk memahami mengapa Bumi menyaring muon atmosfer sepenuhnya namun mulai menyerap neutrino pada energi sangat tinggi (PeV), dihitung panjang interaksi $\lambda_{\text{int}}$ pada penampang lintang neutrino-nukleon $\sigma \approx 10^{-33}\text{ cm}^2$ (energi $\sim 1\text{ PeV}$):

1. **Panjang Interaksi dalam Satuan Kerapatan Kolom ($\lambda_{\text{int}}$):**
   $$\lambda_{\text{int}} = \frac{1}{\sigma N_A}$$
   Dengan bilangan Avogadro $N_A = 6,022 \times 10^{23}\text{ mol}^{-1}$:
   $$\lambda_{\text{int}} = \frac{1}{(10^{-33}\text{ cm}^2)(6,022 \times 10^{23}\text{ g}^{-1})} \approx 1,661 \times 10^9\text{ g cm}^{-2}$$

2. **Peluang Neutrino Lolos Menembus Diameter Bumi:**
   Kerapatan kolom total sepanjang diameter Bumi adalah $X \approx 1,0 \times 10^{10}\text{ g cm}^{-2}$. Maka rasio kedalaman interaksi adalah:
   $$\frac{X}{\lambda_{\text{int}}} = \frac{1,0 \times 10^{10}\text{ g cm}^{-2}}{1,661 \times 10^9\text{ g cm}^{-2}} \approx 6,02$$
   Peluang neutrino energi PeV lolos menembus diameter Bumi tanpa berinteraksi adalah:
   $$P_{\text{lolos}} = e^{-X/\lambda_{\text{int}}} = e^{-6,02} \approx 0,00243 \quad (0,24\%)$$
   *Interpretasi Fisis:* Pada energi $\sim \text{PeV}$, Bumi menjadi hampir buram bagi neutrino yang datang dari arah nadir (deklinasi utara jauh), sedangkan pada rentang energi $\text{TeV}$ (di mana penampang lintang $\sigma$ jauh lebih kecil), Bumi tetap transparan bagi neutrino namun buram total bagi muon atmosfer.

---

### Bagian C: Perhitungan Jarak Sudut ($\psi_i$) dan Rapat Sinyal Gaussian 2D ($S_i$)
Perhitungan ini disiapkan untuk menguji fungsi `angsep` dan `bangun_dlogL` pada notebook Python di Minggu 2 menggunakan koordinat presisi **TXS 0506+056**:

* **Posisi Sumber (TXS 0506+056):** $(\alpha_1, \delta_1) = (77,358185^\circ, +5,693148^\circ)$
* **Posisi Event Uji Sintetis:** $(\alpha_2, \delta_2) = (77,858185^\circ, +6,093148^\circ)$ (selisih $\Delta\alpha = 0,50^\circ$, $\Delta\delta = 0,40^\circ$)
* **Galat Sudut Event ($\sigma_i$):** $0,80^\circ = 0,0139626\text{ rad}$ (asumsi standar deviasi Gaussian $1\sigma$)

1. **Menghitung Jarak Sudut Bola ($\psi_i$):**
   $$\cos\psi_i = \sin\delta_1 \sin\delta_2 + \cos\delta_1 \cos\delta_2 \cos(\alpha_1 - \alpha_2)$$
   - $\sin(5,693148^\circ)\sin(6,093148^\circ) = (0,0992038)(0,1061442) = 0,0105299$
   - $\cos(5,693148^\circ)\cos(6,093148^\circ)\cos(0,50^\circ) = (0,9950671)(0,9943507)(0,9999619) = 0,9894080$
   - $\cos\psi_i = 0,0105299 + 0,9894080 = 0,9999379$
   $$\psi_i = \arccos(0,9999379) = 0,6382^\circ = 0,0111387\text{ rad}$$

2. **Menghitung Rapat Peluang Sinyal Gaussian 2D ($S_i$):**
   $$S_i = \frac{1}{2\pi\sigma_i^2} \exp\left(-\frac{\psi_i^2}{2\sigma_i^2}\right)$$
   - Faktor normalisasi:
     $$2\pi\sigma_i^2 = 2\pi (0,0139626\text{ rad})^2 = 1,22493 \times 10^{-3}\text{ sr}$$
   - Eksponen:
     $$-\frac{\psi_i^2}{2\sigma_i^2} = -\frac{(0,0111387)^2}{2(0,0139626)^2} = -\frac{1,24071 \times 10^{-4}}{3,89909 \times 10^{-4}} = -0,31820$$
   - Hasil akhir $S_i$:
     $$S_i = \frac{1}{1,22493 \times 10^{-3}\text{ sr}} \times e^{-0,31820} = 816,373 \times 0,72746 \approx 593,88\text{ sr}^{-1}$$

---
4. IceCube Collaboration (2018), *Neutrino emission from the direction of the blazar TXS 0506+056 prior to the IceCube-170922A alert*, Science 361, 147 (`arXiv:1807.08794`).
5. NASA/IPAC Extragalactic Database (NED), Caltech/JPL, data koordinat ekuatorial J2000 dan *redshift* objek `TXS 0506+056` serta `PKS 1424+240` (diakses 20 November 2026).
