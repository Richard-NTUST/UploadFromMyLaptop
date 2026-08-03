import os
import re
import sys
from dataclasses import dataclass
from datetime import timedelta

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# === Configuration ===
# Default run folder (override by passing a run dir or date: `py scripts/analyze_week3_data.py runs/2026-01-23`)
DEFAULT_RUN_DATE = "2026-01-22"

# Scoring hygiene: exclude transition seconds at segment boundaries.
# (Power is sampled every ~10s in this run; trimming 10s removes the boundary samples.)
TRIM_START_SECONDS = 10
TRIM_END_SECONDS = 10

def _resolve_paths(arg: str | None):
    if not arg:
        run_date = DEFAULT_RUN_DATE
        data_dir = f"runs/{run_date}"
    else:
        # Allow either a date like 2026-01-23 or a path like runs/2026-01-23
        candidate = arg.rstrip("/\\")
        data_dir = candidate if (os.path.sep in candidate or "/" in candidate or "\\" in candidate) else f"runs/{os.path.basename(candidate)}"

        # Prefer a YYYY-MM-DD segment as the "run_date" for output folder naming.
        # This keeps assets organized by day even when the run folder is a nested sweep (e.g., runs/2026-02-05/sweep-120233).
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", data_dir)
        run_date = date_match.group(1) if date_match else os.path.basename(data_dir)

    markers_file = f"{data_dir}/markers.md"
    if not os.path.exists(markers_file):
        markers_file = f"{data_dir}/markers.csv"
        
    power_file = f"{data_dir}/power_uw.txt"
    iperf_file = f"{data_dir}/iperf.txt"
    output_dir = f"assets/{run_date}/plots"
    return run_date, data_dir, markers_file, power_file, iperf_file, output_dir


RUN_DATE, DATA_DIR, MARKERS_FILE, POWER_FILE, IPERF_FILE, OUTPUT_DIR = _resolve_paths(sys.argv[1] if len(sys.argv) > 1 else None)

# Ensure output dir
os.makedirs(OUTPUT_DIR, exist_ok=True)


@dataclass(frozen=True)
class Interval:
    label: str
    state: str
    round: int
    start: pd.Timestamp
    end: pd.Timestamp


def _parse_marker_line(line: str):
    # Example: [2026-01-22T10:14:18Z] MARKER: Start_Initial_Idle
    match = re.match(r"^\[(?P<ts>[^\]]+)\]\s+MARKER:\s+(?P<label>.+?)\s*$", line)
    if not match:
        return None
    return match.group("ts"), match.group("label")


def load_markers():
    # Supports:
    # 1) markers.md lines like: [2026-01-22T10:14:18Z] MARKER: Start_Initial_Idle
    # 2) markers.csv lines like: 2026-02-05T12:02:34Z,Start_Initial_Idle (no header)
    if MARKERS_FILE.endswith(".csv"):
        markers = pd.read_csv(MARKERS_FILE, header=None, names=["timestamp", "label"])
        markers["timestamp"] = pd.to_datetime(markers["timestamp"], utc=True)
        markers = markers.sort_values("timestamp").reset_index(drop=True)
        return markers

    markers_list = []
    with open(MARKERS_FILE, "r", encoding="utf-8") as f:
        for raw_line in f:
            parsed = _parse_marker_line(raw_line.strip())
            if not parsed:
                continue
            ts_str, label = parsed
            markers_list.append({"timestamp": ts_str, "label": label})

    markers = pd.DataFrame(markers_list)
    markers["timestamp"] = pd.to_datetime(markers["timestamp"], utc=True)
    markers = markers.sort_values("timestamp").reset_index(drop=True)
    return markers


def _parse_iperf_receiver_bitrate(line: str):
    # Example:
    # [  5]   0.00-180.00 sec  1.11 GBytes  53.1 Mbits/sec                  receiver
    m = re.search(r"\s(?P<val>\d+(?:\.\d+)?)\s+(?P<unit>[KMG])bits/sec\s+.*receiver\s*$", line)
    if not m:
        return None
    val = float(m.group("val"))
    unit = m.group("unit")
    scale = {"K": 1e3, "M": 1e6, "G": 1e9}[unit]
    return val * scale


