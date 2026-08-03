import os
import re
import matplotlib.pyplot as plt
import glob
import numpy as np

# Path configurations
LOG_DIR = r'runs/2026-01-21/bandwidth-test'
OUTPUT_PLOT = os.path.join(LOG_DIR, 'bandwidth_validation.png')

def parse_iperf_log(filepath):
    """
    Parses an iperf3 text log file and returns a list of (time, bitrate_gbps) tuples.
    """
    data_points = []
    # Regex to capture: Interval (start-end), Bitrate Value, Bitrate Unit
    # Example: [  5]   1.00-2.00   sec  7.84 GBytes  67.4 Gbits/sec    0   2.69 MBytes
    regex = re.compile(r'\[\s*\d+\]\s+(\d+\.\d+)-(\d+\.\d+)\s+sec\s+[\d\.]+\s+\w+ytes\s+(\d+\.\d+)\s+(\w+)bits/sec')

    with open(filepath, 'r') as f:
        for line in f:
            match = regex.search(line)
            if match:
                end_time = float(match.group(2))
                bitrate_val = float(match.group(3))
                unit = match.group(4)

                # Normalize to Gbps
                if unit == 'G':
                    bitrate_gbps = bitrate_val
                elif unit == 'M':
                    bitrate_gbps = bitrate_val / 1000.0
                elif unit == 'K':
                    bitrate_gbps = bitrate_val / 1000000.0
                else:
                    bitrate_gbps = bitrate_val # Assume bits? unlikely in this context but safe fallback

                data_points.append((end_time, bitrate_gbps))
    
    return data_points

def main():
    if not os.path.exists(LOG_DIR):
        print(f"Directory not found: {LOG_DIR}")
        return

    # Files pattern: iperf_Load_{Level}_Run{RunNum}_Run{RunNum}.txt
    files = glob.glob(os.path.join(LOG_DIR, 'iperf_*.txt'))
    
    if not files:
        print(f"No log files found in {LOG_DIR}")
        return

    plt.figure(figsize=(12, 6))
    
    colors = {'L': 'green', 'M': 'orange', 'H': 'red'}
    labels = {'L': 'Low Load (Target 30G)', 'M': 'Medium Load (Target 60G)', 'H': 'High Load (Unlim)'}
    
    # Track which labels we've added to legend to avoid duplicates
    added_labels = set()

    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        # Extract Load Level (L, M, H)
        parts = filename.split('_')
        if len(parts) >= 3:
            load_level = parts[2] # Load, L
        else:
            continue

        data = parse_iperf_log(filepath)
        if not data:
            continue
            
        times, bitrates = zip(*data)
        
        label = labels.get(load_level, load_level)
        color = colors.get(load_level, 'blue')
        
        # Only add label to legend once
        plot_label = label if label not in added_labels else "_nolegend_"
        added_labels.add(label)
        
        plt.plot(times, bitrates, label=plot_label, color=color, alpha=0.7, linewidth=2)

    plt.xlabel('Time (seconds)')
    plt.ylabel('Throughput (Gbps)')
    plt.title('Validation of Load Shaping Script (Dry Run Results)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    print(f"Saving plot to {OUTPUT_PLOT}")
    plt.savefig(OUTPUT_PLOT)
    print("Done.")

if __name__ == "__main__":
    main()
