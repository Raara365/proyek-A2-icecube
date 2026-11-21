
from pathlib import Path
import sys
import numpy as np
import pandas as pd

EVENT_COLUMNS = [
    "MJD", "log10_E_GeV", "AngErr_deg", "RA_deg",
    "Dec_deg", "Azimuth_deg", "Zenith_deg"
]

UPTIME_COLUMNS = ["MJD_start", "MJD_stop"]

SEASONS = [
    "IC40", "IC59", "IC79", "IC86_I", "IC86_II",
    "IC86_III", "IC86_IV", "IC86_V", "IC86_VI", "IC86_VII"
]


def locate_project():
    here = Path(__file__).resolve().parent

    for folder in [here, here.parent, here.parent.parent]:
        if (
            (folder / "dataverse_files" / "events").is_dir()
            and (folder / "dataverse_files" / "uptime").is_dir()
        ):
            return folder

    raise FileNotFoundError(
        "Folder dataverse_files/events atau uptime tidak ditemukan."
    )


def load_events(path):
    return pd.read_csv(
        path,
        sep=r"\s+",
        comment="#",
        header=None,
        names=EVENT_COLUMNS
    )


def load_uptime(path):
    runs = pd.read_csv(
        path,
        sep=r"\s+",
        comment="#",
        header=None,
        names=UPTIME_COLUMNS
    )

    starts = runs["MJD_start"].to_numpy(dtype=float)
    stops = runs["MJD_stop"].to_numpy(dtype=float)

    order = np.argsort(starts)
    starts = starts[order]
    stops = stops[order]

    merged_starts = []
    merged_stops = []

    for start, stop in zip(starts, stops):
        if not merged_starts or start > merged_stops[-1]:
            merged_starts.append(start)
            merged_stops.append(stop)
        else:
            merged_stops[-1] = max(merged_stops[-1], stop)

    return np.array(merged_starts), np.array(merged_stops)


def check_events(event_mjd, starts, stops):
    idx = np.searchsorted(starts, event_mjd, side="right") - 1

    valid = idx >= 0
    result = np.zeros(len(event_mjd), dtype=bool)

    positions = np.where(valid)[0]
    result[positions] = (
        event_mjd[positions] <= stops[idx[positions]]
    )

    return result


def main():
    project = locate_project()

    event_folder = project / "dataverse_files" / "events"
    uptime_folder = project / "dataverse_files" / "uptime"
    output_folder = project / "results" / "logs"

    output_folder.mkdir(parents=True, exist_ok=True)

    summaries = []
    outside_events = []

    print("=" * 65)
    print("AUDIT EVENT VS UPTIME - ICECUBE A2")
    print("=" * 65)

    for season in SEASONS:
        print(f"\nMemeriksa {season}...")

        event_file = event_folder / f"{season}_exp.csv"
        uptime_file = uptime_folder / f"{season}_exp.csv"

        if not event_file.exists():
            raise FileNotFoundError(f"File event tidak ditemukan: {event_file}")

        if not uptime_file.exists():
            raise FileNotFoundError(f"File uptime tidak ditemukan: {uptime_file}")

        events = load_events(event_file)
        starts, stops = load_uptime(uptime_file)

        status = check_events(
            events["MJD"].to_numpy(dtype=float),
            starts,
            stops
        )

        n_total = len(events)
        n_inside = int(status.sum())
        n_outside = n_total - n_inside

        summaries.append({
            "Season": season,
            "Total_events": n_total,
            "Events_in_good_run": n_inside,
            "Events_outside_good_run": n_outside,
            "Percentage_in_good_run": n_inside / n_total * 100
        })

        if n_outside > 0:
            outside = events.loc[~status].copy()
            outside.insert(0, "Season", season)
            outside_events.append(outside)

        print(f"Total event          : {n_total:,}")
        print(f"Di dalam good-run    : {n_inside:,}")
        print(f"Di luar good-run     : {n_outside:,}")

    summary_df = pd.DataFrame(summaries)

    summary_path = output_folder / "audit_event_vs_uptime.csv"
    summary_df.to_csv(summary_path, index=False)

    if outside_events:
        outside_df = pd.concat(outside_events, ignore_index=True)
    else:
        outside_df = pd.DataFrame(
            columns=["Season"] + EVENT_COLUMNS
        )

    outside_path = output_folder / "events_di_luar_good_run.csv"
    outside_df.to_csv(outside_path, index=False)

    print("\n" + "=" * 65)
    print("RINGKASAN AUDIT")
    print("=" * 65)

    print(summary_df.to_string(index=False))

    print("\nTotal seluruh event:",
          f"{summary_df['Total_events'].sum():,}")

    print("Event di luar good-run:",
          f"{summary_df['Events_outside_good_run'].sum():,}")

    print("\nFile hasil tersimpan:")
    print(summary_path)
    print(outside_path)

    print("\nAUDIT SELESAI.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nAUDIT GAGAL:")
        print(error)
        sys.exit(1)
