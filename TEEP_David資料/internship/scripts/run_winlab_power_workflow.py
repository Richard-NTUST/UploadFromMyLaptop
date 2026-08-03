#!/usr/bin/env python3
"""
Run the WINLAB evidence workflow in a safe, ordered way.

Default behavior is dry-run. Pass --live to start an actual rApp /gnb/run job.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def run_step(name: str, cmd: list[str], allow_failure: bool = False) -> dict:
    print(f"\n[{name}] {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.stdout:
        print(proc.stdout.rstrip(), flush=True)
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr, flush=True)
    result = {
        "name": name,
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.returncode != 0 and not allow_failure:
        raise SystemExit(f"{name} failed with return code {proc.returncode}")
    return result


def first_output_line(result: dict) -> str:
    for line in str(result.get("stdout", "")).splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def parse_bandwidth(raw: str) -> str:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one bandwidth value is required")
    for value in values:
        int(value)
    return ",".join(values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["ocloud", "baremetal"], default="ocloud")
    parser.add_argument("--live", action="store_true", help="Start a real rApp job. Default is dry-run.")
    parser.add_argument("--bandwidth", type=parse_bandwidth, default="100")
    parser.add_argument("--period", type=int, default=300)
    parser.add_argument("--gap-time", type=int, default=2)
    parser.add_argument("--ue-model", choices=["samsung", "mtk"], default="samsung")
    parser.add_argument("--settle-time", type=int, default=45)
    parser.add_argument("--attach-timeout", type=int, default=240)
    parser.add_argument("--outlets", default="outlet2")
    parser.add_argument("--output-root", default="runs")
    parser.add_argument("--poll-interval", type=int, default=5)
    parser.add_argument("--ping", action="store_true", help="Ask the underlying experiment to include ping collection.")
    parser.add_argument("--skip-snapshot", action="store_true")
    parser.add_argument("--skip-report", action="store_true")
    args = parser.parse_args()

    root = Path(args.output_root)
    stamp = utc_stamp()
    workflow_dir = root / f"workflow-{args.mode}-{'live' if args.live else 'dry'}-{stamp}"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    scripts = script_dir()

    steps: list[dict] = []
    snapshot_dir = workflow_dir / "status_snapshot"
    probe_dir = workflow_dir / "probe"

    if not args.skip_snapshot:
        steps.append(
            run_step(
                "snapshot",
                [
                    sys.executable,
                    str(scripts / "collect_winlab_status_snapshot.py"),
                    "--output-dir",
                    str(snapshot_dir),
                ],
            )
        )

    probe_cmd = [
        sys.executable,
        str(scripts / "run_winlab_ocloud_power_probe.py"),
        "--mode",
        args.mode,
        "--bandwidth",
        args.bandwidth,
        "--period",
        str(args.period),
        "--gap-time",
        str(args.gap_time),
        "--ue-model",
        args.ue_model,
        "--output-dir",
        str(probe_dir),
        "--poll-interval",
        str(args.poll_interval),
    ]
    if args.mode == "ocloud":
        probe_cmd.extend(
            [
                "--settle-time",
                str(args.settle_time),
                "--attach-timeout",
                str(args.attach_timeout),
                "--outlets",
                args.outlets,
            ]
        )
    if not args.live:
        probe_cmd.append("--dry-run")
    if args.ping:
        probe_cmd.append("--ping")
    steps.append(run_step("probe", probe_cmd, allow_failure=args.live))

    if (probe_dir / "influx").exists():
        steps.append(
            run_step(
                "outlet_summary",
                [sys.executable, str(scripts / "summarize_winlab_outlet_power.py"), str(probe_dir)],
                allow_failure=True,
            )
        )

    if not args.skip_report:
        if snapshot_dir.exists():
            steps.append(
                run_step(
                    "snapshot_report",
                    [sys.executable, str(scripts / "build_winlab_evidence_report.py"), str(snapshot_dir)],
                    allow_failure=True,
                )
            )
        if probe_dir.exists():
            steps.append(
                run_step(
                    "probe_report",
                    [sys.executable, str(scripts / "build_winlab_evidence_report.py"), str(probe_dir)],
                    allow_failure=True,
                )
            )

    summary = {
        "workflow_dir": str(workflow_dir),
        "mode": args.mode,
        "live": args.live,
        "snapshot_dir": str(snapshot_dir) if snapshot_dir.exists() else "",
        "probe_dir": str(probe_dir) if probe_dir.exists() else "",
        "steps": [
            {
                "name": step["name"],
                "command": step["command"],
                "returncode": step["returncode"],
                "first_output_line": first_output_line(step),
            }
            for step in steps
        ],
    }
    (workflow_dir / "workflow_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"\nWorkflow directory: {workflow_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
