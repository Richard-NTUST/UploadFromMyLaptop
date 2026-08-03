#!/bin/bash

set -euo pipefail

# Week 3 / Week 4 sweep driver
# - Produces markers.csv + iperf logs in OUTPUT_DIR
# - Intended to pair with Scaphandre power capture into power_uw.txt
#
# IMPORTANT:
# - If you want a controlled target rate (e.g., 30G/60G), use UDP mode.
# - In TCP mode, iperf3 does best-effort; the "target" values are not enforced.

# Configuration (override any of these via environment variables)
TARGET_HOST="${TARGET_HOST:-localhost}"            # Change this to the O-RU/DUT IP for the real run
IPERF_PORT="${IPERF_PORT:-5201}"
MODE="${MODE:-udp}"                               # udp | tcp

TARGET_L="${TARGET_L:-30G}"
TARGET_M="${TARGET_M:-60G}"
TARGET_H="${TARGET_H:-90G}"                        # For UDP, set an explicit max (e.g., 90G). For TCP, any value is informational.

DURATION="${DURATION:-120}"
IDLE="${IDLE:-60}"
ROUNDS="${ROUNDS:-3}"

OUTPUT_DIR="${OUTPUT_DIR:-runs/current_sweep}"
MARKER_FILE="$OUTPUT_DIR/markers.csv"

# Ensure output dir exists
mkdir -p $OUTPUT_DIR

# Function to log marker
log_marker() {
    LABEL=$1
    # ISO 8601 UTC timestamp
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "$TS,$LABEL" >> $MARKER_FILE
    echo "[$TS] MARKER: $LABEL"
}

# Function to run load
run_load() {
    BW=$1
    NAME=$2
    
    echo "Starting $NAME (Target: $BW)..."
    log_marker "Start_$NAME"

    if [ "$MODE" = "udp" ]; then
        # UDP mode: -b enforces the target rate
        iperf3 -c "$TARGET_HOST" -p "$IPERF_PORT" -t "$DURATION" -u -b "$BW" -P 1 > "$OUTPUT_DIR/iperf_${NAME}.txt"
    elif [ "$MODE" = "tcp" ]; then
        # TCP mode: best-effort (no enforced bitrate)
        iperf3 -c "$TARGET_HOST" -p "$IPERF_PORT" -t "$DURATION" -P 1 > "$OUTPUT_DIR/iperf_${NAME}.txt"
    else
        echo "ERROR: Unknown MODE='$MODE' (expected 'udp' or 'tcp')" >&2
        exit 2
    fi
    
    echo "Finished $NAME"
    log_marker "Stop_$NAME"
}

# --- Main Sequence ---

echo "Starting Week 3 Load Sweep Experiment..."
echo "Markers will be saved to $MARKER_FILE"
echo "Mode: $MODE"
echo "Target host: $TARGET_HOST:$IPERF_PORT"

# 1. Initial Idle
echo "Initial Idle ($IDLE s)..."
log_marker "Start_Initial_Idle"
sleep $IDLE
log_marker "Stop_Initial_Idle"

# 2. Sweep Loops
for ((i=1; i<=ROUNDS; i++)); do
    echo "=== Round $i of $ROUNDS ==="
    
    # Load L
    run_load $TARGET_L "Load_L_Run$i"
    echo "Cool-down ($IDLE s)..."
    sleep $IDLE
    
    # Load M
    run_load $TARGET_M "Load_M_Run$i"
    echo "Cool-down ($IDLE s)..."
    sleep $IDLE
    
    # Load H
    run_load $TARGET_H "Load_H_Run$i"
    echo "Cool-down ($IDLE s)..."
    sleep $IDLE
done

echo "Experiment Complete."
