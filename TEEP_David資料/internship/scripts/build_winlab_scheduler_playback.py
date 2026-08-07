#!/usr/bin/env python3
"""Build an offline scheduler-playback dataset from WINLAB E2E artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean


SCHEDULER_RE = re.compile(
    r"^(?P<clock>\d+\.\d+).*?\[WINLAB_SCHED_LOG\] "
    r"mode=(?P<mode>\S+) frame=(?P<frame>\d+) slot=(?P<slot>\d+) "
    r"rnti=(?P<rnti>[0-9a-fA-F]+) is_retx=(?P<is_retx>[01]) "
    r"rbStart=(?P<rb_start>\d+) rbSize=(?P<rb_size>\d+) "
    r"mcs=(?P<mcs>\d+) tbs=(?P<tbs>\d+) layers=(?P<layers>\d+) "
    r"harq_pid=(?P<harq_pid>\d+) beam=(?P<beam>\d+) "
    r"tda=(?P<tda>\d+) sym=(?P<sym_start>\d+):(?P<sym_count>\d+)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("pdu_csv", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--total-prbs", type=int, default=273)
    parser.add_argument(
        "--representative-grants",
        type=int,
        default=16,
        help="Maximum grants retained per one-second playback bucket.",
    )
    return parser.parse_args()


def parse_timestamp(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    match = re.match(r"^(.*?\.)(\d+)([+-]\d\d:\d\d)$", value)
    if match:
        value = match.group(1) + match.group(2)[:6].ljust(6, "0") + match.group(3)
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_throughput(path: Path) -> list[dict]:
    samples: list[dict] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            mbps = float(row["mbps"])
            if mbps <= 0:
                continue
            samples.append(
                {
                    "t": round(float(row["end_s"]), 3),
                    "mbps": round(mbps, 3),
                }
            )
    return samples


def load_power(path: Path, run_start: datetime) -> list[dict]:
    samples: list[dict] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if not row or not row.get("_time") or not row.get("_value"):
                continue
            timestamp = parse_timestamp(row["_time"])
            samples.append(
                {
                    "t": round((timestamp - run_start).total_seconds(), 3),
                    "watts": round(float(row["_value"]), 3),
                }
            )
    return samples


def representative_events(events: list[dict], limit: int) -> list[dict]:
    if len(events) <= limit:
        return events
    step = (len(events) - 1) / (limit - 1)
    return [events[round(index * step)] for index in range(limit)]


def load_scheduler(path: Path, representative_limit: int) -> tuple[list[dict], dict]:
    raw_events: list[dict] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = SCHEDULER_RE.search(line)
            if not match:
                continue
            values = match.groupdict()
            raw_events.append(
                {
                    "clock": float(values["clock"]),
                    "mode": values["mode"],
                    "frame": int(values["frame"]),
                    "slot": int(values["slot"]),
                    "rnti": values["rnti"].lower(),
                    "retx": int(values["is_retx"]),
                    "rbStart": int(values["rb_start"]),
                    "rbSize": int(values["rb_size"]),
                    "mcs": int(values["mcs"]),
                    "tbs": int(values["tbs"]),
                    "layers": int(values["layers"]),
                    "harq": int(values["harq_pid"]),
                    "tda": int(values["tda"]),
                    "symStart": int(values["sym_start"]),
                    "symCount": int(values["sym_count"]),
                }
            )

    if not raw_events:
        raise ValueError(f"No WINLAB scheduler records found in {path}")

    first_clock = raw_events[0]["clock"]
    raw_buckets: dict[int, list[dict]] = defaultdict(list)
    for event in raw_events:
        event["t"] = round(event.pop("clock") - first_clock, 6)
        raw_buckets[int(math.floor(event["t"]))].append(event)

    peak_grants_per_second = max(len(events) for events in raw_buckets.values())
    dense_threshold = max(100, int(peak_grants_per_second * 0.1))
    dense_seconds: list[int] = []
    for second in range(max(raw_buckets) + 1):
        if len(raw_buckets.get(second, [])) >= dense_threshold:
            dense_seconds.append(second)
        elif dense_seconds:
            break

    if dense_seconds:
        dense_stop = dense_seconds[-1] + 1
        dense_events = [event for event in raw_events if event["t"] < dense_stop]
    else:
        dense_events = raw_events

    buckets: dict[int, list[dict]] = defaultdict(list)
    for event in dense_events:
        buckets[int(math.floor(event["t"]))].append(event)

    series: list[dict] = []
    for second in range(max(buckets) + 1):
        events = buckets.get(second, [])
        if not events:
            series.append(
                {
                    "t": second,
                    "grantCount": 0,
                    "meanPrbs": 0,
                    "maxPrbs": 0,
                    "meanMcs": 0,
                    "meanTbs": 0,
                    "retxRate": 0,
                    "events": [],
                }
            )
            continue
        series.append(
            {
                "t": second,
                "grantCount": len(events),
                "meanPrbs": round(fmean(event["rbSize"] for event in events), 2),
                "maxPrbs": max(event["rbSize"] for event in events),
                "meanMcs": round(fmean(event["mcs"] for event in events), 2),
                "meanTbs": round(fmean(event["tbs"] for event in events), 2),
                "retxRate": round(
                    100 * sum(event["retx"] for event in events) / len(events), 2
                ),
                "events": representative_events(events, representative_limit),
            }
        )

    modes = Counter(event["mode"] for event in dense_events)
    rntis = Counter(event["rnti"] for event in dense_events)
    rb_size_counts = Counter(event["rbSize"] for event in dense_events)
    dominant_rb_size, dominant_rb_count = rb_size_counts.most_common(1)[0]
    metadata = {
        "eventCount": len(dense_events),
        "coverageSeconds": round(dense_events[-1]["t"], 3),
        "rawEventCount": len(raw_events),
        "rawCoverageSeconds": round(raw_events[-1]["t"], 3),
        "excludedSparseEventCount": len(raw_events) - len(dense_events),
        "denseThreshold": dense_threshold,
        "modes": dict(modes),
        "rntis": dict(rntis),
        "rbSizeCounts": dict(sorted(rb_size_counts.items())),
        "dominantGrantPrbs": dominant_rb_size,
        "dominantGrantPercent": round(100 * dominant_rb_count / len(dense_events), 1),
        "newTxCount": sum(1 for event in dense_events if not event["retx"]),
        "retxCount": sum(event["retx"] for event in dense_events),
        "maxNewTxPrbs": max(
            event["rbSize"] for event in dense_events if not event["retx"]
        ),
        "maxRetxPrbs": max(
            (event["rbSize"] for event in dense_events if event["retx"]),
            default=0,
        ),
    }
    return series, metadata


def mean_power_during_traffic(power: list[dict], duration: float) -> float:
    active = [sample["watts"] for sample in power if 0 <= sample["t"] <= duration]
    return round(fmean(active), 3) if active else 0


def main() -> None:
    args = parse_args()
    artifact_dir = args.artifact_dir.resolve()
    summary = load_json(artifact_dir / "summary.json")
    request = load_json(artifact_dir / "request.json")
    iperf = load_json(artifact_dir / "iperf-UE-RX.log")

    run_start = datetime.fromtimestamp(
        iperf["start"]["timestamp"]["timesecs"], tz=timezone.utc
    )
    throughput = load_throughput(artifact_dir / "iperf_timeseries.csv")
    power = load_power(args.pdu_csv.resolve(), run_start)
    scheduler, scheduler_meta = load_scheduler(
        artifact_dir / "ocloud_pod_logs" / "vnf_pod.log",
        args.representative_grants,
    )

    traffic_duration = throughput[-1]["t"]
    requested_duration = float(request["period"])
    payload = {
        "meta": {
            "title": "Single-UE Scheduler Playback",
            "runId": artifact_dir.name,
            "jobMode": summary["mode"],
            "schedulerMode": next(iter(scheduler_meta["modes"])),
            "target": summary["target_identity"],
            "ueSerial": summary["ue_serial"],
            "rnti": next(iter(scheduler_meta["rntis"])),
            "runStartUtc": run_start.isoformat().replace("+00:00", "Z"),
            "offeredLoadMbps": float(request["bandwidth"][0]),
            "requestedDurationSeconds": requested_duration,
            "trafficDurationSeconds": round(traffic_duration, 3),
            "completionPercent": round(100 * traffic_duration / requested_duration, 1),
            "meanThroughputMbps": round(
                fmean(sample["mbps"] for sample in throughput), 3
            ),
            "meanPowerWatts": mean_power_during_traffic(power, traffic_duration),
            "iperfError": iperf.get("error", ""),
            "totalPrbs": args.total_prbs,
            **scheduler_meta,
        },
        "throughput": throughput,
        "power": power,
        "scheduler": scheduler,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    args.output.write_text(
        "window.WINLAB_RUN_DATA=" + encoded + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output} ({len(encoded):,} JSON bytes)")
    print(
        f"Scheduler: {scheduler_meta['eventCount']:,} grants over "
        f"{scheduler_meta['coverageSeconds']:.1f}s; traffic: {traffic_duration:.1f}s"
    )


if __name__ == "__main__":
    main()
