#!/usr/bin/env python3
"""
Run a marked WINLAB rApp OCloud test and optionally export candidate PDU outlet
power data from InfluxDB.

This is intentionally credential-neutral. Set the Influx environment variables
only on the lab machine or shell that has access.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TAIPEI_TZ = timezone(timedelta(hours=8))
TERMINAL_STATES = {"succeeded", "failed", "cancelled"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def taipei_iso(ts: datetime) -> str:
    return ts.astimezone(TAIPEI_TZ).isoformat(timespec="seconds")


def request_json(method: str, url: str, payload: dict | None = None, timeout: int = 10) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as res:
            text = res.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc}") from exc
    return json.loads(text)


def append_marker(path: Path, label: str, ts: datetime, notes: str = "") -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["label", "timestamp_utc", "timestamp_taipei", "notes"])
        writer.writerow([label, iso_z(ts), taipei_iso(ts), notes])


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_bandwidths(raw: str) -> list[int]:
    values = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            values.append(int(item))
    if not values:
        raise argparse.ArgumentTypeError("at least one bandwidth value is required")
    return values


def influx_configured() -> bool:
    required = ["INFLUX_URL", "INFLUX_TOKEN", "INFLUX_ORG", "INFLUX_BUCKET"]
    return all(os.environ.get(k) for k in required)


def influx_query_csv(flux: str) -> str:
    url = os.environ["INFLUX_URL"].rstrip("/") + "/api/v2/query"
    org = os.environ["INFLUX_ORG"]
    token = os.environ["INFLUX_TOKEN"]
    body = json.dumps({"query": flux, "type": "flux"}).encode("utf-8")
    req = Request(
        f"{url}?org={org}",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
            "Accept": "application/csv",
        },
    )
    with urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def escape_flux_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_flux(start: str, stop: str, outlet: str) -> str:
    bucket = escape_flux_string(os.environ["INFLUX_BUCKET"])
    field = escape_flux_string(os.environ.get("INFLUX_FIELD", "active_power"))
    outlet_column = os.environ.get("INFLUX_OUTLET_COLUMN", "outlet")
    measurement = os.environ.get("INFLUX_MEASUREMENT", "").strip()

    filters = [f'r._field == "{field}"']
    if measurement:
        filters.append(f'r._measurement == "{escape_flux_string(measurement)}"')
    if outlet_column == "_measurement":
        filters.append(f'r._measurement == "{escape_flux_string(outlet)}"')
    else:
        filters.append(f'r["{escape_flux_string(outlet_column)}"] == "{escape_flux_string(outlet)}"')

    filter_expr = " and ".join(filters)
    return (
        f'from(bucket: "{bucket}")\n'
        f"  |> range(start: time(v: \"{start}\"), stop: time(v: \"{stop}\"))\n"
        f"  |> filter(fn: (r) => {filter_expr})\n"
        f"  |> keep(columns: [\"_time\", \"_value\", \"_field\", \"_measurement\", \"{escape_flux_string(outlet_column)}\"])\n"
    )


def export_influx(out_dir: Path, start: str, stop: str, outlets: list[str]) -> dict:
    result = {
        "configured": influx_configured(),
        "outlets": outlets,
        "files": [],
        "notes": [],
    }
    if not influx_configured():
        result["notes"].append(
            "Skipped Influx export; set INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, and INFLUX_BUCKET."
        )
        return result

    influx_dir = out_dir / "influx"
    influx_dir.mkdir(parents=True, exist_ok=True)
    for outlet in outlets:
        flux = build_flux(start, stop, outlet)
        flux_path = influx_dir / f"{outlet}.flux"
        csv_path = influx_dir / f"{outlet}.csv"
        flux_path.write_text(flux, encoding="utf-8")
        try:
            csv_text = influx_query_csv(flux)
        except Exception as exc:  # Keep other outlets moving.
            err_path = influx_dir / f"{outlet}.error.txt"
            err_path.write_text(str(exc) + "\n", encoding="utf-8")
            result["files"].append(str(err_path))
            result["notes"].append(f"{outlet}: query failed; see {err_path.name}")
            continue
        csv_path.write_text(csv_text, encoding="utf-8")
        result["files"].append(str(csv_path))
        result["files"].append(str(flux_path))
        non_comment_lines = [line for line in csv_text.splitlines() if line and not line.startswith("#")]
        result["notes"].append(f"{outlet}: wrote {max(0, len(non_comment_lines) - 1)} data rows")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp-url", default=os.environ.get("RAPP_URL", "http://127.0.0.1:9090"))
    parser.add_argument("--mode", choices=["ocloud", "baremetal"], default="ocloud")
    parser.add_argument("--bandwidth", type=parse_bandwidths, default=[100], help="Comma-separated Mbps values")
    parser.add_argument("--period", type=int, default=300)
    parser.add_argument("--gap-time", type=int, default=2)
    parser.add_argument("--ue-model", default="samsung")
    parser.add_argument("--settle-time", type=int, default=45)
    parser.add_argument("--attach-timeout", type=int, default=240)
    parser.add_argument("--uplink", action="store_true")
    parser.add_argument("--ping", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-ue-online-on-failure", action="store_true", default=True)
    parser.add_argument("--outlets", default="outlet2")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--poll-interval", type=int, default=5)
    args = parser.parse_args()

    run_start = utc_now()
    out_dir = Path(args.output_dir) if args.output_dir else Path("runs") / run_start.strftime("%Y-%m-%d") / (
        "winlab-ocloud-power-probe-" + run_start.strftime("%H%M%S")
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    markers_path = out_dir / "markers.csv"
    append_marker(markers_path, "preflight_start", run_start, "script started")

    payload = {
        "mode": args.mode,
        "bandwidth": args.bandwidth,
        "period": args.period,
        "gap_time": args.gap_time,
        "ue_model": args.ue_model,
        "settle_time": args.settle_time,
        "attach_timeout": args.attach_timeout,
        "keep_ue_online_on_failure": args.keep_ue_online_on_failure,
        "uplink": args.uplink,
        "ping": args.ping,
        "dry_run": args.dry_run,
    }
    write_json(out_dir / "request_payload.json", payload)

    submit_ts = utc_now()
    append_marker(markers_path, "rapp_submit", submit_ts, f"POST /gnb/run mode={args.mode}")
    submission = request_json("POST", args.rapp_url.rstrip("/") + "/gnb/run", payload)
    write_json(out_dir / "submission.json", submission)

    job_id = submission.get("job_id")
    if not job_id or job_id == "dry-run":
        append_marker(markers_path, "dry_run_done", utc_now(), "no live job started")
        write_json(out_dir / "summary.json", {"submission": submission, "output_dir": str(out_dir)})
        print(str(out_dir))
        return 0

    last_job = {}
    while True:
        last_job = request_json("GET", args.rapp_url.rstrip("/") + f"/jobs/{job_id}")
        write_json(out_dir / "job_latest.json", last_job)
        status = str(last_job.get("status", "unknown"))
        print(f"{iso_z(utc_now())} job={job_id} status={status}", flush=True)
        if status in TERMINAL_STATES:
            break
        time.sleep(max(1, args.poll_interval))

    finish_ts = utc_now()
    append_marker(markers_path, "rapp_finished", finish_ts, f"job={job_id} status={last_job.get('status')}")

    outlets = [item.strip() for item in args.outlets.split(",") if item.strip()]
    influx = export_influx(out_dir, iso_z(run_start), iso_z(finish_ts), outlets)
    write_json(out_dir / "influx_export_summary.json", influx)

    summary = {
        "output_dir": str(out_dir),
        "job_id": job_id,
        "status": last_job.get("status"),
        "returncode": last_job.get("returncode"),
        "start_utc": iso_z(run_start),
        "finish_utc": iso_z(finish_ts),
        "markers_csv": str(markers_path),
        "influx": influx,
    }
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if last_job.get("status") == "succeeded" else 1


if __name__ == "__main__":
    sys.exit(main())