def write_iperf_client_summaries():
    """Summarize per-segment iperf3 client outputs (iperf_Load_*_Run*.txt) if present."""
    pattern = re.compile(r"^iperf_(?P<state>Load_[LMH])_Run(?P<round>\d+)\.txt$")
    rows = []
    try:
        filenames = os.listdir(DATA_DIR)
    except FileNotFoundError:
        return

    for filename in sorted(filenames):
        m = pattern.match(filename)
        if not m:
            continue
        state_raw = m.group("state")
        round_num = int(m.group("round"))
        state = {"Load_L": "Load-L", "Load_M": "Load-M", "Load_H": "Load-H"}[state_raw]

        filepath = os.path.join(DATA_DIR, filename)
        receiver_bps = None
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                parsed = _parse_iperf_receiver_bitrate(line)
                if parsed is not None:
                    receiver_bps = parsed

        if receiver_bps is None:
            continue

        rows.append(
            {
                "file": filename,
                "state": state,
                "round": round_num,
                "receiver_mbps": receiver_bps / 1e6,
                "receiver_gbps": receiver_bps / 1e9,
            }
        )

    if not rows:
        print("Note: No per-segment iperf client logs found (iperf_Load_*_Run*.txt).")
        return

    df = pd.DataFrame(rows).sort_values(["state", "round"]).reset_index(drop=True)
    out_path = os.path.join(DATA_DIR, "iperf_client_summary.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# iperf Summary (Client Logs)\n\n")
        f.write("This file summarizes per-segment iperf3 client outputs saved as `iperf_Load_*_Run*.txt`.\n\n")
        f.write("| File | State | Round | Receiver (Mbps) | Receiver (Gbps) |\n")
        f.write("| :--- | :--- | ---: | ---: | ---: |\n")
        for _, r in df.iterrows():
            f.write(
                f"| {r['file']} | {r['state']} | {int(r['round'])} | {r['receiver_mbps']:.2f} | {r['receiver_gbps']:.4f} |\n"
            )

    print(f"Saved iperf client summary to {out_path}")


