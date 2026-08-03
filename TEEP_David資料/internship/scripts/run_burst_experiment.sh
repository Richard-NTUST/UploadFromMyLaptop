#!/bin/bash

# ==============================================================================
# Script: run_burst_experiment.sh
# Purpose: Compare "Smooth" (FDM-like) vs "Bursty" (TDM-like) traffic power.
#          Validates if "Duty Cycling" saves platform power compared to constant load.
#
# Hypothesis:
#   - Smooth: 30% Constant Load -> CPU stays in C0 (active) state -> Higher Energy
#   - Burst:  100% Load for 30% time -> CPU races to sleep (C6) -> Lower Energy
# ==============================================================================

# ----------------- Configuration -----------------
OUTPUT_DIR="runs/$(date +%Y-%m-%d)/burst-experiment"
MARKER_FILE="$OUTPUT_DIR/markers.csv"
DURATION_TOTAL=180     # Total duration for comparison window (seconds)
BURST_ON=3             # Time ON (seconds)
BURST_OFF=7            # Time OFF (seconds)
# Duty Cycle = 3 / (3+7) = 30%

# Rate Targets (Adjust based on your max link speed)
# Assuming a 10G link for this example. Adjust MAX_RATE variable below!
MAX_RATE="90G"         # Burst Speed (100%)
AVG_RATE="30G"          # Smooth Speed (30%)

IPERF_SERVER="127.0.0.1" # Localhost or target IP

# ----------------- Setup -----------------
mkdir -p "$OUTPUT_DIR"
echo "Timestamp,Label" > "$MARKER_FILE"

log_marker() {
    echo "$(date +%s.%N),$1" >> "$MARKER_FILE"
    echo "MARKER: $1"
}

echo "=================================================="
echo "      O-RU Power Experiment: Smooth vs Burst      "
echo "=================================================="
echo "Output Directory: $OUTPUT_DIR"
echo "Max Rate (Burst): $MAX_RATE"
echo "Avg Rate (Smooth): $AVG_RATE"
echo "Comparison Window: ${DURATION_TOTAL}s"
echo "=================================================="

# ----------------- Phase 1: Idle Baseline -----------------
echo ""
echo "[Phase 1] Warm-up and Idle Baseline (60s)..."
log_marker "Start_Idle_Baseline"
sleep 60
log_marker "Stop_Idle_Baseline"


# ----------------- Phase 2: Smooth Load (FDM Proxy) -----------------
echo ""
echo "[Phase 2] Running SMOOTH Load (Constant $AVG_RATE)..."
echo "   -> Simulates current srsRAN FDM behavior (Always Active)"

log_marker "Start_Smooth_30pct"

# Run single constant flow for total duration
iperf3 -c $IPERF_SERVER -u -b $AVG_RATE -t $DURATION_TOTAL -P 1 > "$OUTPUT_DIR/iperf_smooth.txt" &
IPERF_PID=$!

wait $IPERF_PID
log_marker "Stop_Smooth_30pct"

echo "   -> Cooldown (30s)..."
sleep 30


# ----------------- Phase 3: Burst Load (TDM Proxy) -----------------
echo ""
echo "[Phase 3] Running BURST Load ($MAX_RATE On/Off)..."
echo "   -> Simulates proposed TDM behavior (Race-to-Sleep)"
echo "   -> Cycle: ${BURST_ON}s ON / ${BURST_OFF}s OFF"

log_marker "Start_Burst_30pct"

# Calculate loops needed
CYCLE_TIME=$((BURST_ON + BURST_OFF))
LOOPS=$((DURATION_TOTAL / CYCLE_TIME))

echo "   -> Starting $LOOPS burst cycles..."

for ((i=1; i<=LOOPS; i++)); do
    # Burst ON (High Load)
    iperf3 -c $IPERF_SERVER -u -b $MAX_RATE -t $BURST_ON -P 1 >> "$OUTPUT_DIR/iperf_burst.txt" 2>&1
    
    # Burst OFF (Sleep)
    sleep $BURST_OFF
    
    echo -ne "      Cycle $i/$LOOPS complete... \r"
done

echo ""
log_marker "Stop_Burst_30pct"


# ----------------- Phase 4: Idle Post-Check -----------------
echo ""
echo "[Phase 4] Post-run Idle (30s)..."
log_marker "Start_Idle_End"
sleep 30
log_marker "Stop_Idle_End"

echo ""
echo "=================================================="
echo "Experiment Complete."
echo "1. Verify markers at: $MARKER_FILE"
echo "2. Don't forget to grab power_uw.txt from Scaphandre!"
echo "=================================================="
