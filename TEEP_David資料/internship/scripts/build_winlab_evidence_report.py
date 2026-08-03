#!/usr/bin/env python3
"""
Build a compact Markdown report from WINLAB status/probe evidence folders.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return None


def read_text(path: Path, max_lines: int = 80) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[:max_lines])


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        return list(csv.DictReader(f))


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    if not rows:
        return []
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(item) for item in row) + " |")
    return out


def fenced(label: str, text: str) -> list[str]:
    if not text.strip():
        return []
    return [f"```{label}", text.strip(), "```"]


def summarize_snapshot(run_dir: Path, lines: list[str]) -> None:
    summary = read_json(run_dir / "summary.json")
    if not summary or "commands" not in summary:
        return

    lines.extend(["## Status Snapshot", ""])
    lines.append(f"- Started UTC: `{summary.get('started_utc', '')}`")
    lines.append(f"- Started Taipei: `{summary.get('started_taipei', '')}`")
    lines.append(f"- Namespace: `{summary.get('namespace', '')}`")
    lines.append(f"- rApp URL: `{summary.get('rapp_url', '')}`")
    lines.append("")

    command_rows = []
    for item in summary.get("commands", []):
        command_rows.append([item.get("name", ""), item.get("returncode", ""), item.get("stdout_file", "")])
    lines.extend(md_table(["Check", "Return Code", "Output"], command_rows))
    lines.append("")

    for title, filename in [
        ("rApp Health", "rapp_health.stdout.txt"),
        ("Helm Releases", "helm_list.stdout.txt"),
        ("Pods", "kubectl_pods.stdout.txt"),
        ("NetworkAttachmentDefinitions", "kubectl_nads.stdout.txt"),
    ]:
        text = read_text(run_dir / filename)
        if text:
            lines.extend([f"### {title}", ""])
            lines.extend(fenced("text", text))
            lines.append("")


def summarize_probe(run_dir: Path, lines: list[str]) -> None:
    request_payload = read_json(run_dir / "request_payload.json")
    submission = read_json(run_dir / "submission.json")
    job_latest = read_json(run_dir / "job_latest.json")
    probe_summary = read_json(run_dir / "summary.json")
    if not any([request_payload, submission, job_latest]):
        return

    lines.extend(["## rApp Probe", ""])
    if request_payload:
        lines.extend(["### Request", ""])
        lines.extend(fenced("json", json.dumps(request_payload, indent=2, sort_keys=True)))
        lines.append("")
    if submission:
        lines.extend(["### Submission", ""])
        lines.extend(fenced("json", json.dumps(submission, indent=2, sort_keys=True)))
        lines.append("")
    if job_latest:
        lines.extend(["### Final Job Status", ""])
        job_rows = [
            ["job_id", job_latest.get("id", "")],
            ["status", job_latest.get("status", "")],
            ["returncode", job_latest.get("returncode", "")],
            ["created_at", job_latest.get("created_at", "")],
            ["started_at", job_latest.get("started_at", "")],
            ["finished_at", job_latest.get("finished_at", "")],
        ]
        lines.extend(md_table(["Field", "Value"], job_rows))
        lines.append("")
        output_tail = job_latest.get("output_tail") or []
        if output_tail:
            lines.extend(["### Job Output Tail", ""])
            lines.extend(fenced("text", "\n".join(output_tail)))
            lines.append("")
    elif probe_summary:
        lines.extend(["### Probe Summary", ""])
        lines.extend(fenced("json", json.dumps(probe_summary, indent=2, sort_keys=True)))
        lines.append("")

    markers = read_csv_rows(run_dir / "markers.csv")
    if markers:
        rows = [[r.get("label", ""), r.get("timestamp_utc", ""), r.get("timestamp_taipei", ""), r.get("notes", "")] for r in markers]
        lines.extend(["### Markers", ""])
        lines.extend(md_table(["Label", "UTC", "Taipei", "Notes"], rows))
        lines.append("")


def summarize_outlets(run_dir: Path, lines: list[str]) -> None:
    rows = read_csv_rows(run_dir / "candidate_outlet_power_summary.csv")
    if not rows:
        return
    lines.extend(["## Candidate Outlet Power", ""])
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row.get("outlet", ""),
                row.get("n", ""),
                row.get("duration_s", ""),
                row.get("mean_w", ""),
                row.get("min_w", ""),
                row.get("max_w", ""),
                row.get("energy_j", ""),
            ]
        )
    lines.extend(md_table(["Outlet", "Samples", "Duration s", "Mean W", "Min W", "Max W", "Energy J"], table_rows))
    lines.append("")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", help="Status snapshot or probe run directory")
    parser.add_argument("--output", default="run_report.md")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        raise SystemExit(f"Missing run directory: {run_dir}")

    out_path = run_dir / args.output
    lines = [
        "# WINLAB Evidence Report",
        "",
        f"- Source folder: `{run_dir}`",
        "",
    ]

    summarize_snapshot(run_dir, lines)
    summarize_probe(run_dir, lines)
    summarize_outlets(run_dir, lines)

    if len(lines) <= 4:
        lines.extend(["No recognized WINLAB evidence files were found.", ""])

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