def load_power():
    power_data = []
    with open(POWER_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            # Robust filtering for corrupted lines
            if not line or len(line) > 50:
                continue
            
            # Expect "TIMESTAMP POWER" or "TIMESTAMP,POWER"
            parts = re.split(r'[,\s]+', line)
            clean_parts = [p for p in parts if p]
            
            if len(clean_parts) >= 2:
                ts, val = clean_parts[0], clean_parts[1]
                try:
                    # Quick validation of timestamp format
                    if "T" in ts and "Z" in ts:
                        power_data.append({"timestamp": ts, "power_uw": float(val)})
                except ValueError:
                    continue

    power = pd.DataFrame(power_data)
    power["timestamp"] = pd.to_datetime(power["timestamp"], utc=True)
    power["power_w"] = power["power_uw"] / 1_000_000.0
    power = power.sort_values("timestamp").reset_index(drop=True)
    return power


def _normalize_state_from_label(raw_label: str):
    # Input label example: Load_L_Run1, Load_M_Run2, Load_H_Run3, Initial_Idle
    round_num = 0
    if "Run" in raw_label:
        match = re.search(r"Run(\d+)", raw_label)
        if match:
            round_num = int(match.group(1))

    # State normalization: Load_L -> Load-L etc.
    state = raw_label
    state = state.replace("Load_L", "Load-L")
    state = state.replace("Load_M", "Load-M")
    state = state.replace("Load_H", "Load-H")

    # Strip run suffix
    state = re.sub(r"[_-]?Run\d+", "", state).strip("_-")
    return state, round_num


def build_intervals(markers: pd.DataFrame):
    # Build explicit Start/Stop intervals (this prevents boundary contamination).
    starts = {}
    stops = {}
    for _, row in markers.iterrows():
        label = row["label"]
        ts = row["timestamp"]
        if label.startswith("Start_"):
            starts[label[len("Start_") :]] = ts
        elif label.startswith("Stop_"):
            stops[label[len("Stop_") :]] = ts

    intervals = []
    for key, start_ts in starts.items():
        end_ts = stops.get(key)
        if end_ts is None:
            continue
        state, round_num = _normalize_state_from_label(key)
        if state == "Initial_Idle":
            state = "Idle"
        intervals.append(Interval(label=key, state=state, round=round_num, start=start_ts, end=end_ts))

    intervals = sorted(intervals, key=lambda i: i.start)

    # Add explicit idle gaps between intervals (cool-down windows).
    idle_intervals = []
    for i in range(len(intervals) - 1):
        a = intervals[i]
        b = intervals[i + 1]
        if b.start <= a.end:
            continue
        inferred_round = b.round if b.round != 0 else a.round
        idle_intervals.append(
            Interval(
                label=f"Idle_between_{a.label}_and_{b.label}",
                state="Idle",
                round=inferred_round,
                start=a.end,
                end=b.start,
            )
        )

    all_intervals = sorted(intervals + idle_intervals, key=lambda i: i.start)
    return all_intervals


def label_power_by_intervals(power: pd.DataFrame, intervals, trim_start_s: int, trim_end_s: int):
    labeled = power.copy()
    labeled["state"] = "Unlabeled"
    labeled["round"] = 0
    trim_start = timedelta(seconds=trim_start_s)
    trim_end = timedelta(seconds=trim_end_s)

    for interval in intervals:
        scored_start = interval.start + trim_start
        scored_end = interval.end - trim_end
        if scored_end <= scored_start:
            continue
        mask = (labeled["timestamp"] >= scored_start) & (labeled["timestamp"] < scored_end)
        labeled.loc[mask, "state"] = interval.state
        labeled.loc[mask, "round"] = interval.round

    return labeled


def parse_iperf_tests(iperf_path: str):
    # Parses server log of iperf3; groups by "test #N" and extracts [SUM] Gbits/sec lines.
    tests = {}
    current_test = None
    sum_line = re.compile(
        r"^\[SUM\]\s+(?P<s>\d+\.\d+)-(?P<e>\d+\.\d+)\s+sec\s+.*?\s+(?P<gbps>\d+(?:\.\d+)?)\s+Gbits/sec\s*$"
    )

    with open(iperf_path, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            match_test = re.search(r"Server listening on 5201 \(test #(\d+)\)", line)
            if match_test:
                current_test = int(match_test.group(1))
                tests[current_test] = []
                continue

            if current_test is None:
                continue

            match_sum = sum_line.match(line.strip())
            if match_sum:
                tests[current_test].append(
                    {
                        "start_s": float(match_sum.group("s")),
                        "end_s": float(match_sum.group("e")),
                        "gbps": float(match_sum.group("gbps")),
                    }
                )

    # Compute trimmed means per test.
    summaries = []
    for test_num in sorted(tests.keys()):
        rows = tests[test_num]
        if not rows:
            continue
        duration_s = max(r["end_s"] for r in rows)
        scored = [
            r
            for r in rows
            if r["start_s"] >= TRIM_START_SECONDS and r["end_s"] <= (duration_s - TRIM_END_SECONDS)
        ]
        use_rows = scored if scored else rows
        gbps_values = [r["gbps"] for r in use_rows]
        summaries.append(
            {
                "test": test_num,
                "duration_s": duration_s,
                "mean_gbps": float(pd.Series(gbps_values).mean()),
                "min_gbps": float(pd.Series(gbps_values).min()),
                "max_gbps": float(pd.Series(gbps_values).max()),
                "samples": len(gbps_values),
            }
        )

    return pd.DataFrame(summaries)

def load_data():
    """Loads markers and power data."""
    try:
        markers = load_markers()
    except FileNotFoundError:
        print(f"Error: Markers file not found at {MARKERS_FILE}")
        return None, None

    try:
        power = load_power()
    except FileNotFoundError:
        print(f"Error: Power file not found at {POWER_FILE}")
        return None, None

    return markers, power

def plot_timeline(power):
    """Plots Power vs Time with colored state regions."""
    plt.figure(figsize=(15, 6))
    
    sns.lineplot(data=power, x="timestamp", y="power_w", linewidth=0.8, alpha=0.8, color='black')
    
    # Color background by state
    # We can use the 'state' column to create colored spans
    # Simple approach: scatter plot on top with hue
    
    # Filter out unlabeled for clearer plot
    plot_data = power[power["state"] != "Unlabeled"]
    
    sns.scatterplot(data=plot_data, x="timestamp", y="power_w", hue="state", s=10, linewidth=0)
    
    plt.title("Power Consumption Timeline")
    plt.ylabel("Power (Watts)")
    plt.xlabel("Time (UTC)")
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, "power_timeline.png")
    plt.savefig(save_path)
    print(f"Saved timeline plot to {save_path}")

def plot_linearity(power):
    """Plots Power vs Load State (Boxplot) to show linearity."""
    
    # Filter for Load states only (and Idle)
    # Exclude unlabeled points (scoring-only view)
    valid_states = ["Idle", "Load-L", "Load-M", "Load-H"]
    df = power[power["state"].isin(valid_states)].copy()
    
    # Order: Idle -> L -> M -> H
    order = ["Idle", "Load-L", "Load-M", "Load-H"]
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="state", y="power_w", order=order, palette="viridis")
    
    # Add mean markers
    sns.pointplot(data=df, x="state", y="power_w", order=order, estimator="mean", color="red", join=False, label="Mean")
    
    plt.title("Power vs State (Trimmed Windows)")
    plt.ylabel("Power (Watts)")
    plt.xlabel("Load Level")
    plt.grid(True, alpha=0.3)
    
    save_path = os.path.join(OUTPUT_DIR, "power_linearity_boxplot.png")
    plt.savefig(save_path)
    print(f"Saved linearity plot to {save_path}")

