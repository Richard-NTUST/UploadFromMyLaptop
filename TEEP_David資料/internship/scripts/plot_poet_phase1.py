#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Configuration
RUN_DIR = "runs/poet_phase1_test"
MARKERS_FILE = os.path.join(RUN_DIR, "markers.csv")
POWER_FILE = os.path.join(RUN_DIR, "power_uj.txt")
OUTPUT_PLOT = "assets/poet_phase1/power_validation.png"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_PLOT), exist_ok=True)

# Load markers
try:
    markers = pd.read_csv(MARKERS_FILE, parse_dates=["timestamp"])
    start_time = markers[markers["event"] == "RUN_START"]["timestamp"].iloc[0]
    end_time = markers[markers["event"] == "RUN_END"]["timestamp"].iloc[0]
    load_start = markers[markers["event"] == "LOAD_START"]["timestamp"].iloc[0]
    load_end = markers[markers["event"] == "LOAD_END"]["timestamp"].iloc[0]
except Exception as e:
    print(f"Error reading markers: {e}")
    exit(1)

# Load power data
try:
    # Read the space-separated power_uw.txt file
    # Format: 2026-06-26T01:29:10Z 12345678 (where 12345678 is scaph_host_energy_microjoules)
    df = pd.read_csv(POWER_FILE, sep=" ", header=None, names=["timestamp", "energy_uj"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Calculate power (Watts) = diff(energy_uj) / 1e6 / diff(seconds)
    df["energy_diff"] = df["energy_uj"].diff()
    df["time_diff"] = df["timestamp"].diff().dt.total_seconds()
    df["power_w"] = (df["energy_diff"] / 1e6) / df["time_diff"]
    
    # Drop first row which has NaN from diff
    df = df.dropna()
except Exception as e:
    print(f"Error reading power data: {e}")
    exit(1)

# Filter by run time
df = df[(df["timestamp"] >= start_time) & (df["timestamp"] <= end_time)]

if df.empty:
    print("No power data found for the run duration.")
    exit(1)

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(df["timestamp"], df["power_w"], label="Host Power (Scaphandre)", color="blue")

# Annotate states
plt.axvspan(start_time, load_start, color="gray", alpha=0.2, label="Idle")
plt.axvspan(load_start, load_end, color="red", alpha=0.2, label="Load (stress-ng)")
plt.axvspan(load_end, end_time, color="gray", alpha=0.2)

plt.title("POET Phase 1: Measurement Stack Validation")
plt.xlabel("Time (UTC)")
plt.ylabel("Power (W)")
plt.grid(True)
plt.legend()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.gcf().autofmt_xdate()

plt.tight_layout()
plt.savefig(OUTPUT_PLOT)
print(f"Plot saved to {OUTPUT_PLOT}")

