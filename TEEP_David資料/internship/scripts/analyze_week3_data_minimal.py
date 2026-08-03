#!/usr/bin/env python3

import argparse
import csv
import re
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional


TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
MARKER_BRACKET_RE = re.compile(r"^\[(?P<ts>[^\]]+)\]\s+MARKER:\s+(?P<label>.+?)\s*$")


def parse_utc(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class Interval:
    label: str
    state: str
    round: int
    start: datetime
    end: datetime


@dataclass(frozen=True)
class Sample:
    t: datetime
    power_w: float


def _resolve_paths(arg: str) -> tuple[str, Path, Path, Path, Path]:
    run_dir = Path(arg).expanduser().resolve()
    if run_dir.is_file():
        run_dir = run_dir.parent

    run_date = run_dir.name

    markers = run_dir / "markers.md"
    if not markers.exists():
        markers = run_dir / "markers.csv"

    power = run_dir / "power_uw.txt"
    out_dir = Path("assets") / run_date / "plots"

    return run_date, run_dir, markers, power, out_dir


def iter_markers(path: Path) -> Iterable[tuple[datetime, str]]:
    """Yield (timestamp_utc, label) from markers.md or markers.csv."""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    if path.suffix.lower() == ".csv":
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) >= 2 and TS_RE.match(parts[0]):
                yield parse_utc(parts[0]), parts[1]
        return

    for line in lines:
        line = line.strip()
        m = MARKER_BRACKET_RE.match(line)
        if not m:
            continue
        ts = m.group("ts").strip()
        label = m.group("label").strip()
        if TS_RE.match(ts):
            yield parse_utc(ts), label


def _normalize_state_from_label(raw_label: str) -> tuple[str, int]:
    round_num = 0
    m = re.search(r"Run(\d+)", raw_label)
    if m:
        round_num = int(m.group(1))

    state = raw_label
    state = state.replace("Load_L", "Load-L")
    state = state.replace("Load_M", "Load-M")
    state = state.replace("Load_H", "Load-H")

    state = re.sub(r"[_-]?Run\d+", "", state).strip("_-")
    if state == "Initial_Idle":
        state = "Idle"

    return state, round_num


def build_intervals(markers: list[tuple[datetime, str]]) -> list[Interval]:
    starts: dict[str, datetime] = {}
    stops: dict[str, datetime] = {}

    for ts, label in sorted(markers, key=lambda x: x[0]):
        if label.startswith("Start_"):
            starts[label[len("Start_") :]] = ts
        elif label.startswith("Stop_"):
            stops[label[len("Stop_") :]] = ts

    intervals: list[Interval] = []
    for key, start_ts in starts.items():
        end_ts = stops.get(key)
        if not end_ts:
            continue
        state, round_num = _normalize_state_from_label(key)
        intervals.append(Interval(label=key, state=state, round=round_num, start=start_ts, end=end_ts))

    intervals = sorted(intervals, key=lambda i: i.start)

    idle_intervals: list[Interval] = []
    for a, b in zip(intervals, intervals[1:]):
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

    return sorted(intervals + idle_intervals, key=lambda i: i.start)


def iter_power_samples(path: Path) -> Iterable[Sample]:
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [p for p in re.split(r"[\s,]+", line) if p]
        if len(parts) < 2:
            continue
        ts, val = parts[0], parts[1]
        if not TS_RE.match(ts):
            continue
        try:
            uw = float(val)
        except ValueError:
            continue
        yield Sample(t=parse_utc(ts), power_w=uw / 1_000_000.0)


def label_samples(samples: list[Sample], intervals: list[Interval], trim_start_s: int, trim_end_s: int):
    trim_start = timedelta(seconds=trim_start_s)
    trim_end = timedelta(seconds=trim_end_s)

    out = []
    for s in samples:
        state = "Unlabeled"
        round_num = 0
        for itv in intervals:
            scored_start = itv.start + trim_start
            scored_end = itv.end - trim_end
            if scored_end <= scored_start:
                continue
            if scored_start <= s.t < scored_end:
                state = itv.state
                round_num = itv.round
                break
        out.append((s, state, round_num))
    return out


def _safe_stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return float(statistics.stdev(values))


