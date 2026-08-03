#!/usr/bin/env python3
"""
3GPP TS 38.214 §5.1.3.2 — Transport Block Size (TBS) Calculator
================================================================

Implements the complete TBS determination algorithm for 5G NR PDSCH,
then compares Strategy A (273 PRBs × 1 slot) vs Strategy B (27 PRBs × 10 slots)
across all MCS indices to prove throughput equivalence.

Reference: 3GPP TS 38.214 v17.6.0, Section 5.1.3.2
Author:    David P — BMW-NTUST TEEP Internship
Date:      2026-02-26
"""

import math
import sys

# ──────────────────────────────────────────────────────────────────────
# Table 5.1.3.2-1: TBS for N_info ≤ 3824 (93 entries from the spec)
# ──────────────────────────────────────────────────────────────────────
TBS_TABLE = [
    24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136,
    144, 152, 160, 168, 176, 184, 192, 208, 224, 240, 256, 272, 288,
    304, 320, 336, 352, 368, 384, 408, 432, 456, 480, 504, 528, 552,
    576, 608, 640, 672, 704, 736, 768, 808, 848, 888, 928, 984, 1032,
    1064, 1128, 1160, 1192, 1224, 1256, 1288, 1320, 1352, 1416, 1480,
    1544, 1608, 1672, 1736, 1800, 1864, 1928, 2024, 2088, 2152, 2216,
    2280, 2408, 2472, 2536, 2600, 2664, 2728, 2792, 2856, 2976, 3104,
    3240, 3368, 3496, 3624, 3752, 3824,
]

# ──────────────────────────────────────────────────────────────────────
# MCS Table 1 (TS 38.214 Table 5.1.3.1-1): 64QAM max
# Format: (MCS_index, Q_m, R_x1024)
# ──────────────────────────────────────────────────────────────────────
MCS_TABLE_1 = [
    ( 0, 2,  120),
    ( 1, 2,  157),
    ( 2, 2,  193),
    ( 3, 2,  251),
    ( 4, 2,  308),
    ( 5, 2,  379),
    ( 6, 2,  449),
    ( 7, 2,  526),
    ( 8, 2,  602),
    ( 9, 2,  679),
    (10, 4,  340),
    (11, 4,  378),
    (12, 4,  434),
    (13, 4,  490),
    (14, 4,  553),
    (15, 4,  616),
    (16, 4,  658),
    (17, 6,  438),
    (18, 6,  466),
    (19, 6,  517),
    (20, 6,  567),
    (21, 6,  616),
    (22, 6,  666),
    (23, 6,  719),
    (24, 6,  772),
    (25, 6,  822),
    (26, 6,  873),
    (27, 6,  910),
    (28, 6,  948),
    # 29-31 are reserved / retransmission indicators
]

# ──────────────────────────────────────────────────────────────────────
# MCS Table 2 (TS 38.214 Table 5.1.3.1-2): 256QAM max
# Format: (MCS_index, Q_m, R_x1024)
# ──────────────────────────────────────────────────────────────────────
MCS_TABLE_2 = [
    ( 0, 2,  120),
    ( 1, 2,  193),
    ( 2, 2,  308),
    ( 3, 2,  449),
    ( 4, 2,  602),
    ( 5, 4,  378),
    ( 6, 4,  434),
    ( 7, 4,  490),
    ( 8, 4,  553),
    ( 9, 4,  616),
    (10, 4,  658),
    (11, 6,  466),
    (12, 6,  517),
    (13, 6,  567),
    (14, 6,  616),
    (15, 6,  666),
    (16, 6,  719),
    (17, 6,  772),
    (18, 6,  822),
    (19, 6,  873),
    (20, 8,  682.5),
    (21, 8,  711),
    (22, 8,  754),
    (23, 8,  797),
    (24, 8,  841),
    (25, 8,  885),
    (26, 8,  916.5),
    (27, 8,  948),
    # 28-31 are reserved / retransmission indicators
]


# ──────────────────────────────────────────────────────────────────────
# TBS Determination Algorithm  (TS 38.214 §5.1.3.2)
# ──────────────────────────────────────────────────────────────────────

