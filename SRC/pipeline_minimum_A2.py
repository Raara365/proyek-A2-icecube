"""Pipeline tingkat minimum Jalur A2 (Minggu 2, Analis Statistik).

Likelihood posisi saja untuk TXS 0506+056 dan PKS 1424+240 pada data
IceCube 10 tahun (10 musim), dengan scrambling RA dan pseudo-experiment.

Keluaran (dari akar proyek):
  Results/Tables/hasil_minimum_A2.json   semua angka + metadata (seed, versi, checksum)
  Results/Tables/tabel_TS_sumber.csv     tabel TS per sumber (pra dan pasca-trial)
  Results/Figures/distribusi_TS_pseudo.png

Contoh:
  python SRC/pipeline_minimum_A2.py --M 200               # uji cepat
  python SRC/pipeline_minimum_A2.py --M 1000              # hasil final
  python SRC/pipeline_minimum_A2.py --M 1000 --bkg per_musim
  python SRC/pipeline_minimum_A2.py --demo --M 200        # data tiruan, tanpa data nyata

PERHATIAN sebelum memakai hasil sebagai hasil resmi:
  1. AngErr dipakai LANGSUNG sebagai sigma (Gerbang 0, pertanyaan 3: README
     menyatakan sudah dikalibrasi sebagai sigma Gaussian 2D, tanpa faktor 1,1774).
     Opsi --sigma-dari-r50 hanya untuk pengujian kepekaan, bukan analisis utama.
  2. Koordinat sumber dari NED (diakses 20 November 2026).
  3. Pra-registrasi: radius 5 derajat, 40 bin, M >= 1000. Jangan diubah
     setelah melihat hasil; bila diubah, laporkan sebagai perubahan.
"""
import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.optimize import minimize_scalar
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import statistik as st  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent

NAMA_KOLOM = ["MJD", "log10_E_GeV", "AngErr_deg", "RA_deg", "Dec_deg",
              "Azimuth_deg", "Zenith_deg"]
URUTAN_MUSIM = ["IC40", "IC59", "IC79", "IC86_I", "IC86_II", "IC86_III",
                "IC86_IV", "IC86_V", "IC86_VI", "IC86_VII"]

# Koordinat J2000 dari NED (diakses 20 November 2026), sesuai Draf Data dan Metode
SUMBER = {
    "TXS 0506+056": (77.358185, 5.693148),
    "PKS 1424+240": (216.751632, 23.800010),
}

R50_KE_SIGMA = 1.1774  # radius penampung 50% = 1,1774 sigma (Gaussian 2D)


# ----------------------------------------------------------------- data
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def muat_data(folder):
    """Baca semua *_exp.csv, beri label Season, seragamkan nama kolom."""
    folder = Path(folder)
    berkas = {p.name.replace("_exp.csv", ""): p for p in folder.glob("*_exp.csv")}
    if not berkas:
        raise FileNotFoundError(f"Tidak ada *_exp.csv di {folder}")
    musim = [m for m in URUTAN_MUSIM if m in berkas] + \
            sorted(m for m in berkas if m not in URUTAN_MUSIM)
    bagian, checksum = [], {}
    for m in musim:
        d = pd.read_csv(berkas[m], sep=r"\s+", comment="#", header=None,
                        names=NAMA_KOLOM)
        d["season"] = m
        bagian.append(d)
        checksum[berkas[m].name] = sha256(berkas[m])
    df = pd.concat(bagian, ignore_index=True)
    df = df.rename(columns={"MJD": "mjd", "log10_E_GeV": "log10E",
                            "AngErr_deg": "ang_err", "RA_deg": "ra",
                            "Dec_deg": "dec", "Azimuth_deg": "azi",
                            "Zenith_deg": "zen"})
    df["ra"] = df["ra"] % 360.0  # 360,0 sama dengan 0,0 (lihat log kualitas data)
    return df, musim, checksum


