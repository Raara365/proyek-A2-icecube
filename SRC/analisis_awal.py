
import pandas as pd
from pathlib import Path

# ==========================================
# 1. MENENTUKAN LOKASI DATA
# ==========================================

project_folder = Path(__file__).resolve().parent.parent

data_folder = project_folder / "dataverse_files" / "events"

file_data = data_folder / "IC40_exp.csv"

# ==========================================
# 2. MEMERIKSA FILE
# ==========================================

print("Lokasi file:", file_data)

if not file_data.exists():
    raise FileNotFoundError("File IC40_exp.csv tidak ditemukan!")

# ==========================================
# 3. MEMBACA DATA ICECUBE
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

data = pd.read_csv(
    file_data,
    sep=r"\s+",
    comment="#",
    header=None,
    names=nama_kolom
)

# ==========================================
# 4. MENAMPILKAN LIMA DATA PERTAMA
# ==========================================

print("\n=== LIMA DATA PERTAMA ===")
print(data.head())

# ==========================================
# 5. DIMENSI DATA
# ==========================================

print("\n=== DIMENSI DATA ===")
print("Jumlah baris dan kolom:", data.shape)

# ==========================================
# 6. NAMA KOLOM
# ==========================================

print("\n=== NAMA KOLOM ===")
print(data.columns.tolist())

# ==========================================
# 7. INFORMASI DATA
# ==========================================

print("\n=== INFORMASI DATA ===")
data.info()

# ==========================================
# 8. STATISTIK DESKRIPTIF
# ==========================================

print("\n=== STATISTIK DESKRIPTIF ===")
print(data.describe())

# ==========================================
# 9. PEMERIKSAAN NILAI KOSONG
# ==========================================

print("\n=== NILAI KOSONG ===")
print(data.isnull().sum())


# ==========================================
# 10. PEMERIKSAAN KUALITAS DATA
# ==========================================

print("\n=== PEMERIKSAAN KUALITAS DATA ===")

# 1. Memeriksa duplikasi event
jumlah_duplikat = data.duplicated().sum()

print("\nJumlah baris duplikat:", jumlah_duplikat)

# 2. Memeriksa nilai tak hingga
jumlah_infinity = (~data.select_dtypes(include="number")
                   .apply(lambda kolom: kolom.map(lambda x: abs(x) != float("inf")))
                   ).sum().sum()

print("Jumlah nilai infinity:", jumlah_infinity)

# 3. Memeriksa batas fisik variabel

print("\n=== PEMERIKSAAN BATAS FISIK ===")

pemeriksaan = {
    "RA (0 sampai 360 derajat)": (
        (data["RA_deg"] >= 0) &
        (data["RA_deg"] < 360)
    ),

    "Dec (-90 sampai 90 derajat)": (
        (data["Dec_deg"] >= -90) &
        (data["Dec_deg"] <= 90)
    ),

    "AngErr (lebih besar dari 0)": (
        data["AngErr_deg"] > 0
    ),

    "Azimuth (0 sampai 360 derajat)": (
        (data["Azimuth_deg"] >= 0) &
        (data["Azimuth_deg"] < 360)
    ),

    "Zenith (0 sampai 180 derajat)": (
        (data["Zenith_deg"] >= 0) &
        (data["Zenith_deg"] <= 180)
    )
}

for nama, kondisi in pemeriksaan.items():
    print(f"{nama}: {kondisi.sum()} dari {len(data)} event valid")

# 4. Memeriksa konsistensi koordinat
selisih = abs(
    data["Zenith_deg"] - (data["Dec_deg"] + 90)
)

print("\n=== KONSISTENSI ZENITH DAN DECLINATION ===")
print("Rata-rata selisih:", selisih.mean(), "derajat")
print("Selisih maksimum:", selisih.max(), "derajat")
