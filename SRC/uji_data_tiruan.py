"""Uji kewarasan fungsi TS pada data tiruan (Minggu 1, Analis Statistik).

Jalankan dari akar proyek:  python src/uji_data_tiruan.py
Hasil ditulis ke results/tables/uji_data_tiruan.json
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import statistik as st

SEED = 42
N = 100000
M = 300            # kecilkan untuk uji cepat; final minimal 1000
RADIUS = 5.0
NBIN = 40
SRC1 = (77.36, 5.69)       # TXS 0506+056 (verifikasi SIMBAD)
SRC2 = (216.75, 23.80)     # PKS 1424+240 (verifikasi SIMBAD)

hasil = {"seed": SEED, "N": N, "M": M, "radius_deg": RADIUS, "nbin": NBIN}

# 1. Data isotropik tanpa sinyal
ev = st.data_tiruan(N=N, seed=1)
B = st.bangun_bkg_pdf(ev["dec"].values, nbin=NBIN)
b_rata = float(np.mean(B(np.array([-60.0, -20.0, 0.0, 20.0, 60.0]))))
hasil["B_rata"] = b_rata
hasil["B_teori_1_per_4pi"] = float(1 / (4 * np.pi))
print(f"B(dec) rata-rata = {b_rata:.4f}  (teori isotropik 1/4pi = {1/(4*np.pi):.4f})")

# 2. Distribusi TS tanpa sinyal
ts_bkg = st.pseudo_ts(ev["dec"].values, ev["ang_err"].values,
                      *SRC1, B, M=M, seed=SEED, radius=RADIUS)
frac0 = float(np.mean(ts_bkg == 0.0))
hasil["frac_TS_nol"] = frac0
hasil["TS_median"] = float(np.median(ts_bkg))
hasil["TS_p95"] = float(np.percentile(ts_bkg, 95))
hasil["TS_maks"] = float(ts_bkg.max())
print(f"Tanpa sinyal: fraksi TS=0 = {frac0:.3f} (harapan ~0,5-0,6), "
      f"persentil 95 = {hasil['TS_p95']:.2f}, maks = {ts_bkg.max():.2f}")

# 3. Injeksi sinyal: TS dan ns_hat harus naik
rng = np.random.default_rng(SEED)
hasil["injeksi"] = []
for n_inj in (0, 5, 10, 20, 40):
    ts_l, ns_l = [], []
    for _ in range(20):
        e2 = st.suntik_sinyal(rng, ev, n_inj, *SRC1) if n_inj else ev
        ts, ns = st.ts_spasial(e2["ra"].values, e2["dec"].values,
                               e2["ang_err"].values, *SRC1, B, RADIUS)
        ts_l.append(ts)
        ns_l.append(ns)
    baris = {"n_inj": n_inj, "TS_median": float(np.median(ts_l)),
             "ns_hat_median": float(np.median(ns_l))}
    hasil["injeksi"].append(baris)
    print(f"n_inj={n_inj:3d}  TS median={baris['TS_median']:8.2f}  "
          f"ns_hat median={baris['ns_hat_median']:6.2f}")

# 4. p-value dan sigma contoh (satu sisi, pra-trial), TS dari injeksi 20 event
e2 = st.suntik_sinyal(np.random.default_rng(7), ev, 20, *SRC1)
ts_obs, ns_hat = st.ts_spasial(e2["ra"].values, e2["dec"].values,
                               e2["ang_err"].values, *SRC1, B, RADIUS)
p, k, Mx = st.p_value(ts_obs, ts_bkg)
hasil["contoh_p"] = {"ts_obs": ts_obs, "ns_hat": ns_hat, "k": k, "M": Mx,
                     "p_pra_trial": p, "sigma_satu_sisi": st.sigma_satu_sisi(p)}
print(f"Contoh: TS_obs={ts_obs:.2f}, k={k}/{Mx}, p={p:.4g}, "
      f"Z={st.sigma_satu_sisi(p):.2f} sigma (satu sisi, pra-trial)")
if k == 0:
    print(f"  k = 0 -> laporkan p < 1/M = {1/Mx:.3g}")

# 5. Trial factor dua sumber (TS maksimum)
ts_maks = st.pseudo_ts_maks(ev["dec"].values, ev["ang_err"].values,
                            [SRC1, SRC2], B, M=M, seed=SEED + 1, radius=RADIUS)
hasil["dua_sumber_TS_p95"] = float(np.percentile(ts_maks, 95))
print(f"Dua sumber: persentil 95 TS maks = {hasil['dua_sumber_TS_p95']:.2f} "
      f"(vs satu sumber {hasil['TS_p95']:.2f})")

Path("results/tables").mkdir(parents=True, exist_ok=True)
with open("results/tables/uji_data_tiruan.json", "w") as f:
    json.dump(hasil, f, indent=2)
