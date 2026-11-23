from pathlib import Path
import sys
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FOLDER = PROJECT_ROOT / "dataverse_files" / "events"
PROCESSED_FOLDER = PROJECT_ROOT / "results" / "processed"
TABLE_FOLDER = PROJECT_ROOT / "results" / "tables"
LOG_FOLDER = PROJECT_ROOT / "results" / "logs"

SEASON_FILES = [
    "IC40_exp.csv", "IC59_exp.csv", "IC79_exp.csv",
    "IC86_I_exp.csv", "IC86_II_exp.csv", "IC86_III_exp.csv",
    "IC86_IV_exp.csv", "IC86_V_exp.csv", "IC86_VI_exp.csv",
    "IC86_VII_exp.csv",
]

COLUMNS = [
    "MJD", "log10_E_GeV", "AngErr_deg", "RA_deg",
    "Dec_deg", "Azimuth_deg", "Zenith_deg",
]


def load_one_season(file_path: Path) -> pd.DataFrame:
    """Membaca satu file event IceCube berformat whitespace-delimited."""
    if not file_path.is_file():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    df = pd.read_csv(
        file_path, sep=r"\s+", comment="#", header=None,
        names=COLUMNS, engine="python"
    )
    if df.empty:
        raise ValueError(f"File kosong: {file_path.name}")

    df["Season"] = file_path.stem.replace("_exp", "")
    return df