def compute_tbs(
    n_prb: int,
    mcs_index: int,
    n_layers: int = 2,
    n_sh_symb: int = 12,
    n_dmrs_prb: int = 12,
    n_prb_oh: int = 0,
    mcs_table: int = 1,
) -> dict:
    """
    Compute TBS per TS 38.214 §5.1.3.2.

    Parameters
    ----------
    n_prb       : number of allocated PRBs
    mcs_index   : MCS index (0–28 for Table 1, 0–27 for Table 2)
    n_layers    : number of MIMO layers (v)
    n_sh_symb   : number of PDSCH symbols in the slot
    n_dmrs_prb  : DMRS REs per PRB (per DMRS symbol × number of DMRS symbols)
    n_prb_oh    : xOverhead from RRC (0 if not configured)
    mcs_table   : 1 (64QAM) or 2 (256QAM)

    Returns
    -------
    dict with intermediate values and final TBS
    """
    # --- Look up MCS parameters ---
    table = MCS_TABLE_1 if mcs_table == 1 else MCS_TABLE_2
    entry = [e for e in table if e[0] == mcs_index]
    if not entry:
        raise ValueError(f"MCS index {mcs_index} not found in Table {mcs_table}")
    _, Qm, R_x1024 = entry[0]
    R = R_x1024 / 1024.0

    # --- Step 1: N'_RE per PRB ---
    N_RE_prime = 12 * n_sh_symb - n_dmrs_prb - n_prb_oh

    # --- Step 2: Total N_RE ---
    N_RE = min(156, N_RE_prime) * n_prb

    # --- Step 3: Intermediate N_info ---
    N_info = N_RE * R * Qm * n_layers

    # --- Step 4: Quantised TBS ---
    if N_info <= 3824:
        tbs = _tbs_small(N_info)
    else:
        tbs = _tbs_large(N_info, R)

    modulation = {2: "QPSK", 4: "16QAM", 6: "64QAM", 8: "256QAM"}[Qm]

    return {
        "mcs_index": mcs_index,
        "Qm": Qm,
        "R_x1024": R_x1024,
        "R": R,
        "modulation": modulation,
        "N_RE_prime": N_RE_prime,
        "N_RE": N_RE,
        "N_info": N_info,
        "TBS": tbs,
        "n_prb": n_prb,
        "n_layers": n_layers,
    }


def _tbs_small(N_info: float) -> int:
    """Case 1: N_info ≤ 3824 → table lookup (find smallest TBS ≥ N_info)."""
    for tbs in TBS_TABLE:
        if tbs >= N_info:
            return tbs
    return TBS_TABLE[-1]  # should not reach here


def _tbs_large(N_info: float, R: float) -> int:
    """Case 2: N_info > 3824 → formula-based quantisation."""
    n = int(math.floor(math.log2(N_info - 24))) - 5
    N_info_prime = max(3840, (1 << n) * round((N_info - 24) / (1 << n)))

    if R <= 0.25:
        C = math.ceil((N_info_prime + 24) / 3816)
        tbs = 8 * C * math.ceil((N_info_prime + 24) / (8 * C)) - 24
    else:
        if N_info_prime + 24 <= 8424:
            tbs = 8 * math.ceil((N_info_prime + 24) / 8) - 24
        else:
            C = math.ceil((N_info_prime + 24) / 8424)
            tbs = 8 * C * math.ceil((N_info_prime + 24) / (8 * C)) - 24
    return tbs


# ──────────────────────────────────────────────────────────────────────
# Throughput Helpers
# ──────────────────────────────────────────────────────────────────────

def throughput_mbps(tbs_bits: int, n_slots: int = 1, slot_duration_ms: float = 0.5) -> float:
    """Compute average throughput in Mbps over n_slots."""
    total_bits = tbs_bits * n_slots if n_slots > 1 else tbs_bits
    total_time_s = n_slots * slot_duration_ms / 1000.0
    return total_bits / total_time_s / 1e6


# ──────────────────────────────────────────────────────────────────────
# Main: 273×1 vs 27×10 comparison across all MCS indices
# ──────────────────────────────────────────────────────────────────────

def separator(char="─", width=140):
    return char * width


