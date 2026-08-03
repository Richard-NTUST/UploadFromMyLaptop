#!/usr/bin/env python3
"""Merge WINLAB rApp throughput artifacts with Outlet 2 PDU power data."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


@dataclass(frozen=True)
class PowerSample:
    t: datetime
    watts: float


@dataclass(frozen=True)
class StepWindow:
    offered_load_mbps: float
    rx_throughput_mbps: float
    start: datetime
    end: datetime


def parse_time(raw: str) -> datetime:
    raw = raw.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    if "." in raw:
        head, tail = raw.split(".", 1)
        offset = ""
        for marker in ("+", "-"):
            marker_index = tail.find(marker)
            if marker_index > 0:
                offset = tail[marker_index:]
                tail = tail[:marker_index]
                break
        raw = f"{head}.{tail[:6]}{offset}"
    ts = datetime.fromisoformat(raw)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def parse_iperf_time(raw: str) -> datetime:
    ts = parsedate_to_datetime(raw)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def parse_float(raw: object) -> float | None:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        return list(csv.DictReader(line for line in f if line.strip() and not line.startswith("#")))


def read_power_samples(path: Path) -> list[PowerSample]:
    rows = []
    for row in read_csv_rows(path):
        raw_time = row.get("_time") or row.get("time") or row.get("timestamp_utc") or row.get("timestamp")
        raw_value = row.get("_value") or row.get("active_power") or row.get("power_w") or row.get("value")
        value = parse_float(raw_value)
        if not raw_time or value is None:
            continue
        try:
            rows.append(PowerSample(t=parse_time(raw_time), watts=value))
        except ValueError:
            continue
    return sorted(rows, key=lambda sample: sample.t)


def read_offered_rows(path: Path) -> list[dict[str, float]]:
    rows = []
    for row in read_csv_rows(path):
        offered = parse_float(row.get("offered_load_mbps"))
        rx = parse_float(row.get("rx_throughput_mbps"))
        if offered is None or rx is None:
            continue
        rows.append({"offered_load_mbps": offered, "rx_throughput_mbps": rx})
    return rows


def read_concatenated_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    decoder = json.JSONDecoder()
    pos = 0
    objects = []
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            break
        try:
            obj, index = decoder.raw_decode(text, pos)
        except json.JSONDecodeError:
            next_obj = text.find("{", pos + 1)
            if next_obj == -1:
                break
            pos = next_obj
            continue
        if isinstance(obj, dict):
            objects.append(obj)
        pos = index
    return objects


def iperf_object_window(obj: dict) -> tuple[datetime, datetime] | None:
    timestamp = obj.get("start", {}).get("timestamp", {})
    start_raw = timestamp.get("time")
    if not start_raw:
        return None
    try:
        start = parse_iperf_time(start_raw)
    except (TypeError, ValueError):
        return None

    interval_ends = []
    all_interval_ends = []
    for interval in obj.get("intervals", []):
        summary = interval.get("sum", {})
        end_s = parse_float(summary.get("end"))
        if end_s is not None:
            all_interval_ends.append(end_s)
            bits_per_second = parse_float(summary.get("bits_per_second"))
            if bits_per_second is not None and bits_per_second > 0:
                interval_ends.append(end_s)

    # An interrupted UE client may remain alive with zero-throughput intervals
    # until its idle timeout. Power must be aligned to carried traffic, not that
    # inactive tail.
    duration = max(interval_ends) if interval_ends else None
    if duration is None and all_interval_ends:
        duration = max(all_interval_ends)
    if duration is None:
        duration = parse_float(obj.get("start", {}).get("test_start", {}).get("duration"))
    if duration is None:
        duration = 0.0
    return start, start + timedelta(seconds=duration)


def build_step_windows(
    artifact_dir: Path,
    summary: dict,
    offered_rows: list[dict[str, float]],
    request: dict,
) -> list[StepWindow]:
    ue_json = artifact_dir / "iperf-UE-RX.log"
    json_windows = [
        window
        for window in (iperf_object_window(obj) for obj in read_concatenated_json(ue_json))
        if window is not None
    ]

    if len(json_windows) >= len(offered_rows):
        return [
            StepWindow(
                offered_load_mbps=row["offered_load_mbps"],
                rx_throughput_mbps=row["rx_throughput_mbps"],
                start=json_windows[index][0],
                end=json_windows[index][1],
            )
            for index, row in enumerate(offered_rows)
        ]

    if len(offered_rows) == 1:
        return [
            StepWindow(
                offered_load_mbps=offered_rows[0]["offered_load_mbps"],
                rx_throughput_mbps=offered_rows[0]["rx_throughput_mbps"],
                start=parse_time(summary["started_utc"]),
                end=parse_time(summary["finished_utc"]),
            )
        ]

    start = parse_time(summary["started_utc"])
    period = int(request.get("period") or 0)
    gap_time = int(request.get("gap_time") or request.get("gap-time") or 0)
    windows = []
    cursor = start
    for row in offered_rows:
        end = cursor + timedelta(seconds=period)
        windows.append(
            StepWindow(
                offered_load_mbps=row["offered_load_mbps"],
                rx_throughput_mbps=row["rx_throughput_mbps"],
                start=cursor,
                end=end,
            )
        )
        cursor = end + timedelta(seconds=gap_time)
    return windows


def summarize_power(samples: list[PowerSample], start: datetime, end: datetime) -> dict[str, object]:
    selected = [sample.watts for sample in samples if start <= sample.t <= end]
    if not selected:
        return {
            "avg_power_w": "",
            "min_power_w": "",
            "max_power_w": "",
            "sample_count": 0,
        }
    return {
        "avg_power_w": statistics.mean(selected),
        "min_power_w": min(selected),
        "max_power_w": max(selected),
        "sample_count": len(selected),
    }


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "run_id",
        "mode",
        "target_identity",
        "offered_load_mbps",
        "rx_throughput_mbps",
        "start_utc",
        "end_utc",
        "avg_power_w",
        "min_power_w",
        "max_power_w",
        "sample_count",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def merge(artifact_dir: Path, pdu_csv: Path) -> list[dict[str, object]]:
    summary = read_json(artifact_dir / "summary.json")
    request_path = artifact_dir / "request.json"
    request = read_json(request_path) if request_path.exists() else {}
    offered_rows = read_offered_rows(artifact_dir / "offered_load_throughput.csv")
    if not offered_rows:
        raise SystemExit(f"No offered-load rows found in {artifact_dir / 'offered_load_throughput.csv'}")

    power_samples = read_power_samples(pdu_csv)
    if not power_samples:
        raise SystemExit(f"No power samples found in {pdu_csv}")

    run_id = Path(summary.get("artifact_dir") or artifact_dir).name
    windows = build_step_windows(artifact_dir, summary, offered_rows, request)
    rows = []
    for window in windows:
        row = {
            "run_id": run_id,
            "mode": summary.get("mode", ""),
            "target_identity": summary.get("target_identity", ""),
            "offered_load_mbps": window.offered_load_mbps,
            "rx_throughput_mbps": window.rx_throughput_mbps,
            "start_utc": iso_z(window.start),
            "end_utc": iso_z(window.end),
        }
        row.update(summarize_power(power_samples, window.start, window.end))
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_dir", type=Path, help="rApp E2E artifact directory")
    parser.add_argument("pdu_csv", type=Path, help="InfluxDB Outlet 2 active_power CSV")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output merged CSV path. Default: <artifact_dir>/power_throughput_summary.csv",
    )
    args = parser.parse_args()

    artifact_dir = args.artifact_dir
    output = args.output or artifact_dir / "power_throughput_summary.csv"
    rows = merge(artifact_dir, args.pdu_csv)
    write_csv(output, rows)
    print(f"Wrote {output}")
    for row in rows:
        avg_power = row["avg_power_w"]
        avg_power_text = f"{avg_power:.3f}" if isinstance(avg_power, float) else "n/a"
        print(
            f"{row['offered_load_mbps']} Mbps -> {row['rx_throughput_mbps']:.3f} Mbps, "
            f"power={avg_power_text} W, n={row['sample_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
