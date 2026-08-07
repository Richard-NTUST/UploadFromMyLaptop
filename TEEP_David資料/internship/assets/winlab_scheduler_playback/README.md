# WINLAB Single-UE Scheduler Playback

This offline visualization replays measured scheduler allocations from the July 30, 2026 27-PRB experiment and aligns them with UE throughput and Raritan PDU active power.

## Open

Open `index.html` directly in a browser. The generated data is loaded as a local JavaScript file, so no web server is required.

## Rebuild the data

```bash
python3 scripts/build_winlab_scheduler_playback.py \
  runs/hpe_artifacts/e2e-ocloud-20260730-064034 \
  pdu_data_20260730_063800_070400.csv \
  -o assets/winlab_scheduler_playback/data/run-data.js
```

## Coverage

- Positive iPerf traffic: approximately 1,120 seconds.
- Live scheduler records: approximately the first 130 seconds.
- PDU samples: approximately one sample per minute.

The resource grid stops at the end of scheduler-log coverage. The complete throughput and power timeline remains visible for context.