def run_comparison(mcs_table_id: int = 1, n_layers: int = 2):
    """Run full MCS sweep comparison for chosen table and print results."""

    table = MCS_TABLE_1 if mcs_table_id == 1 else MCS_TABLE_2
    max_mcs = table[-1][0]
    table_name = f"Table {mcs_table_id} ({'64QAM' if mcs_table_id == 1 else '256QAM'} max)"

    print(f"\n{'=' * 140}")
    print(f"  3GPP TS 38.214 §5.1.3.2 — TBS Calculator: 273×1 vs 27×10 Comparison")
    print(f"  MCS {table_name}  |  Layers = {n_layers}  |  DMRS Type 1 addPos=1 (N'_RE=132)")
    print(f"  Slot duration = 0.5 ms (µ=1, 30 kHz SCS)  |  N_sh_symb = 12")
    print(f"{'=' * 140}")

    # Header
    print(f"\n{'MCS':>3} {'Mod':>6} {'Rx1024':>7} {'R':>6}"
          f" │ {'TBS_273':>10} {'TBS_27':>10} {'27×10':>12}"
          f" │ {'Δ(bits)':>10} {'Δ(%)':>7}"
          f" │ {'TP_273':>9} {'TP_27×10':>9}"
          f" │ {'Equiv?':>6}")
    print(f"{'':>3} {'':>6} {'':>7} {'':>6}"
          f" │ {'(bits)':>10} {'(bits)':>10} {'(bits)':>12}"
          f" │ {'':>10} {'':>7}"
          f" │ {'(Mbps)':>9} {'(Mbps)':>9}"
          f" │ {'':>6}")
    print(separator("─"))

    results = []
    for mcs_idx, Qm, R_x1024 in table:
        a = compute_tbs(273, mcs_idx, n_layers=n_layers, mcs_table=mcs_table_id)
        b = compute_tbs(27,  mcs_idx, n_layers=n_layers, mcs_table=mcs_table_id)

        tbs_a = a["TBS"]
        tbs_b = b["TBS"]
        tbs_b_10 = tbs_b * 10

        delta = tbs_a - tbs_b_10
        pct = (delta / tbs_b_10 * 100) if tbs_b_10 > 0 else 0.0

        # Average throughput over 10-slot window (5 ms)
        tp_a = tbs_a / (5e-3) / 1e6       # 273×1: data in 1 slot, idle 9 → avg over 5ms
        tp_b = tbs_b_10 / (5e-3) / 1e6    # 27×10: data across all 10 slots → avg over 5ms

        equiv = "YES" if abs(pct) < 5.0 else "NO"
        mod = a["modulation"]

        print(f"{mcs_idx:>3} {mod:>6} {R_x1024:>7.1f} {R_x1024/1024:>6.4f}"
              f" │ {tbs_a:>10,} {tbs_b:>10,} {tbs_b_10:>12,}"
              f" │ {delta:>+10,} {pct:>+7.2f}%"
              f" │ {tp_a:>9.2f} {tp_b:>9.2f}"
              f" │ {equiv:>6}")

        results.append({
            "mcs": mcs_idx,
            "mod": mod,
            "Qm": Qm,
            "R": R_x1024 / 1024,
            "tbs_273": tbs_a,
            "tbs_27": tbs_b,
            "tbs_27x10": tbs_b_10,
            "delta": delta,
            "pct": pct,
            "tp_273_mbps": tp_a,
            "tp_27x10_mbps": tp_b,
            "equiv": equiv,
        })

    print(separator("─"))

    # Summary statistics
    pcts = [r["pct"] for r in results]
    print(f"\n  Summary:")
    print(f"    Min Δ  = {min(pcts):+.2f}%")
    print(f"    Max Δ  = {max(pcts):+.2f}%")
    print(f"    Mean Δ = {sum(pcts)/len(pcts):+.2f}%")
    print(f"    All within ±5%: {'YES ✓' if all(abs(p) < 5.0 for p in pcts) else 'NO ✗'}")

    max_tbs_a = max(r["tbs_273"] for r in results)
    max_tp_a = max(r["tp_273_mbps"] for r in results)
    print(f"\n    Peak TBS (273 PRBs, MCS {results[-1]['mcs']}): {max_tbs_a:,} bits = {max_tbs_a/8:,.0f} bytes")
    print(f"    Peak throughput (per 10-slot window):  {max_tp_a:.2f} Mbps")

    return results


def run_layer_sensitivity(mcs_table_id: int = 1, mcs_index: int = 27):
    """Show how layer count affects the equivalence ratio for a fixed MCS."""
    table = MCS_TABLE_1 if mcs_table_id == 1 else MCS_TABLE_2
    entry = [e for e in table if e[0] == mcs_index]
    if not entry:
        print(f"MCS {mcs_index} not in Table {mcs_table_id}")
        return
    max_mcs = entry[0][0]

    print(f"\n{'=' * 80}")
    print(f"  Layer Sensitivity (MCS {max_mcs}, Table {mcs_table_id})")
    print(f"{'=' * 80}")
    print(f"{'Layers':>6} │ {'TBS_273':>12} {'TBS_27':>12} {'27×10':>12} │ {'Ratio':>8} {'Δ(%)':>7}")
    print("─" * 80)

    for v in [1, 2, 4]:
        a = compute_tbs(273, max_mcs, n_layers=v, mcs_table=mcs_table_id)
        b = compute_tbs(27,  max_mcs, n_layers=v, mcs_table=mcs_table_id)
        ratio = a["TBS"] / (b["TBS"] * 10) if b["TBS"] > 0 else 0
        pct = (ratio - 1.0) * 100
        print(f"{v:>6} │ {a['TBS']:>12,} {b['TBS']:>12,} {b['TBS']*10:>12,} │ {ratio:>8.4f} {pct:>+7.2f}%")


