#!/bin/bash

set -euo pipefail

# One-command runner for the Week 4 gap-analysis pipeline inputs.
# Produces a new run folder containing:
# - power_uw.txt (Scaphandre host power, microwatts)
# - markers.csv  (UTC markers)
# - iperf_*.txt   (iperf client logs)
#
# Prereqs on Ubuntu:
# - Scaphandre exporter is running and serving /metrics (default: http://localhost:8080/metrics)
# - iperf3 server is running on the target host (default port 5201)
#
# Usage examples:
#   TARGET_HOST=10.0.0.2 MODE=udp TARGET_L=10G TARGET_M=40G TARGET_H=80G ./scripts/run_week4_gap_run.sh
#   OUTPUT_DIR=runs/2026-01-28/sweep-01 ./scripts/run_week4_gap_run.sh

# ---- Config (override via env vars) ----
TARGET_HOST="${TARGET_HOST:-192.168.1.15}"
IPERF_PORT="${IPERF_PORT:-5201}"
MODE="${MODE:-udp}"              # udp | tcp

# Traffic targets should match the real link capacity.
# You can always override via env vars, e.g. TARGET_L=200M TARGET_M=500M TARGET_H=900M
TARGET_L="${TARGET_L:-}"
TARGET_M="${TARGET_M:-}"
TARGET_H="${TARGET_H:-}"

DURATION="${DURATION:-180}"
IDLE="${IDLE:-60}"
ROUNDS="${ROUNDS:-3}"

SCAPHANDRE_URL="${SCAPHANDRE_URL:-http://localhost:8080/metrics}"
POWER_SAMPLE_PERIOD_SEC="${POWER_SAMPLE_PERIOD_SEC:-10}"

DEFAULT_DATE_UTC="$(date -u +%Y-%m-%d)"
DEFAULT_TIME_UTC="$(date -u +%H%M%S)"
OUTPUT_DIR="${OUTPUT_DIR:-runs/${DEFAULT_DATE_UTC}/sweep-${DEFAULT_TIME_UTC}}"

# ---- Helpers ----
require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "ERROR: missing command '$1'" >&2; exit 127; }
}

resolve_route_iface() {
  local host="$1"
  ip route get "$host" 2>/dev/null | awk '{for (i=1;i<=NF;i++) if ($i=="dev") {print $(i+1); exit}}'
}

read_iface_speed_mbps() {
  local iface="$1"

  # Kernel-provided; may be missing or "-1" (unknown), especially on Wi-Fi.
  if [[ -r "/sys/class/net/$iface/speed" ]]; then
    local speed
    speed="$(cat "/sys/class/net/$iface/speed" 2>/dev/null || true)"
    if [[ "$speed" =~ ^[0-9]+$ ]] && [[ "$speed" -gt 0 ]]; then
      echo "$speed"
      return 0
    fi
  fi

  echo ""
  return 1
}

set_default_targets_from_speed() {
  # Only fill defaults if user didn't provide explicit targets.
  if [[ -n "${TARGET_L}" && -n "${TARGET_M}" && -n "${TARGET_H}" ]]; then
    return 0
  fi

  local iface speed_mbps
  iface="$(resolve_route_iface "$TARGET_HOST")"
  speed_mbps="$(read_iface_speed_mbps "$iface" || true)"

  echo "Egress interface: ${iface:-unknown}"
  if [[ -n "$speed_mbps" ]]; then
    echo "Detected link speed: ${speed_mbps} Mb/s"
  else
    echo "Detected link speed: unknown (set TARGET_L/M/H manually)"
  fi

  if [[ -z "$TARGET_L" || -z "$TARGET_M" || -z "$TARGET_H" ]]; then
    # If we can't detect speed (common on Wi-Fi), default conservatively.
    # These are meant to produce clear state changes without saturating typical Wi-Fi links.
    if [[ -z "$speed_mbps" ]] && [[ "${iface:-}" == wl* ]]; then
      TARGET_L="${TARGET_L:-50M}"
      TARGET_M="${TARGET_M:-150M}"
      TARGET_H="${TARGET_H:-300M}"
      return 0
    fi

    if [[ -n "$speed_mbps" && "$speed_mbps" -ge 8000 ]]; then
      TARGET_L="${TARGET_L:-3G}"
      TARGET_M="${TARGET_M:-6G}"
      TARGET_H="${TARGET_H:-9G}"
    elif [[ -n "$speed_mbps" && "$speed_mbps" -ge 2000 ]]; then
      TARGET_L="${TARGET_L:-800M}"
      TARGET_M="${TARGET_M:-1500M}"
      TARGET_H="${TARGET_H:-2300M}"
    else
      TARGET_L="${TARGET_L:-200M}"
      TARGET_M="${TARGET_M:-500M}"
      TARGET_H="${TARGET_H:-900M}"
    fi
  fi
}