def data_demo(folder, seed=123):
    """Tulis 10 berkas tiruan berformat sama dengan data asli (isotropik)."""
    jumlah = [36900, 107011, 93133, 136244, 112858, 122541, 127045,
              129311, 123657, 145750]
    rng = np.random.default_rng(seed)
    for m, n in zip(URUTAN_MUSIM, jumlah):
        dec = np.degrees(np.arcsin(rng.uniform(-1, 1, n)))
        d = pd.DataFrame({
            "MJD": np.sort(rng.uniform(54562, 58308, n)),
            "log10_E_GeV": rng.uniform(2, 5, n),
            "AngErr_deg": np.clip(rng.lognormal(np.log(0.6), 0.5, n), 0.2, 15),
            "RA_deg": rng.uniform(0, 360, n),
            "Dec_deg": dec,
            "Azimuth_deg": rng.uniform(0, 360, n),
            "Zenith_deg": dec + 90.0,
        })
        d.to_csv(Path(folder) / f"{m}_exp.csv", sep=" ", header=False, index=False)


# -------------------------------------------------- latar B(dec) per event
def bangun_B_event(df, mode="gabungan", nbin=40):
    """Mengembalikan B (per steradian) untuk TIAP event, dihitung sekali karena
    dec tidak berubah saat RA diacak.

    gabungan : satu histogram sin(dec) dari semua musim.
    per_musim: histogram per musim, dipakai untuk event musim itu
               (pendekatan: fraksi sinyal tiap musim dianggap sama dengan ns/N).
    """
    dec = df["dec"].values
    if mode == "gabungan":
        return st.bangun_bkg_pdf(dec, nbin)(dec)
    B = np.empty(len(df))
    for m in df["season"].unique():
        idx = (df["season"] == m).values
        B[idx] = st.bangun_bkg_pdf(dec[idx], nbin)(dec[idx])
    return B


# ------------------------------------------- statistik untuk satu sumber
class SumberTS:
    """Menyimpan event dalam pita deklinasi sumber. Scrambling RA mempertahankan
    dec, jadi event di luar pita tidak mungkin jatuh dalam radius; cukup
    mengacak RA event di pita. Hasilnya identik dengan mengacak semua event,
    tetapi jauh lebih cepat. N tetap jumlah event total."""

    def __init__(self, nama, ra, dec, df, B_event, N, radius, faktor_sigma):
        self.nama, self.ra0, self.dec0 = nama, ra, dec
        self.radius, self.N = radius, N
        pita = np.abs(df["dec"].values - dec) < radius
        self.ra_obs = df["ra"].values[pita]
        self.dec = df["dec"].values[pita]
        self.sig = np.radians(df["ang_err"].values[pita] * faktor_sigma)
        self.B = B_event[pita]
        self.n_pita = int(pita.sum())
        # konstanta untuk cos(psi) = sin d1 sin d2 + cos d1 cos d2 cos(dRA)
        d, d0 = np.radians(self.dec), np.radians(dec)
        self._a = np.sin(d) * np.sin(d0)
        self._b = np.cos(d) * np.cos(d0)
        self._cos_r = np.cos(np.radians(radius))

    def ts(self, ra):
        """(TS, ns_hat, Nd) untuk satu set RA."""
        c = self._a + self._b * np.cos(np.radians(ra - self.ra0))
        dekat = c > self._cos_r
        Nd = int(dekat.sum())
        if Nd == 0:
            return 0.0, 0.0, 0
        psi = np.arccos(np.clip(c[dekat], -1, 1))
        s2 = self.sig[dekat] ** 2
        rasio = np.exp(-psi ** 2 / (2 * s2)) / (2 * np.pi * s2) / self.B[dekat]
        N = self.N
        # ln L konkaf dalam ns; bila gradien di ns=0 tidak positif, TS = 0
        if (rasio.sum() - N) <= 0:
            return 0.0, 0.0, Nd

        def dlogL(ns):
            x = ns / N
            return np.sum(np.log1p(x * (rasio - 1.0))) + (N - Nd) * np.log1p(-x)

        h = minimize_scalar(lambda n: -dlogL(n), bounds=(0.0, float(Nd)),
                            method="bounded", options={"xatol": 1e-6})
        ts = 2.0 * dlogL(h.x)
        if ts < 1e-9:
            return 0.0, 0.0, Nd
        return float(ts), float(h.x), Nd

    def cek_manual(self, ns):
        """ln L(ns) - ln L(0) dihitung dengan LOOP biasa (math), untuk dicocokkan
        dengan keluaran vektor. Ini 'satu angka kunci dengan dua cara' (G2)."""
        import math
        N, tot, Nd = self.N, 0.0, 0
        for i in range(self.n_pita):
            d1, d2 = math.radians(self.dec[i]), math.radians(self.dec0)
            c = (math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2)
                 * math.cos(math.radians(self.ra_obs[i] - self.ra0)))
            psi = math.acos(max(-1.0, min(1.0, c)))
            if math.degrees(psi) < self.radius:
                Nd += 1
                S = math.exp(-psi ** 2 / (2 * self.sig[i] ** 2)) / \
                    (2 * math.pi * self.sig[i] ** 2)
                tot += math.log(1 + (ns / N) * (S / self.B[i] - 1))
        tot += (N - Nd) * math.log(1 - ns / N)
        return tot, Nd

    def dlogL_vektor(self, ns):
        c = self._a + self._b * np.cos(np.radians(self.ra_obs - self.ra0))
        dekat = c > self._cos_r
        psi = np.arccos(np.clip(c[dekat], -1, 1))
        s2 = self.sig[dekat] ** 2
        rasio = np.exp(-psi ** 2 / (2 * s2)) / (2 * np.pi * s2) / self.B[dekat]
        x = ns / self.N
        Nd = int(dekat.sum())
        return float(np.sum(np.log1p(x * (rasio - 1.0))) + (self.N - Nd) * np.log1p(-x)), Nd


