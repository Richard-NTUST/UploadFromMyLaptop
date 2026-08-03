#!/bin/bash
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_DIR="runs/poet_phase1_test"
MARKERS_FILE="$OUTPUT_DIR/markers.csv"
POWER_FILE="$OUTPUT_DIR/power_uj.txt"   # energy in micro-joules; power derived in plot script
IDLE_WAIT=10
LOAD_TIME=30

# ── Preflight ─────────────────────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"

# Confirm we can read RAPL. It is root-owned so we need sudo once here to cache credentials.
echo "Checking RAPL access via sudo (you may be asked for your password once)..."
if ! sudo cat /sys/class/powercap/intel-rapl:0/energy_uj > /dev/null 2>&1; then
    echo "ERROR: Cannot read RAPL energy_uj. Make sure sudo works and RAPL is available." >&2
    exit 1
fi
echo "RAPL access OK."

# Collect all top-level RAPL package paths (intel-rapl:N, not sub-domains like intel-rapl:0:0)
RAPL_PATHS=$(ls /sys/class/powercap/ | grep -E '^intel-rapl:[0-9]+$' | \
    awk '{print "/sys/class/powercap/" $1 "/energy_uj"}')
echo "RAPL domains: $(echo $RAPL_PATHS | tr ' ' '\n' | xargs -I{} basename {} ../)"

# ── Init files ────────────────────────────────────────────────────────────────
echo "timestamp,event" > "$MARKERS_FILE"
> "$POWER_FILE"

# ── Background RAPL scraper (1 Hz) ───────────────────────────────────────────
echo "Starting RAPL power scraper (1 Hz)..."
(
  while true; do
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    # Sum all RAPL package domains
    total=0
    for path in $RAPL_PATHS; do
      val=$(sudo cat "$path" 2>/dev/null || echo 0)
      total=$((total + val))
    done
    echo "$ts $total"
    sleep 1
  done
) >> "$POWER_FILE" 2>/dev/null &
SCRAPER_PID=$!

cleanup() {
    kill "$SCRAPER_PID" 2>/dev/null || true
}
trap cleanup EXIT

# Log start marker
echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ'),RUN_START" >> "$MARKERS_FILE"
echo "RUN_START recorded. Waiting for idle baseline ($IDLE_WAIT seconds)..."
sleep $IDLE_WAIT

# Start CPU load
echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ'),LOAD_START" >> "$MARKERS_FILE"
echo "LOAD_START recorded. Starting CPU stress test ($LOAD_TIME seconds)..."
stress-ng --cpu 4 --timeout $LOAD_TIME

# Log end of load
echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ'),LOAD_END" >> "$MARKERS_FILE"
echo "LOAD_END recorded. Waiting for cool-down baseline ($IDLE_WAIT seconds)..."
sleep $IDLE_WAIT

# Log end marker
echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ'),RUN_END" >> "$MARKERS_FILE"
echo "RUN_END recorded."

# Stop scraper
echo "Stopping scraper..."
kill $SCRAPER_PID 2>/dev/null || true

echo "Phase 1 test complete. Results logged to $OUTPUT_DIR"
echo "  Power trace: $POWER_FILE"
echo "  Markers:     $MARKERS_FILE"
