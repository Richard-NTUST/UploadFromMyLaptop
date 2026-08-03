#!/usr/bin/env python3
"""
Collect a non-invasive WINLAB HPE/OCloud status snapshot.

This script does not start traffic, toggle UE state, install Helm charts, or
modify Kubernetes resources. It only records command output for pre-test
evidence and troubleshooting.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


TAIPEI_TZ = timezone(timedelta(hours=8))
DEFAULT_KUBECONFIG = "/home/hpe/CRAN/ming-kubeconfig.yaml"
DEFAULT_KUBECTL = "/home/hpe/CRAN/kubectl"
DEFAULT_HELM = "/home/linuxbrew/.linuxbrew/bin/helm"
DEFAULT_RAPP_URL = "http://127.0.0.1:9090"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def taipei_iso(ts: datetime) -> str:
    return ts.astimezone(TAIPEI_TZ).isoformat(timespec="seconds")


def run_capture(name: str, cmd: list[str], out_dir: Path, timeout: int = 20) -> dict:
    started = utc_now()
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        result = {
            "name": name,
            "command": cmd,
            "returncode": proc.returncode,
            "started_utc": iso_z(started),
            "finished_utc": iso_z(utc_now()),
            "stdout_file": f"{name}.stdout.txt",
            "stderr_file": f"{name}.stderr.txt",
        }
        (out_dir / result["stdout_file"]).write_text(proc.stdout, encoding="utf-8", errors="replace")
        (out_dir / result["stderr_file"]).write_text(proc.stderr, encoding="utf-8", errors="replace")
        return result
    except Exception as exc:
        result = {
            "name": name,
            "command": cmd,
            "returncode": None,
            "started_utc": iso_z(started),
            "finished_utc": iso_z(utc_now()),
            "error": str(exc),
        }
        (out_dir / f"{name}.error.txt").write_text(str(exc) + "\n", encoding="utf-8")
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--rapp-url", default=DEFAULT_RAPP_URL)
    parser.add_argument("--kubeconfig", default=DEFAULT_KUBECONFIG)
    parser.add_argument("--kubectl", default=DEFAULT_KUBECTL)
    parser.add_argument("--helm", default=DEFAULT_HELM)
    parser.add_argument("--namespace", default="ming-ns")
    parser.add_argument("--amf-log", default="/home/hpe/open5gs_logs/amf.log")
    args = parser.parse_args()

    started = utc_now()
    out_dir = Path(args.output_dir) if args.output_dir else Path("runs") / (
        "status-snapshot-" + started.strftime("%Y%m%d-%H%M%S")
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    commands = [
        ("hostname", ["hostname"]),
        ("date", ["date", "-Iseconds"]),
        ("rapp_health", ["curl", "-sS", "--max-time", "5", f"{args.rapp_url.rstrip('/')}/health"]),
        ("rapp_config", ["curl", "-sS", "--max-time", "5", f"{args.rapp_url.rstrip('/')}/config"]),
        ("rapp_jobs", ["curl", "-sS", "--max-time", "5", f"{args.rapp_url.rstrip('/')}/jobs"]),
        ("helm_list", [args.helm, "list", "-n", args.namespace]),
        (
            "kubectl_pods",
            [args.kubectl, "--kubeconfig", args.kubeconfig, "get", "pods", "-n", args.namespace, "-o", "wide"],
        ),
        (
            "kubectl_deployments",
            [args.kubectl, "--kubeconfig", args.kubeconfig, "get", "deployments", "-n", args.namespace, "-o", "wide"],
        ),
        (
            "kubectl_nads",
            [
                args.kubectl,
                "--kubeconfig",
                args.kubeconfig,
                "get",
                "network-attachment-definitions",
                "-n",
                args.namespace,
            ],
        ),
        ("amf_tail", ["tail", "-n", "80", args.amf_log]),
    ]

    results = [run_capture(name, cmd, out_dir) for name, cmd in commands]
    summary = {
        "output_dir": str(out_dir),
        "started_utc": iso_z(started),
        "started_taipei": taipei_iso(started),
        "finished_utc": iso_z(utc_now()),
        "namespace": args.namespace,
        "rapp_url": args.rapp_url,
        "commands": results,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(str(out_dir))
    failed = [r for r in results if r.get("returncode") not in (0,)]
    if failed:
        print("Some snapshot commands failed; see summary.json and stderr files.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