# ----------------------------------------------------------------- utama
def jalankan(df, musim, checksum, M, seed, radius, nbin, bkg, faktor_sigma,
             sumber=SUMBER, kecil=False):
    N = len(df)
    B_event = bangun_B_event(df, bkg, nbin)
    S = [SumberTS(n, ra, dec, df, B_event, N, radius, faktor_sigma)
         for n, (ra, dec) in sumber.items()]

    # data asli
    obs = [s.ts(s.ra_obs) for s in S]

    # pseudo-experiment: satu seed BERBEDA untuk tiap pseudo-experiment,
    # diturunkan dari seed dasar lewat SeedSequence (dapat diulang persis)
    anak = np.random.SeedSequence(seed).spawn(M)
    ts_bkg = np.zeros((M, len(S)))
    for k in range(M):
        rng = np.random.default_rng(anak[k])
        for j, s in enumerate(S):
            ts_bkg[k, j] = s.ts(rng.uniform(0.0, 360.0, size=s.n_pita))[0]
    ts_maks_bkg = ts_bkg.max(axis=1)

    hasil = {"sumber": {}}
    ts_obs_maks = max(o[0] for o in obs)
    p_pasca, k_pasca, _ = st.p_value(ts_obs_maks, ts_maks_bkg)
    for j, s in enumerate(S):
        ts_o, ns_o, Nd_o = obs[j]
        p, kk, MM = st.p_value(ts_o, ts_bkg[:, j])
        hasil["sumber"][s.nama] = {
            "ra_deg": s.ra0, "dec_deg": s.dec0, "N_dekat_radius": Nd_o,
            "TS_obs": ts_o, "ns_hat": ns_o,
            "k": kk, "M": MM, "p_pra_trial": p,
            "p_pra_trial_batas_atas_jika_k0": (1.0 / MM) if kk == 0 else None,
            "sigma_pra_trial_satu_sisi": st.sigma_satu_sisi(p),
            "frac_TS_nol_pseudo": float(np.mean(ts_bkg[:, j] == 0.0)),
        }
    hasil["dua_sumber"] = {
        "TS_maks_obs": ts_obs_maks,
        "sumber_pemilik_TS_maks": S[int(np.argmax([o[0] for o in obs]))].nama,
        "k": k_pasca, "M": M, "p_pasca_trial": p_pasca,
        "sigma_pasca_trial_satu_sisi": st.sigma_satu_sisi(p_pasca),
        "trial_factor_efektif": p_pasca / min(h["p_pra_trial"]
                                              for h in hasil["sumber"].values()),
    }

    # angka kunci dua cara (Gerbang G2)
    cek = {}
    for s in S:
        ns_uji = 5.0
        manual, Nd_m = s.cek_manual(ns_uji)
        vek, Nd_v = s.dlogL_vektor(ns_uji)
        cek[s.nama] = {"ns_uji": ns_uji, "lnL_rasio_manual_loop": manual,
                       "lnL_rasio_vektor": vek, "selisih": abs(manual - vek),
                       "Nd_manual": Nd_m, "Nd_vektor": Nd_v,
                       "cocok": bool(abs(manual - vek) < 1e-8 and Nd_m == Nd_v)}
    hasil["cek_dua_cara"] = cek

    hasil["metadata"] = {
        "waktu_jalan": datetime.now().isoformat(timespec="seconds"),
        "seed_dasar": seed, "skema_seed": "SeedSequence(seed).spawn(M): seed berbeda tiap pseudo-experiment",
        "M": M, "radius_deg": radius, "nbin_sin_dec": nbin, "B_delta": bkg,
        "faktor_sigma_terhadap_AngErr": faktor_sigma,
        "N_event_total": N, "musim": musim,
        "event_per_musim": df["season"].value_counts().reindex(musim).to_dict(),
        "versi": {"python": sys.version.split()[0], "numpy": np.__version__,
                  "scipy": scipy.__version__, "pandas": pd.__version__},
        "checksum_sha256": checksum,
        "catatan": "Koordinat sumber dari NED (diakses 20 November 2026). AngErr dipakai langsung sebagai sigma (Gerbang 0 no. 3)."
    }
    return hasil, ts_bkg, ts_maks_bkg


