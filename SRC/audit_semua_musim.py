
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# 1. MENENTUKAN LOKASI DATA
# ==========================================

project_folder = Path(__file__).resolve().parent.parent

data_folder = project_folder / "dataverse_files" / "events"

result_folder = project_folder / "results"
result_folder.mkdir(exist_ok=True)

# ==========================================
# 2. MENENTUKAN NAMA KOLOM
# ==========================================

nama_kolom = [
    "MJD",
    "log10_E_GeV",
    "AngErr_deg",
    "RA_deg",
    "Dec_deg",
    "Azimuth_deg",
    "Zenith_deg"
]

# ==========================================
# 3. MEMBACA SELURUH FILE CSV
# ==========================================

daftar_file = sorted(data_folder.glob("*_exp.csv"))

print("Jumlah file ditemukan:", len(daftar_file))

if len(daftar_file) != 10:
    print("PERINGATAN: Jumlah file tidak sesuai dugaan.")
    
# ==========================================
# 4. PROSES AUDIT SETIAP MUSIM
# ==========================================

hasil_audit = []

for file in daftar_file:

    print("\nMemeriksa:", file.name)

    data = pd.read_csv(
        file,
        sep=r"\s+",
        comment="#",
        header=None,
        names=nama_kolom
    )

    # Pemeriksaan nilai kosong
    missing = data.isnull().sum().sum()

    # Pemeriksaan nilai tidak hingga
    nonfinite = np.isfinite(data.select_dtypes(
        include="number"
    )).sum().sum()

    jumlah_nonfinite = data.select_dtypes(
        include="number"
    ).size - nonfinite

    # Pemeriksaan duplikasi
    duplikat = data.duplicated().sum()

    # Pemeriksaan batas fisik
    ra_invalid = (
        (data["RA_deg"] < 0) |
        (data["RA_deg"] >= 360)
    ).sum()

    dec_invalid = (
        (data["Dec_deg"] < -90) |
        (data["Dec_deg"] > 90)
    ).sum()

    angerr_invalid = (
        data["AngErr_deg"] <= 0
    ).sum()

    azimuth_invalid = (
        (data["Azimuth_deg"] < 0) |
        (data["Azimuth_deg"] >= 360)
    ).sum()

    zenith_invalid = (
        (data["Zenith_deg"] < 0) |
        (data["Zenith_deg"] > 180)
    ).sum()

    # Menyimpan hasil pemeriksaan
    hasil_audit.append({
        "Season": file.stem,
        "Jumlah_Event": len(data),
        "Jumlah_Kolom": len(data.columns),
        "Missing_Values": missing,
        "Duplikasi": duplikat,
        "Nonfinite": jumlah_nonfinite,
        "RA_Invalid": ra_invalid,
        "Dec_Invalid": dec_invalid,
        "AngErr_Invalid": angerr_invalid,
        "Azimuth_Invalid": azimuth_invalid,
        "Zenith_Invalid": zenith_invalid,
        "MJD_Min": data["MJD"].min(),
        "MJD_Max": data["MJD"].max(),
        "Median_Energi_Log": data["log10_E_GeV"].median(),
        "Median_AngErr": data["AngErr_deg"].median()
    })

    print("Jumlah event:", len(data))
    print("Jumlah duplikasi:", duplikat)
    print("Jumlah missing values:", missing)

# ==========================================
# 5. MENAMPILKAN HASIL AUDIT
# ==========================================

hasil = pd.DataFrame(hasil_audit)

print("\n==========================================")
print("HASIL AUDIT SELURUH MUSIM ICECUBE")
print("==========================================")

print(hasil.to_string(index=False))

# ==========================================
# 6. MENYIMPAN HASIL AUDIT
# ==========================================

output_file = result_folder / "data_quality_per_season.csv"

hasil.to_csv(output_file, index=False)

print("\nHasil audit disimpan di:")
print(output_file)