def compute_stats(rows):
    valid_states = ["Idle", "Load-L", "Load-M", "Load-H"]

    by_state = {s: [] for s in valid_states}
    by_state_round: dict[tuple[str, int], list[float]] = {}

    for sample, state, round_num in rows:
        if state not in valid_states:
            continue
        by_state[state].append(sample.power_w)
        by_state_round.setdefault((state, int(round_num)), []).append(sample.power_w)

    agg = {}
    for state in valid_states:
        vals = by_state[state]
        if not vals:
            continue
        mean = float(statistics.mean(vals))
        std = _safe_stdev(vals)
        cv = (std / mean * 100.0) if mean > 0 else 0.0
        agg[state] = {
            "mean": mean,
            "std": std,
            "cv_pct": cv,
            "min": float(min(vals)),
            "max": float(max(vals)),
            "count": int(len(vals)),
        }

    per_run = []
    for (state, round_num), vals in sorted(by_state_round.items(), key=lambda x: (x[0][0], x[0][1])):
        mean = float(statistics.mean(vals))
        std = _safe_stdev(vals)
        cv = (std / mean * 100.0) if mean > 0 else 0.0
        per_run.append(
            {
                "state": state,
                "round": round_num,
                "mean": mean,
                "std": std,
                "cv_pct": cv,
                "min": float(min(vals)),
                "max": float(max(vals)),
                "count": int(len(vals)),
            }
        )

    return agg, per_run


def write_outputs(run_dir: Path, out_dir: Path, rows, agg, per_run, trim_start_s: int, trim_end_s: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    labeled_csv = run_dir / "power_labeled.csv"
    with labeled_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp_utc", "power_w", "state", "round"])
        for sample, state, round_num in rows:
            w.writerow([sample.t.strftime("%Y-%m-%dT%H:%M:%SZ"), f"{sample.power_w:.6f}", state, round_num])

    stats_path = out_dir / "stats_summary.md"
    with stats_path.open("w", encoding="utf-8") as f:
        f.write("# Power Sweep Statistics (Trimmed Windows)\n\n")
        f.write(
            f"Scoring uses explicit Start/Stop markers and excludes transition samples by trimming {trim_start_s}s at the start and {trim_end_s}s at the end of each segment.\n\n"
        )
        f.write("| State | Mean (W) | Std (W) | CV (%) | Min (W) | Max (W) | Count |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for state in ["Idle", "Load-L", "Load-M", "Load-H"]:
            row = agg.get(state)
            if not row:
                continue
            f.write(
                f"| {state} | {row['mean']:.4f} | {row['std']:.4f} | {row['cv_pct']:.2f} | {row['min']:.4f} | {row['max']:.4f} | {row['count']} |\n"
            )

    per_run_path = out_dir / "repeatability_per_run.md"
    with per_run_path.open("w", encoding="utf-8") as f:
        f.write("# Repeatability (Per Run)\n\n")
        f.write(
            "Mean/Std/CV computed over the trimmed scoring window for each segment. `round=0` means the segment is not tied to a specific run (e.g., initial idle).\n\n"
        )
        f.write("| State | Round | Mean (W) | Std (W) | CV (%) | Min (W) | Max (W) | Count |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for row in per_run:
            f.write(
                f"| {row['state']} | {row['round']} | {row['mean']:.4f} | {row['std']:.4f} | {row['cv_pct']:.2f} | {row['min']:.4f} | {row['max']:.4f} | {row['count']} |\n"
            )

    print(f"Wrote labeled samples: {labeled_csv}")
    print(f"Wrote stats summary: {stats_path}")
    print(f"Wrote repeatability: {per_run_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Minimal Week3 sweep analyzer (no pandas/matplotlib dependencies)")
    ap.add_argument("run_dir", help="Run folder (e.g., runs/2026-01-23 or runs/2026-01-28/sweep-01)")
    ap.add_argument("--trim-start", type=int, default=10)
    ap.add_argument("--trim-end", type=int, default=10)
    args = ap.parse_args()

    _, run_dir, markers_path, power_path, out_dir = _resolve_paths(args.run_dir)

    if not markers_path.exists():
        raise SystemExit(f"Markers not found: {markers_path}")
    if not power_path.exists():
        raise SystemExit(f"Power log not found: {power_path}")

    markers = list(iter_markers(markers_path))
    if not markers:
        raise SystemExit(f"No markers parsed from {markers_path}")

    intervals = build_intervals(markers)
    if not intervals:
        raise SystemExit("No Start_/Stop_ interval pairs found in markers")

    samples = list(iter_power_samples(power_path))
    if not samples:
        raise SystemExit(f"No power samples parsed from {power_path}")

    rows = label_samples(samples, intervals, trim_start_s=args.trim_start, trim_end_s=args.trim_end)
    agg, per_run = compute_stats(rows)

    write_outputs(run_dir, out_dir, rows, agg, per_run, args.trim_start, args.trim_end)


if __name__ == "__main__":
    main()
