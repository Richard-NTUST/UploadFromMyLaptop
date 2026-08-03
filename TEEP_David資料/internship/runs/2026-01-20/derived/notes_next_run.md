# Next Run Improvement Decision

**Decision:** Add Load-L and Load-H points (3x repeats each) to the next run matrix.

**Reasoning:**
- The pilot run proved we can measure stable power states for `Idle` and `Load-M` (Max).
- To fully characterize the RU platform power, we need to sweep the load (Low/Medium/High) to see if the power consumption scales linearly or follows a different curve.
- Repeating 3x helps filter out noise and confirms steady-state stability.

**Plan for Week 3 Run:**
1.  **Load-L:** ~30% throughput target (via iperf bandwidth limit).
2.  **Load-M:** ~60% throughput target.
3.  **Load-H:** Max throughput (unlimited).
4.  **Structure:** `Idle -> Warmup -> [Load-L -> Idle -> Load-M -> Idle -> Load-H -> Idle] x 3`.
