import argparse
import json
import re
import statistics
from pathlib import Path


def parse_cleaned_power_md(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    parts = re.split(r"^#\s*---\s*(STAGE\s*\d+:[^\n-]*[^\n]*)\s*---\s*$", text, flags=re.M)

    stages = []
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1]
        values_uw = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(\d+)$", line)
            if match:
                values_uw.append(int(match.group(2)))
        if values_uw:
            stages.append((header, values_uw))

    return stages


def summarize_stage(values_uw):
    mean_uw = statistics.mean(values_uw)
    return {
        "n": len(values_uw),
        "mean_w": mean_uw / 1e6,
        "min_w": min(values_uw) / 1e6,
        "max_w": max(values_uw) / 1e6,
    }


def read_iperf_json(path: Path):
    iperf = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    end = iperf.get("end", {})
    sum_received = end.get("sum_received") or end.get("sum") or {}
    sum_sent = end.get("sum_sent") or {}
    return {
        "sum_received": sum_received,
        "sum_sent": sum_sent,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Path to run folder (e.g., runs/2026-01-20)")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    cleaned = run_dir / "cleaned_power_uw.md"
    iperf_json = run_dir / "iperf_tcp_loadm_300s.json"

    if not cleaned.exists():
        raise SystemExit(f"Missing {cleaned}")

    stages = parse_cleaned_power_md(cleaned)
    print("Stage power summary (from cleaned_power_uw.md):")
    for header, values_uw in stages:
        s = summarize_stage(values_uw)
        print(f"- {header}: n={s['n']} mean={s['mean_w']:.3f} W (min={s['min_w']:.3f}, max={s['max_w']:.3f})")

    if iperf_json.exists():
        ip = read_iperf_json(iperf_json)
        recv = ip.get("sum_received", {})
        if recv:
            bps = recv.get("bits_per_second")
            secs = recv.get("seconds")
            bytes_ = recv.get("bytes")
            print("\niperf3 TCP summary_received:")
            print(f"  seconds: {secs}")
            print(f"  bytes: {bytes_}")
            print(f"  bits_per_second: {bps}")
            if bps:
                print(f"  throughput_gbps: {bps/1e9:.3f}")
        sent = ip.get("sum_sent", {})
        if sent and sent.get("bits_per_second"):
            print(f"iperf3 TCP summary_sent throughput_gbps: {sent['bits_per_second']/1e9:.3f}")
    else:
        print("\nNo iperf JSON found in run folder.")


if __name__ == "__main__":
    main()
