
import pandas as pd
from pathlib import Path

# ==========================================
# 1. LOKASI DATA
# ==========================================

project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "dataverse_files" / "events"

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
# 2. MEMERIKSA EVENT DI LUAR BATAS
# ==========================================

daftar_anomali = {
    "IC59_exp.csv": "Azimuth_deg",
    "IC86_V_exp.csv": "RA_deg"
}

for nama_file, variabel in daftar_anomali.items():

    file_data = data_folder / nama_file

    data = pd.read_csv(
        file_data,
        sep=r"\s+",
        comment="#",
        header=None,
        names=nama_kolom
    )

    if variabel == "RA_deg":
        anomali = data[
            (data[variabel] < 0) |
            (data[variabel] >= 360)
        ]

    elif variabel == "Azimuth_deg":
        anomali = data[
            (data[variabel] < 0) |
            (data[variabel] >= 360)
        ]

    print("\n================================")
    print("FILE:", nama_file)
    print("VARIABEL:", variabel)
    print("================================")

    if anomali.empty:
        print("Tidak ditemukan anomali.")
    else:
        print(anomali.to_string(index=True))
