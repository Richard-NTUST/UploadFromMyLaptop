#!/usr/bin/env python3
"""
Summarize candidate WINLAB PDU outlet power CSVs exported by
run_winlab_ocloud_power_probe.py.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Sample:
    t: datetime
    power_w: float


def parse_time(raw: str) -> datetime:
    raw = raw.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    ts = datetime.fromisoformat(raw)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def parse_float(raw: str) -> float | None:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def find_column(fieldnames: list[str], candidates: Iterable[str]) -> str | None:
    lowered = {name.lower(): name for name in fieldnames}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def iter_influx_csv(path: Path) -> Iterable[Sample]:
    """Parse normal Influx annotated CSV and simple timestamp/value CSV."""
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        lines = [line for line in f if line.strip() and not line.startswith("#")]
    if not lines:
        return

    reader = csv.DictReader(lines)
    if not reader.fieldnames:
        return

    time_col = find_column(reader.fieldnames, ["_time", "time", "timestamp_utc", "timestamp"])
    value_col = find_column(reader.fieldnames, ["_value", "value", "active_power", "power_w", "power"])
    if not time_col or not value_col:
        raise ValueError(f"{path} missing time/value columns; found {reader.fieldnames}")

    for row in reader:
        raw_time = row.get(time_col, "")
        raw_value = row.get(value_col, "")
        if not raw_time or raw_value is None:
            continue
        value = parse_float(raw_value)
        if value is None:
            continue
        try:
            yield Sample(t=parse_time(raw_time), power_w=value)
        except ValueError:
            continue


def integrate_energy_j(samples: list[Sample]) -> float:
    if len(samples) < 2:
        return 0.0
    total = 0.0
    ordered = sorted(samples, key=lambda s: s.t)
    for a, b in zip(ordered, ordered[1:]):
        dt = (b.t - a.t).total_seconds()
        if dt <= 0:
            continue
        total += 0.5 * (a.power_w + b.power_w) * dt
    return total


def read_markers(path: Path) -> dict:
    if not path.exists():
        return {}
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8", errors="ignore")))
    markers = {}
    for row in rows:
        label = row.get("label", "")
        ts = row.get("timestamp_utc", "")
        if label and ts:
            try:
                markers[label] = parse_time(ts)
            except ValueError:
                pass
    return markers


def summarize(path: Path, start: datetime | None, stop: datetime | None) -> dict:
    samples = sorted(iter_influx_csv(path), key=lambda s: s.t)
    if start:
        samples = [s for s in samples if s.t >= start]
    if stop:
        samples = [s for s in samples if s.t <= stop]

    values = [s.power_w for s in samples]
    if not values:
        return {
            "source_file": str(path),
            "outlet": path.stem,
            "n": 0,
            "start_utc": "",
            "end_utc": "",
            "mean_w": "",
            "min_w": "",
            "max_w": "",
            "std_w": "",
            "energy_j": "",
            "duration_s": "",
        }

    duration_s = (samples[-1].t - samples[0].t).total_seconds() if len(samples) > 1 else 0.0
    return {
        "source_file": str(path),
        "outlet": path.stem,
        "n": len(samples),
        "start_utc": samples[0].t.isoformat().replace("+00:00", "Z"),
        "end_utc": samples[-1].t.isoformat().replace("+00:00", "Z"),
        "mean_w": statistics.mean(values),
        "min_w": min(values),
        "max_w": max(values),
        "std_w": statistics.pstdev(values) if len(values) > 1 else 0.0,
        "energy_j": integrate_energy_j(samples),
        "duration_s": duration_s,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "outlet",
        "n",
        "start_utc",
        "end_utc",
        "duration_s",
        "mean_w",
        "min_w",
        "max_w",
        "std_w",
        "energy_j",
        "source_file",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", help="Probe run directory")
    parser.add_argument("--start", help="UTC ISO timestamp override")
    parser.add_argument("--stop", help="UTC ISO timestamp override")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    influx_dir = run_dir / "influx"
    if not influx_dir.exists():
        raise SystemExit(f"Missing {influx_dir}; run the probe with Influx env vars first.")

    markers = read_markers(run_dir / "markers.csv")
    start = parse_time(args.start) if args.start else markers.get("preflight_start")
    stop = parse_time(args.stop) if args.stop else markers.get("rapp_finished")

    rows = []
    for path in sorted(influx_dir.glob("*.csv")):
        rows.append(summarize(path, start, stop))

    if not rows:
        raise SystemExit(f"No CSV files found in {influx_dir}")

    out_csv = run_dir / "candidate_outlet_power_summary.csv"
    out_json = run_dir / "candidate_outlet_power_summary.json"
    write_csv(out_csv, rows)
    out_json.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_json}")
    for row in rows:
        mean_w = row["mean_w"]
        mean_text = f"{mean_w:.3f} W" if isinstance(mean_w, float) else "n/a"
        print(f"{row['outlet']}: n={row['n']} mean={mean_text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