check_http_ok() {
  local url="$1"
  curl -fsS "$url" >/dev/null
}

# ---- Preflight ----
require_cmd bash
require_cmd curl
require_cmd awk
require_cmd iperf3
require_cmd date
require_cmd mkdir
require_cmd tee

mkdir -p "$OUTPUT_DIR"

echo "Run folder: $OUTPUT_DIR"
echo "Target host: $TARGET_HOST:$IPERF_PORT"
echo "Mode: $MODE"
echo "Targets: L=$TARGET_L M=$TARGET_M H=$TARGET_H"
echo "Timing: DURATION=$DURATION IDLE=$IDLE ROUNDS=$ROUNDS"

echo "Checking Scaphandre exporter: $SCAPHANDRE_URL"
check_http_ok "$SCAPHANDRE_URL" || {
  echo "ERROR: cannot reach Scaphandre metrics at $SCAPHANDRE_URL" >&2
  echo "Start Scaphandre exporter first, then retry." >&2
  exit 1
}

set_default_targets_from_speed

echo "Checking iperf3 connectivity (quick handshake)..."
iperf3 -c "$TARGET_HOST" -p "$IPERF_PORT" -t 1 --connect-timeout 1000 >/dev/null || {
  echo "ERROR: iperf3 server not reachable at $TARGET_HOST:$IPERF_PORT" >&2
  echo "Start: iperf3 -s -p $IPERF_PORT (on the target), then retry." >&2
  exit 1
}

# ---- Power capture (background) ----
POWER_OUT="$OUTPUT_DIR/power_uw.txt"
MARKERS_OUT="$OUTPUT_DIR/markers.csv"

echo "Starting power capture -> $POWER_OUT"
(
  while true; do
    printf "%s " "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    curl -s "$SCAPHANDRE_URL" | awk '!/^#/ && $1 ~ /^scaph_host_power_microwatts(\{|$)/ {print $NF; exit}'
    sleep "$POWER_SAMPLE_PERIOD_SEC"
  done
) | tee "$POWER_OUT" >/dev/null &
POWER_PID=$!

cleanup() {
  echo "Stopping power capture (pid=$POWER_PID)"
  kill "$POWER_PID" 2>/dev/null || true
}
trap cleanup EXIT

# ---- Sweep ----
echo "Starting sweep -> $MARKERS_OUT"
OUTPUT_DIR="$OUTPUT_DIR" \
MARKER_FILE="$MARKERS_OUT" \
TARGET_HOST="$TARGET_HOST" \
IPERF_PORT="$IPERF_PORT" \
MODE="$MODE" \
TARGET_L="$TARGET_L" \
TARGET_M="$TARGET_M" \
TARGET_H="$TARGET_H" \
DURATION="$DURATION" \
IDLE="$IDLE" \
ROUNDS="$ROUNDS" \
./scripts/week3_load_sweep.sh

echo "Done. Captured inputs for Week 4 notebook in: $OUTPUT_DIR" 