def generate_stats_table(power):
    """Generates markdown tables of trimmed stats + repeatability."""
    valid_states = ["Idle", "Load-L", "Load-M", "Load-H"]
    df = power[power["state"].isin(valid_states)].copy()

    agg = (
        df.groupby("state")["power_w"]
        .agg(["mean", "std", "min", "max", "count"])
        .reindex(valid_states)
    )
    agg["cv_pct"] = (agg["std"] / agg["mean"]) * 100.0

    per_run = (
        df.groupby(["state", "round"])["power_w"]
        .agg(["mean", "std", "min", "max", "count"])
        .reset_index()
    )
    per_run["cv_pct"] = (per_run["std"] / per_run["mean"]) * 100.0
    per_run = per_run.sort_values(["state", "round"], key=lambda s: s)

    print("\n=== Experiment Statistics (TRIMMED windows) ===")
    print(agg)

    stats_path = os.path.join(OUTPUT_DIR, "stats_summary.md")
    with open(stats_path, "w", encoding="utf-8") as f:
        f.write("# Power Sweep Statistics (Trimmed Windows)\n\n")
        f.write(
            f"Scoring uses explicit Start/Stop markers and excludes transition samples by trimming {TRIM_START_SECONDS}s at the start and {TRIM_END_SECONDS}s at the end of each segment.\n\n"
        )
        f.write("| State | Mean (W) | Std (W) | CV (%) | Min (W) | Max (W) | Count |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for idx, row in agg.iterrows():
            if pd.notna(row["mean"]):
                f.write(
                    f"| {idx} | {row['mean']:.4f} | {row['std']:.4f} | {row['cv_pct']:.2f} | {row['min']:.4f} | {row['max']:.4f} | {int(row['count'])} |\n"
                )

    per_run_path = os.path.join(OUTPUT_DIR, "repeatability_per_run.md")
    with open(per_run_path, "w", encoding="utf-8") as f:
        f.write("# Repeatability (Per Run)\n\n")
        f.write(
            "Mean/Std/CV computed over the trimmed scoring window for each segment. `round=0` means the segment is not tied to a specific run (e.g., initial idle).\n\n"
        )
        f.write("| State | Round | Mean (W) | Std (W) | CV (%) | Min (W) | Max (W) | Count |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for _, row in per_run.iterrows():
            f.write(
                f"| {row['state']} | {int(row['round'])} | {row['mean']:.4f} | {row['std']:.4f} | {row['cv_pct']:.2f} | {row['min']:.4f} | {row['max']:.4f} | {int(row['count'])} |\n"
            )

    print(f"Saved stats to {stats_path}")
    print(f"Saved per-run repeatability to {per_run_path}")


def write_iperf_summary(load_intervals):
    """Writes an iperf summary aligned to the 9 load segments (L/M/H x 3)."""
    if not os.path.exists(IPERF_FILE):
        print(f"Note: No iperf log found at {IPERF_FILE}. Skipping iperf summary.")
        return

    iperf = parse_iperf_tests(IPERF_FILE)
    if iperf.empty:
        print("Note: iperf log parsed but no [SUM] lines found. Skipping iperf summary.")
        return

    load_only = [i for i in load_intervals if i.state in {"Load-L", "Load-M", "Load-H"}]
    load_only = sorted(load_only, key=lambda i: i.start)

    # Map tests 1..9 in order to load segments.
    mapping_rows = []
    for idx, interval in enumerate(load_only, start=1):
        row = iperf[iperf["test"] == idx]
        if row.empty:
            continue
        r = row.iloc[0]
        mapping_rows.append(
            {
                "segment": interval.label,
                "state": interval.state,
                "round": interval.round,
                "iperf_test": int(r["test"]),
                "mean_gbps": float(r["mean_gbps"]),
                "min_gbps": float(r["min_gbps"]),
                "max_gbps": float(r["max_gbps"]),
                "samples": int(r["samples"]),
            }
        )

    summary = pd.DataFrame(mapping_rows)
    out_path = os.path.join(DATA_DIR, "iperf_summary.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# iperf Summary (Server Log)\n\n")
        f.write(
            "This file summarizes `iperf.txt` by extracting per-test `[SUM]` throughput lines from the server output and mapping tests 1..9 to the 9 load segments (L/M/H x 3) in chronological order.\n\n"
        )
        f.write(
            "Important note: the sweep script uses `-P 4`. If `-b` applies per stream in your `iperf3` mode, the aggregate throughput will be ~4× the `-b` target.\n\n"
        )
        f.write("| Segment | State | Round | iperf test | Mean (Gbps) | Min (Gbps) | Max (Gbps) | Samples |\n")
        f.write("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for _, row in summary.iterrows():
            f.write(
                f"| {row['segment']} | {row['state']} | {int(row['round'])} | {int(row['iperf_test'])} | {row['mean_gbps']:.2f} | {row['min_gbps']:.2f} | {row['max_gbps']:.2f} | {int(row['samples'])} |\n"
            )

    print(f"Saved iperf summary to {out_path}")

def main():
    print("Loading data...")
    markers, power = load_data()
    
    if power is None or markers is None:
        return

    print("Building explicit intervals from markers...")
    intervals = build_intervals(markers)

    print("Labelling power samples using trimmed scoring windows...")
    power_labeled = label_power_by_intervals(
        power,
        intervals,
        trim_start_s=TRIM_START_SECONDS,
        trim_end_s=TRIM_END_SECONDS,
    )
    
    print("Generating plots...")
    plot_timeline(power_labeled)
    plot_linearity(power_labeled)
    generate_stats_table(power_labeled)

    print("Summarizing iperf server log...")
    write_iperf_summary(intervals)

    print("Summarizing iperf client logs...")
    write_iperf_client_summaries()
    
    print("Done.")

if __name__ == "__main__":
    main()