def simpan(hasil, ts_bkg, ts_maks_bkg, nama_sumber):
    tab = RAIZ / "Results" / "Tables"
    fig = RAIZ / "Results" / "Figures"
    tab.mkdir(parents=True, exist_ok=True)
    fig.mkdir(parents=True, exist_ok=True)
    with open(tab / "hasil_minimum_A2.json", "w", encoding="utf-8") as f:
        json.dump(hasil, f, indent=2, ensure_ascii=False, default=float)

    baris = []
    for n, h in hasil["sumber"].items():
        baris.append({
            "sumber": n, "TS_obs": round(h["TS_obs"], 3),
            "ns_hat": round(h["ns_hat"], 3), "N_dekat": h["N_dekat_radius"],
            "k": h["k"], "M": h["M"],
            "p_pra_trial": (f"< {1/h['M']:.3g}" if h["k"] == 0 else f"{h['p_pra_trial']:.4g}"),
            "sigma_pra_trial (satu sisi)": round(h["sigma_pra_trial_satu_sisi"], 2),
        })
    d = hasil["dua_sumber"]
    baris.append({
        "sumber": "dua sumber (TS maks)", "TS_obs": round(d["TS_maks_obs"], 3),
        "ns_hat": "", "N_dekat": "", "k": d["k"], "M": d["M"],
        "p_pra_trial": (f"< {1/d['M']:.3g} (pasca-trial)" if d["k"] == 0
                        else f"{d['p_pasca_trial']:.4g} (pasca-trial)"),
        "sigma_pra_trial (satu sisi)": round(d["sigma_pasca_trial_satu_sisi"], 2),
    })
    pd.DataFrame(baris).to_csv(tab / "tabel_TS_sumber.csv", index=False)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fg, ax = plt.subplots(1, len(nama_sumber), figsize=(5.5 * len(nama_sumber), 4), squeeze=False)
    for j, n in enumerate(nama_sumber):
        a = ax[0, j]
        a.hist(ts_bkg[:, j][ts_bkg[:, j] > 0], bins=30, color="#7a8ba6")
        a.set_yscale("log")
        a.axvline(hasil["sumber"][n]["TS_obs"], color="crimson", lw=2,
                  label=f"TS data = {hasil['sumber'][n]['TS_obs']:.2f}")
        a.set_xlabel("TS (pseudo-experiment, hanya TS > 0)")
        a.set_ylabel("Jumlah pseudo-experiment")
        z = hasil["sumber"][n]["frac_TS_nol_pseudo"]
        a.set_title(f"{n}  (TS = 0 pada {100*z:.0f}% dari M = {len(ts_bkg)})", fontsize=10)
        a.legend()
    fg.tight_layout()
    fg.savefig(fig / "distribusi_TS_pseudo.png", dpi=200)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=str(RAIZ / "dataverse_files" / "events"))
    ap.add_argument("--M", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--radius", type=float, default=5.0)
    ap.add_argument("--nbin", type=int, default=40)
    ap.add_argument("--bkg", choices=["gabungan", "per_musim"], default="gabungan")
    ap.add_argument("--sigma-dari-r50", action="store_true",
                    help="HANYA uji kepekaan: anggap AngErr = radius 50%%, sigma = AngErr/1,1774")
    ap.add_argument("--demo", action="store_true", help="pakai data tiruan berformat sama")
    ap.add_argument("--tanpa-simpan", action="store_true")
    a = ap.parse_args()

    faktor = 1.0 / R50_KE_SIGMA if a.sigma_dari_r50 else 1.0
    tmp = None
    folder = a.data
    if a.demo:
        tmp = tempfile.TemporaryDirectory()
        folder = tmp.name
        data_demo(folder)
        print("MODE DEMO: data tiruan isotropik, BUKAN data nyata.")

    df, musim, cks = muat_data(folder)
    print(f"Dimuat {len(df):,} event dari {len(musim)} musim; B(dec) = {a.bkg}, "
          f"M = {a.M}, seed = {a.seed}, radius = {a.radius} derajat")
    hasil, tsb, tsm = jalankan(df, musim, cks, a.M, a.seed, a.radius, a.nbin,
                               a.bkg, faktor)
    for n, h in hasil["sumber"].items():
        pstr = f"< {1/h['M']:.3g}" if h["k"] == 0 else f"{h['p_pra_trial']:.4g}"
        print(f"{n}: TS = {h['TS_obs']:.3f}, ns_hat = {h['ns_hat']:.2f}, "
              f"Nd = {h['N_dekat_radius']}, p_pra = {pstr}, "
              f"Z = {h['sigma_pra_trial_satu_sisi']:.2f} sigma (satu sisi), "
              f"TS=0 pada pseudo: {100*h['frac_TS_nol_pseudo']:.0f}%")
    d = hasil["dua_sumber"]
    print(f"Dua sumber (pasca-trial): TS_maks = {d['TS_maks_obs']:.3f} "
          f"({d['sumber_pemilik_TS_maks']}), p = {d['p_pasca_trial']:.4g}, "
          f"Z = {d['sigma_pasca_trial_satu_sisi']:.2f} sigma, "
          f"trial factor efektif = {d['trial_factor_efektif']:.2f}")
    for n, c in hasil["cek_dua_cara"].items():
        print(f"Cek dua cara {n}: manual = {c['lnL_rasio_manual_loop']:.10f}, "
              f"vektor = {c['lnL_rasio_vektor']:.10f}, cocok = {c['cocok']}")
    if not a.tanpa_simpan:
        simpan(hasil, tsb, tsm, list(SUMBER))
        print("Tersimpan di Results/Tables/ dan Results/Figures/")
    if tmp:
        tmp.cleanup()


if __name__ == "__main__":
    main()
