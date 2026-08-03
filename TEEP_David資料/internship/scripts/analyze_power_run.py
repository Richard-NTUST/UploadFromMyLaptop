import argparse
import csv
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
MARKER_RE = re.compile(
    r"^-\s*(?P<label>[^:]+):\s*(?P<start>\d{2}:\d{2}:\d{2}Z)\s*to\s*(?P<end>\d{2}:\d{2}:\d{2}Z)\s*$"
)


def parse_utc(ts: str) -> datetime:
    # Example: 2026-01-20T06:05:14Z
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def parse_utc_hms_on_date(date_ymd: str, hmsz: str) -> datetime:
    # date_ymd: 2026-01-20, hmsz: 06:05:14Z
    return parse_utc(f"{date_ymd}T{hmsz[:-1]}Z")


@dataclass(frozen=True)
class Sample:
    t: datetime
    power_w: float


@dataclass(frozen=True)
class Window:
    label: str
    start: datetime
    end: datetime


def iter_power_samples_power_uw_txt(path: Path) -> Iterable[Sample]:
    """Parse `power_uw.txt` robustly.

    Expected normal lines: '<timestamp> <microwatts>'
    The first line may contain timestamp noise; we scan tokens and accept any valid (ts, int) pairs.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    tokens = re.split(r"\s+", text.strip())
    i = 0
    while i + 1 < len(tokens):
        ts = tokens[i]
        v = tokens[i + 1]
        if TS_RE.match(ts) and v.isdigit():
            try:
                yield Sample(t=parse_utc(ts), power_w=int(v) / 1e6)
            except ValueError:
                pass
            i += 2
            continue
        i += 1


def parse_markers_md(path: Path, default_date: str) -> List[Window]:
    windows: List[Window] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        m = MARKER_RE.match(line)
        if not m:
            continue
        label = m.group("label").strip()
        start = parse_utc_hms_on_date(default_date, m.group("start"))
        end = parse_utc_hms_on_date(default_date, m.group("end"))
        windows.append(Window(label=label, start=start, end=end))
    return windows


def window_samples(samples: List[Sample], window: Window) -> List[Sample]:
    # Treat end as exclusive to avoid including transition spikes at the boundary marker.
    return [s for s in samples if window.start <= s.t < window.end]


def mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def integrate_energy_j(samples: List[Sample]) -> float:
    """Approximate energy via trapezoidal integration over irregular samples."""
    if len(samples) < 2:
        return 0.0
    total_j = 0.0
    for a, b in zip(samples, samples[1:]):
        dt = (b.t - a.t).total_seconds()
        if dt <= 0:
            continue
        total_j += 0.5 * (a.power_w + b.power_w) * dt
    return total_j


def write_power_csv(samples: List[Sample], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp_utc", "power_w"])
        for s in samples:
            w.writerow([s.t.strftime("%Y-%m-%dT%H:%M:%SZ"), f"{s.power_w:.6f}"])


def svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def write_plot_svg(
    samples: List[Sample],
    windows: List[Window],
    out_path: Path,
    width: int = 1200,
    height: int = 420,
    margin: int = 50,
) -> None:
    if not samples:
        raise SystemExit("No samples available to plot")

    t0 = min(s.t for s in samples)
    t1 = max(s.t for s in samples)
    span_s = max(1.0, (t1 - t0).total_seconds())

    powers = [s.power_w for s in samples]
    p_min = min(powers)
    p_max = max(powers)
    # Avoid zero-height plot
    if math.isclose(p_min, p_max):
        p_min -= 1.0
        p_max += 1.0

    plot_w = width - 2 * margin
    plot_h = height - 2 * margin

    def x_for(t: datetime) -> float:
        return margin + plot_w * ((t - t0).total_seconds() / span_s)

    def y_for(p: float) -> float:
        # y grows downward in SVG
        return margin + plot_h * (1.0 - ((p - p_min) / (p_max - p_min)))

    pts = " ".join(f"{x_for(s.t):.2f},{y_for(s.power_w):.2f}" for s in samples)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')
        f.write('<rect x="0" y="0" width="100%" height="100%" fill="white"/>\n')

        # Axes
        f.write(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="#111" stroke-width="1"/>\n')
        f.write(f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="#111" stroke-width="1"/>\n')

        # Y labels (min/max)
        f.write(f'<text x="{margin}" y="{margin-10}" font-size="12" fill="#111">{p_max:.2f} W</text>\n')
        f.write(f'<text x="{margin}" y="{height-margin+20}" font-size="12" fill="#111">{p_min:.2f} W</text>\n')

        # Title
        f.write(
            f'<text x="{margin}" y="20" font-size="14" fill="#111">Plot 1: Power vs Time (UTC) — platform power under RU-like workload</text>\n'
        )

        # Window markers
        for w in windows:
            for t, label_suffix in [(w.start, "start"), (w.end, "end")]:
                if t < t0 or t > t1:
                    continue
                x = x_for(t)
                f.write(f'<line x1="{x:.2f}" y1="{margin}" x2="{x:.2f}" y2="{height-margin}" stroke="#c00" stroke-width="1" stroke-dasharray="4 4"/>\n')
            # label near start
            if w.start >= t0 and w.start <= t1:
                x = x_for(w.start) + 3
                y = margin + 14
                f.write(f'<text x="{x:.2f}" y="{y:.2f}" font-size="12" fill="#c00">{svg_escape(w.label)}</text>\n')

        # Line
        f.write(f'<polyline fill="none" stroke="#1f77b4" stroke-width="1.5" points="{pts}"/>\n')

        # Footer time range
        f.write(
            f'<text x="{margin}" y="{height-10}" font-size="12" fill="#111">{t0.strftime("%Y-%m-%dT%H:%M:%SZ")} → {t1.strftime("%Y-%m-%dT%H:%M:%SZ")}</text>\n'
        )

        f.write("</svg>\n")


def read_iperf_tcp_summary(path: Path) -> Tuple[Optional[float], Optional[float], Optional[int]]:
    """Return (throughput_gbps_received, seconds, bytes_received)."""
    iperf = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    end = iperf.get("end", {})
    recv = end.get("sum_received") or end.get("sum") or {}
    if not recv:
        return None, None, None

    bps = recv.get("bits_per_second")
    secs = recv.get("seconds")
    bytes_ = recv.get("bytes")

    gbps = (bps / 1e9) if isinstance(bps, (int, float)) else None
    seconds = secs if isinstance(secs, (int, float)) else None
    bytes_int = bytes_ if isinstance(bytes_, int) else None

    return gbps, seconds, bytes_int


def write_table_md(
    windows: List[Window],
    samples: List[Sample],
    iperf_gbps: Optional[float],
    out_path: Path,
) -> None:
    lines: List[str] = []
    lines.append("# Table 1 — Per-state Summary (Pilot Run 01)\n")
    lines.append("All power values are **platform power under RU-like workload** (Scaphandre on Ubuntu).\n")
    lines.append("| State | Window (UTC) | n | Mean Power (W) | Energy (J) | Duration (s) | Throughput (Gbps) | Efficiency (Gbps/W) |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")

    for w in windows:
        ws = window_samples(samples, w)
        powers = [s.power_w for s in ws]
        mean_p = mean(powers) if powers else float("nan")
        e_j = integrate_energy_j(ws)
        dur_s = (w.end - w.start).total_seconds()

        thr = ""
        eff = ""
        # Only apply iperf throughput to the load window (best-effort)
        if iperf_gbps is not None and w.label.strip().lower().startswith("load") and mean_p and not math.isnan(mean_p) and mean_p > 0:
            thr = f"{iperf_gbps:.3f}"
            eff = f"{(iperf_gbps / mean_p):.3f}"

        lines.append(
            "| "
            + " | ".join(
                [
                    w.label,
                    f"{w.start.strftime('%H:%M:%SZ')}–{w.end.strftime('%H:%M:%SZ')}",
                    str(len(ws)),
                    f"{mean_p:.3f}" if not math.isnan(mean_p) else "",
                    f"{e_j:.1f}",
                    f"{dur_s:.0f}",
                    thr,
                    eff,
                ]
            )
            + " |"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Path to run folder (e.g., runs/2026-01-20)")
    parser.add_argument(
        "--date",
        default=None,
        help="Date for markers (YYYY-MM-DD). Defaults to run folder name if it looks like YYYY-MM-DD.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    power_txt = run_dir / "power_uw.txt"
    markers = run_dir / "markers.md"
    iperf_json = run_dir / "iperf_tcp_loadm_300s.json"

    if not power_txt.exists():
        raise SystemExit(f"Missing {power_txt}")
    if not markers.exists():
        raise SystemExit(f"Missing {markers}")

    default_date = args.date
    if default_date is None:
        # best-effort: infer from run_dir name
        m = re.search(r"(\d{4}-\d{2}-\d{2})", str(run_dir))
        default_date = m.group(1) if m else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    samples = sorted(iter_power_samples_power_uw_txt(power_txt), key=lambda s: s.t)
    windows = parse_markers_md(markers, default_date)

    derived_dir = run_dir / "derived"
    write_power_csv(samples, derived_dir / "power.csv")
    write_plot_svg(samples, windows, derived_dir / "plot_1_power_vs_time.svg")

    iperf_gbps, _, _ = (None, None, None)
    if iperf_json.exists():
        iperf_gbps, _, _ = read_iperf_tcp_summary(iperf_json)

    write_table_md(windows, samples, iperf_gbps, derived_dir / "table_1_per_state.md")

    print("Wrote:")
    print(f"- {derived_dir / 'power.csv'}")
    print(f"- {derived_dir / 'plot_1_power_vs_time.svg'}")
    print(f"- {derived_dir / 'table_1_per_state.md'}")


if __name__ == "__main__":
    main()
