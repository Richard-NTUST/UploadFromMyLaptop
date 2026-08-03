import pandas as pd
import datetime
import sys
import os

# Configuration — accept optional CLI argument for run directory
DEFAULT_RUN_DIR = r"runs/2026-02-04/burst-experiment"
RUN_DIR = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RUN_DIR
MARKERS_FILE = os.path.join(RUN_DIR, "markers.csv")
POWER_FILE = os.path.join(RUN_DIR, "power_uw.txt")
OUTPUT_FILE = os.path.join(RUN_DIR, "analysis_summary.md")

# Fallback: if power_uw.txt is not in the run dir, check repo root (legacy)
if not os.path.exists(POWER_FILE) and os.path.exists("power_uw.txt"):
    print(f"Warning: {POWER_FILE} not found, falling back to ./power_uw.txt")
    POWER_FILE = "power_uw.txt"

def parse_power_file(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                # Assuming format: StartTimestamp [EndTimestamp] Power_uW
                # We take the last timestamp as the "sample time" and the last value as power
                try:
                    ts_str = parts[-2]
                    pwr_str = parts[-1]
                    
                    # specific fix for the weird first line format if needed, but the loop handles parts[-2]
                    # Line 1: 2026...T10:42:34Z 2026...T10:42:44Z 5273155
                    # Line 2: 2026...T10:42:54Z 13971049
                    
                    if len(parts) == 2:
                         ts_str = parts[0]
                    
                    dt = datetime.datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    pwr_w = float(pwr_str) / 1_000_000.0
                    data.append({'timestamp': dt.timestamp(), 'power_w': pwr_w})
                except ValueError:
                    continue
    return pd.DataFrame(data)

def parse_markers(filepath):
    # Timestamp,Label
    df = pd.read_csv(filepath)
    return df

def analyze_phases(power_df, markers_df):
    results = []
    
    # Process pairs of Start/Stop
    # Labels expected: Start_X, Stop_X
    
    # Sort markers
    markers_df = markers_df.sort_values('Timestamp')
    
    # Iterate through markers to find intervals
    current_start = None
    current_label = None
    
    for _, row in markers_df.iterrows():
        label = row['Label']
        ts = row['Timestamp']
        
        if label.startswith("Start_"):
            current_start = ts
            current_label = label.replace("Start_", "")
        elif label.startswith("Stop_") and current_start is not None:
            phase_label = label.replace("Stop_", "")
            if phase_label == current_label:
                # Found a valid interval
                mask = (power_df['timestamp'] >= current_start) & (power_df['timestamp'] <= ts)
                subset = power_df[mask]
                
                if not subset.empty:
                    stats = {
                        'Phase': phase_label,
                        'Duration_s': ts - current_start,
                        'Avg_Power_W': subset['power_w'].mean(),
                        'Min_Power_W': subset['power_w'].min(),
                        'Max_Power_W': subset['power_w'].max(),
                        'Samples': len(subset)
                    }
                    results.append(stats)
            
            current_start = None
    
    return pd.DataFrame(results)

def main():
    print(f"Reading power data from {POWER_FILE}...")
    power_df = parse_power_file(POWER_FILE)
    print(f"  → Loaded {len(power_df)} power samples")
    if len(power_df) > 0:
        print(f"  → Time range: {power_df['timestamp'].min():.2f} to {power_df['timestamp'].max():.2f}")
    
    print(f"Reading markers from {MARKERS_FILE}...")
    markers_df = parse_markers(MARKERS_FILE)
    print(f"  → Loaded {len(markers_df)} markers")
    if len(markers_df) > 0:
        print(f"  → Time range: {markers_df['Timestamp'].min():.2f} to {markers_df['Timestamp'].max():.2f}")
    
    print("Analyzing phases...")
    results_df = analyze_phases(power_df, markers_df)
    print(f"  → Generated {len(results_df)} phase summaries")
    
    if len(results_df) == 0:
        print("\nError: No phases were successfully analyzed. Check that power timestamps overlap with marker timestamps.")
        return
    
    print("\nResults:")
    print(results_df.to_markdown(index=False))
    
    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Burst vs Smooth Power Analysis\n\n")
        f.write(f"**Date:** {datetime.date.today()}\n")
        f.write(f"**Power Source:** {POWER_FILE}\n\n")
        f.write(results_df.to_markdown(index=False))
        f.write("\n\n## Key Findings\n")
        
        # Calculate savings
        smooth_row = results_df[results_df['Phase'].str.contains("Smooth")]
        burst_row = results_df[results_df['Phase'].str.contains("Burst")]
        
        if not smooth_row.empty and not burst_row.empty:
            smooth_val = smooth_row.iloc[0]['Avg_Power_W']
            burst_val = burst_row.iloc[0]['Avg_Power_W']
            savings_w = smooth_val - burst_val
            savings_pct = (savings_w / smooth_val) * 100
            
            f.write(f"- **Smooth Power:** {smooth_val:.2f} W\n")
            f.write(f"- **Burst Power:** {burst_val:.2f} W\n")
            f.write(f"- **Savings:** {savings_w:.2f} W ({savings_pct:.1f}%)\n")
            
    print(f"\nAnalysis saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
