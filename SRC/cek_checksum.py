from pathlib import Path
import hashlib
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "dataverse_files" / "events"
log_folder = project_folder / "results" / "logs"
log_folder.mkdir(parents=True, exist_ok=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

rows = []
for path in sorted(data_folder.glob("*.csv")):
    rows.append({
        "nama_file": path.name,
        "ukuran_byte": path.stat().st_size,
        "SHA256": sha256_file(path)
    })
    print(path.name, path.stat().st_size, rows[-1]["SHA256"])

if len(rows) != 10:
    print(f"PERINGATAN: ditemukan {len(rows)} file CSV, bukan 10.")

output = log_folder / "checksum_data_mentah.csv"
pd.DataFrame(rows).to_csv(output, index=False)
print(f"\nSelesai: {len(rows)} file. Hasil: {output}")
