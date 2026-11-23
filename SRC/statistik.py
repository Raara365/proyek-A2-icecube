"""Fungsi statistik inti Jalur A (likelihood posisi saja, tingkat minimum).

Mengikuti Bab 6 dan Bab 8 (Langkah 3-4) panduan proyek.
Konvensi satuan:
  - RA, Dec, galat sudut, radius: DERAJAT pada antarmuka fungsi.
  - Di dalam S (sinyal), sigma dan psi dipakai dalam RADIAN.
  - B(dec) adalah kerapatan latar PER STERADIAN.
VERIFIKASI definisi galat sudut di README rilis (1 sigma atau radius 50%)
sebelum memakai pada data nyata.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import norm


def angsep(ra1, dec1, ra2, dec2):
    """Jarak sudut (derajat). Semua masukan dalam derajat."""
    r1, d1 = np.radians(ra1), np.radians(dec1)
    r2, d2 = np.radians(ra2), np.radians(dec2)
    c = np.sin(d1) * np.sin(d2) + np.cos(d1) * np.cos(d2) * np.cos(r1 - r2)
    return np.degrees(np.arccos(np.clip(c, -1.0, 1.0)))


def bangun_bkg_pdf(dec_deg, nbin=40):
    """B(dec) per steradian dari histogram sin(dec), seragam di RA."""
    s = np.sin(np.radians(dec_deg))
    h, tepi = np.histogram(s, bins=nbin, range=(-1.0, 1.0), density=True)

    def B(dec_query_deg):
        sq = np.sin(np.radians(dec_query_deg))
        idx = np.clip(np.digitize(sq, tepi) - 1, 0, nbin - 1)
        return h[idx] / (2.0 * np.pi)

    return B


def bangun_dlogL(ra, dec, sig_deg, src_ra, src_dec, B, radius=5.0):
    """Mengembalikan fungsi dlogL(ns) = ln L(ns) - ln L(0) dan Nd (jumlah event dekat)."""
    N = len(ra)
    psi = angsep(ra, dec, src_ra, src_dec)
    dekat = psi < radius
    Nd = int(dekat.sum())
    if Nd == 0:
        return (lambda ns: 0.0), 0
    sig = np.radians(sig_deg[dekat])
    psi_r = np.radians(psi[dekat])
    S = np.exp(-psi_r ** 2 / (2.0 * sig ** 2)) / (2.0 * np.pi * sig ** 2)
    rasio = S / B(dec[dekat])

    def dlogL(ns):
        x = ns / N
        return np.sum(np.log1p(x * (rasio - 1.0))) + (N - Nd) * np.log1p(-x)

    return dlogL, Nd


def ts_spasial(ra, dec, sig_deg, src_ra, src_dec, B, radius=5.0):
    """Mengembalikan (TS, ns_hat) dengan batas ns >= 0."""
    dlogL, Nd = bangun_dlogL(ra, dec, sig_deg, src_ra, src_dec, B, radius)
    if Nd == 0:
        return 0.0, 0.0
    hasil = minimize_scalar(lambda n: -dlogL(n), bounds=(0.0, float(Nd)), method="bounded")
    ts = 2.0 * dlogL(hasil.x)
    if ts < 1e-9:
        return 0.0, 0.0
    return float(ts), float(hasil.x)


def pseudo_ts(dec, sig_deg, src_ra, src_dec, B, M=1000, seed=42, radius=5.0):
    """TS dari M data teracak (scrambling RA). Mengembalikan array TS."""
    rng = np.random.default_rng(seed)
    out = np.empty(M)
    for k in range(M):
        ra_acak = rng.uniform(0.0, 360.0, size=len(dec))
        out[k], _ = ts_spasial(ra_acak, dec, sig_deg, src_ra, src_dec, B, radius)
    return out


def pseudo_ts_maks(dec, sig_deg, sumber, B, M=1000, seed=42, radius=5.0):
    """Untuk trial factor beberapa sumber: TS maksimum di antara `sumber`
    (list of (ra, dec)) pada tiap pseudo-experiment."""
    rng = np.random.default_rng(seed)
    out = np.empty(M)
    for k in range(M):
        ra_acak = rng.uniform(0.0, 360.0, size=len(dec))
        out[k] = max(ts_spasial(ra_acak, dec, sig_deg, ra0, dec0, B, radius)[0]
                     for ra0, dec0 in sumber)
    return out


def p_value(ts_obs, ts_bkg):
    """p = (k+1)/(M+1). Bila k = 0, laporkan p < 1/M (jangan sebut nol)."""
    k = int(np.sum(ts_bkg >= ts_obs))
    M = len(ts_bkg)
    return (k + 1) / (M + 1), k, M


def sigma_satu_sisi(p):
    return float(norm.isf(p))


def data_tiruan(N=100000, seed=1):
    rng = np.random.default_rng(seed)
    ra = rng.uniform(0.0, 360.0, N)
    dec = np.degrees(np.arcsin(rng.uniform(-1.0, 1.0, N)))  # isotropik
    ang_err = rng.uniform(0.3, 1.5, N)
    return pd.DataFrame({"ra": ra, "dec": dec, "ang_err": ang_err})


def suntik_sinyal(rng, ev, n_inj, src_ra, src_dec):
    """Ganti n_inj event acak dengan event sinyal di sekitar sumber
    (pendekatan bidang singgung; cukup untuk uji kewarasan)."""
    ev2 = ev.copy()
    idx = rng.choice(len(ev2), size=n_inj, replace=False)
    sig = ev2["ang_err"].values[idx]
    dx = rng.normal(0.0, sig)
    dy = rng.normal(0.0, sig)
    ev2.loc[ev2.index[idx], "dec"] = src_dec + dy
    ev2.loc[ev2.index[idx], "ra"] = (src_ra + dx / np.cos(np.radians(src_dec))) % 360.0
    return ev2