def load_all_seasons(raw_folder: Path = RAW_FOLDER) -> pd.DataFrame:
    """Membaca sepuluh musim dan menggabungkannya menjadi satu DataFrame."""
    frames = []
    for filename in SEASON_FILES:
        df = load_one_season(raw_folder / filename)
        frames.append(df)
        print(f"[OK] {filename}: {len(df):,} event")
    return pd.concat(frames, ignore_index=True)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Menambahkan sin_dec dan menormalisasi sudut periodik pada batas 360°."""
    data = df.copy()

    # Koreksi batas periodik yang sudah teridentifikasi pada audit Minggu 1.
    data.loc[np.isclose(data["RA_deg"], 360.0), "RA_deg"] = 0.0
    data.loc[np.isclose(data["Azimuth_deg"], 360.0), "Azimuth_deg"] = 0.0

    data["sin_dec"] = np.sin(np.deg2rad(data["Dec_deg"]))
    return data


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Memeriksa nilai kosong, non-finite, dan batas fisis tanpa menghapus baris."""
    required = COLUMNS + ["Season", "sin_dec"]
    missing_columns = [col for col in required if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Kolom wajib tidak tersedia: {missing_columns}")

    print("\nNilai kosong per kolom:")
    print(df[required].isna().sum().to_string())

    nonfinite = {
        col: int((~np.isfinite(df[col])).sum())
        for col in COLUMNS
    }
    print("\nNilai non-finite per kolom numerik:")
    print(pd.Series(nonfinite).to_string())

    checks = {
        "AngErr_nonpositive": df["AngErr_deg"] <= 0,
        "RA_out_of_range": (df["RA_deg"] < 0) | (df["RA_deg"] >= 360),
        "Dec_out_of_range": (df["Dec_deg"] < -90) | (df["Dec_deg"] > 90),
        "Azimuth_out_of_range": (df["Azimuth_deg"] < 0) | (df["Azimuth_deg"] >= 360),
        "Zenith_out_of_range": (df["Zenith_deg"] < 0) | (df["Zenith_deg"] > 180),
    }

    found = []
    for reason, mask in checks.items():
        mask = mask.fillna(True)
        if mask.any():
            part = df.loc[mask, COLUMNS + ["Season"]].copy()
            part.insert(0, "Anomaly", reason)
            found.append(part)

    anomalies = (
        pd.concat(found, ignore_index=True)
        if found else pd.DataFrame(columns=["Anomaly"] + COLUMNS + ["Season"])
    )

    # Tandai baris yang memiliki NaN atau nilai non-finite, tanpa menghapusnya.
    invalid_numeric = ~np.isfinite(df[COLUMNS]).all(axis=1)
    if invalid_numeric.any():
        part = df.loc[invalid_numeric, COLUMNS + ["Season"]].copy()
        part.insert(0, "Anomaly", "Missing_or_nonfinite_numeric")
        anomalies = pd.concat([anomalies, part], ignore_index=True)

    print(f"\nJumlah baris-temuan validasi: {len(anomalies):,}")
    return anomalies


def create_season_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Ringkasan jumlah event, rentang waktu, energi, dan AngErr per musim."""
    summary = (
        df.groupby("Season", sort=False)
        .agg(
            jumlah_event=("MJD", "size"),
            mjd_min=("MJD", "min"),
            mjd_max=("MJD", "max"),
            median_log10_E_GeV=("log10_E_GeV", "median"),
            median_AngErr_deg=("AngErr_deg", "median"),
            median_Dec_deg=("Dec_deg", "median"),
            median_RA_deg=("RA_deg", "median"),
        )
        .reset_index()
    )
    summary["median_energy_GeV"] = 10 ** summary["median_log10_E_GeV"]
    return summary


def create_sin_dec_distribution(
    df: pd.DataFrame, number_of_bins: int = 40
) -> pd.DataFrame:
    """Distribusi event dalam 40 bin sin(Dec), sebagai bahan awal background."""
    values = df["sin_dec"].dropna()
    counts, edges = np.histogram(values, bins=number_of_bins, range=(-1, 1))
    return pd.DataFrame({
        "sin_dec_bin_left": edges[:-1],
        "sin_dec_bin_right": edges[1:],
        "jumlah_event": counts,
    })


def save_outputs(
    df: pd.DataFrame,
    summary: pd.DataFrame,
    anomalies: pd.DataFrame,
    sin_dec_table: pd.DataFrame,
) -> None:
    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    TABLE_FOLDER.mkdir(parents=True, exist_ok=True)
    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    parquet_path = PROCESSED_FOLDER / "events_all_seasons.parquet"
    try:
        df.to_parquet(parquet_path, index=False)
        print(f"[SAVED] {parquet_path}")
    except (ImportError, ModuleNotFoundError):
        csv_path = PROCESSED_FOLDER / "events_all_seasons.csv.gz"
        df.to_csv(csv_path, index=False, compression="gzip")
        print("[INFO] pyarrow/fastparquet belum tersedia; menggunakan CSV.GZ.")
        print(f"[SAVED] {csv_path}")
        print("Untuk Parquet: python -m pip install pyarrow")

    summary.to_csv(TABLE_FOLDER / "ringkasan_per_musim.csv", index=False)
    sin_dec_table.to_csv(TABLE_FOLDER / "distribusi_sin_dec_40_bin.csv", index=False)
    anomalies.to_csv(LOG_FOLDER / "anomali_validasi_minggu2.csv", index=False)

    print(f"[SAVED] {TABLE_FOLDER / 'ringkasan_per_musim.csv'}")
    print(f"[SAVED] {TABLE_FOLDER / 'distribusi_sin_dec_40_bin.csv'}")
    print(f"[SAVED] {LOG_FOLDER / 'anomali_validasi_minggu2.csv'}")


def main() -> None:
    print("=" * 60)
    print("ICECUBE A2 - DATA LOADER MINGGU 2")
    print("=" * 60)
    print(f"Folder data mentah: {RAW_FOLDER}")

    if not RAW_FOLDER.is_dir():
        raise FileNotFoundError(
            f"Folder data mentah tidak ditemukan: {RAW_FOLDER}\n"
            "Periksa lokasi folder dataverse_files/events atau sesuaikan RAW_FOLDER."
        )

    raw = load_all_seasons(RAW_FOLDER)
    print(f"\nTotal event sebelum transformasi: {len(raw):,}")

    processed = transform_data(raw)
    anomalies = validate_data(processed)
    summary = create_season_summary(processed)
    sin_dec_table = create_sin_dec_distribution(processed, number_of_bins=40)

    save_outputs(processed, summary, anomalies, sin_dec_table)

    print("\nRingkasan per musim:")
    print(summary[["Season", "jumlah_event", "mjd_min", "mjd_max"]].to_string(index=False))
    print("\nPipeline selesai.")
    print(f"Total event: {len(processed):,}")
    print(f"Musim terbaca: {processed['Season'].nunique()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n[ERROR] {error}", file=sys.stderr)
        raise
