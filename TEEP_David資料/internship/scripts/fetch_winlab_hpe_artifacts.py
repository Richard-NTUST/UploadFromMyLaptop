#!/usr/bin/env python3
"""
Fetch a WINLAB HPE evidence run folder to the local machine.

Examples:
  python scripts/fetch_winlab_hpe_artifacts.py \
    --remote-run runs/workflow-ocloud-dry-20260703-073208 \
    --dry-run

  python scripts/fetch_winlab_hpe_artifacts.py \
    --remote-run runs/workflow-ocloud-dry-20260703-073208 \
    --output-dir runs/hpe_artifacts
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_HOST = "hpe@192.168.8.26"
DEFAULT_REMOTE_BASE = "/home/hpe/winlab_e2e_rapp"


def default_identity() -> str:
    return str(Path.home() / ".ssh" / "codex_hpe_tmp")


def run(cmd: list[str], dry_run: bool = False) -> subprocess.CompletedProcess[str]:
    print(" ".join(cmd))
    if dry_run:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def remote_join(base: str, run_path: str) -> str:
    run_path = run_path.strip()
    if run_path.startswith("/"):
        return run_path
    return base.rstrip("/") + "/" + run_path.lstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--identity", default=default_identity())
    parser.add_argument("--remote-base", default=DEFAULT_REMOTE_BASE)
    parser.add_argument("--remote-run", required=True, help="Remote run folder, absolute or relative to --remote-base")
    parser.add_argument("--output-dir", default="runs/hpe_artifacts")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-remote-check", action="store_true")
    args = parser.parse_args()

    remote_path = remote_join(args.remote_base, args.remote_run)
    local_root = Path(args.output_dir)
    local_target = local_root / Path(remote_path).name

    if not shutil.which("ssh"):
        raise SystemExit("Missing ssh executable in PATH")
    if not shutil.which("scp"):
        raise SystemExit("Missing scp executable in PATH")

    ssh_base = [
        "ssh",
        "-i",
        args.identity,
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        args.host,
    ]

    if not args.skip_remote_check:
        check = run(ssh_base + ["test", "-d", remote_path], dry_run=args.dry_run)
        if check.returncode != 0:
            if check.stderr:
                print(check.stderr, file=sys.stderr)
            raise SystemExit(f"Remote directory not found or inaccessible: {remote_path}")

    local_root.mkdir(parents=True, exist_ok=True)
    scp_cmd = [
        "scp",
        "-r",
        "-i",
        args.identity,
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{args.host}:{remote_path}",
        str(local_root),
    ]
    result = run(scp_cmd, dry_run=args.dry_run)
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode

    if args.dry_run:
        print(f"Dry run only. Would fetch to: {local_target}")
    else:
        print(f"Fetched to: {local_target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