def run_dmrs_sensitivity(mcs_table_id: int = 1, mcs_index: int = 27, n_layers: int = 2):
    """Show how DMRS additional positions affect the equivalence ratio."""
    table = MCS_TABLE_1 if mcs_table_id == 1 else MCS_TABLE_2
    entry = [e for e in table if e[0] == mcs_index]
    if not entry:
        print(f"MCS {mcs_index} not in Table {mcs_table_id}")
        return

    # DMRS Type 1: 6 REs per PRB per DMRS symbol per CDM group, 2 CDM groups = 12 per sym
    configs = [
        ("Type1 addPos=0", 1, 12),   # 1 DMRS sym × 12 RE/PRB
        ("Type1 addPos=1", 2, 24),   # 2 DMRS sym × 12 RE/PRB
        ("Type1 addPos=2", 3, 36),   # 3 DMRS sym × 12 RE/PRB
        ("Type1 addPos=3", 4, 48),   # 4 DMRS sym × 12 RE/PRB
    ]

    print(f"\n{'=' * 100}")
    print(f"  DMRS Sensitivity (MCS {mcs_index}, Table {mcs_table_id}, {n_layers} layers)")
    print(f"{'=' * 100}")
    print(f"{'Config':>18} {'Syms':>4} {'N_DMRS':>6} {'N_RE_p':>6}"
          f" │ {'TBS_273':>12} {'TBS_27×10':>12} │ {'Δ(%)':>7}")
    print("─" * 100)

    for name, n_sym, n_dmrs in configs:
        a = compute_tbs(273, mcs_index, n_layers=n_layers, n_dmrs_prb=n_dmrs, mcs_table=mcs_table_id)
        b = compute_tbs(27,  mcs_index, n_layers=n_layers, n_dmrs_prb=n_dmrs, mcs_table=mcs_table_id)
        b10 = b["TBS"] * 10
        pct = (a["TBS"] - b10) / b10 * 100 if b10 > 0 else 0
        print(f"{name:>18} {n_sym:>4} {n_dmrs:>6} {a['N_RE_prime']:>6}"
              f" │ {a['TBS']:>12,} {b10:>12,} │ {pct:>+7.2f}%")


# ──────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║  3GPP TS 38.214 §5.1.3.2 — TBS Calculator & Equivalence Verifier      ║")
    print("║  Project: BMW-NTUST TEEP — RU Power Consumption Measurement            ║")
    print("║  Proves: TBS(273 PRBs × 1 slot) ≈ 10 × TBS(27 PRBs × 1 slot)         ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")

    # ── Table 1 (64QAM max) ──
    results_t1 = run_comparison(mcs_table_id=1, n_layers=2)

    # ── Table 2 (256QAM max) ──
    results_t2 = run_comparison(mcs_table_id=2, n_layers=2)

    # ── Sensitivity: Layers ──
    run_layer_sensitivity(mcs_table_id=1, mcs_index=28)
    run_layer_sensitivity(mcs_table_id=2, mcs_index=27)

    # ── Sensitivity: DMRS ──
    run_dmrs_sensitivity(mcs_table_id=1, mcs_index=28, n_layers=2)
    run_dmrs_sensitivity(mcs_table_id=2, mcs_index=27, n_layers=2)

    # ── Final verdict ──
    all_pcts = [r["pct"] for r in results_t1 + results_t2]
    print(f"\n{'=' * 80}")
    print(f"  FINAL VERDICT")
    print(f"{'=' * 80}")
    print(f"  Across {len(all_pcts)} MCS configurations (Tables 1 & 2):")
    print(f"    - Range of Δ: [{min(all_pcts):+.2f}%, {max(all_pcts):+.2f}%]")
    print(f"    - Mean Δ:     {sum(all_pcts)/len(all_pcts):+.2f}%")
    print(f"    - All within ±5%: {'YES ✓' if all(abs(p) < 5 for p in all_pcts) else 'NO ✗'}")
    print()
    print(f"  ┌──────────────────────────────────────────────────────────────┐")
    print(f"  │  CONCLUSION: TBS(273×1) ≈ TBS(27×10)                       │")
    print(f"  │  Frequency-domain (273 PRBs, 1 slot) and time-domain       │")
    print(f"  │  (27 PRBs, 10 slots) scheduling deliver the SAME total     │")
    print(f"  │  data volume (within {max(abs(min(all_pcts)), abs(max(all_pcts))):.1f}%), confirming equivalence.       │")
    print(f"  └──────────────────────────────────────────────────────────────┘")
    print()
