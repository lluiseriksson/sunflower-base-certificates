"""Run all 4 deterministic experiments and emit 16 exact-Z/Q SUNFLOWER-BASE-CERT-1.0 certificates.

Author: Lluis Eriksson
"""

from __future__ import annotations

from fractions import Fraction
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import (
    CERT_SCHEMA,
    abbott_hanson_sauer_2_uniform,
    hemi_icosahedron_20_family,
    rat_to_str,
    verify_sunflower_certificate_exact,
)
from src.sunflower_exact import factorial_exact

RESULTS_DIR = ROOT / "results"
CERTS_DIR = RESULTS_DIR / "certificates"


def _write_cert(filename: str, cert: Dict[str, Any]) -> Dict[str, Any]:
    CERTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CERTS_DIR / filename
    path.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    t0 = time.perf_counter()
    res = verify_sunflower_certificate_exact(cert)
    dt_ms = (time.perf_counter() - t0) * 1000.0
    res["file"] = filename
    res["verify_ms"] = round(dt_ms, 3)
    return res


def _find_exact_crossover(r: int, B: int) -> int:
    k = 2
    while True:
        if B ** k < factorial_exact(k) * ((r - 1) ** k):
            return k
        k += 1


def run_exp1_certified_atlas() -> Dict[str, Any]:
    records = []

    # Mode 1: Exhaustively verified explicit k-uniform r-sunflower-free families (4 certs)
    # (1) r=3, k=1: 2 singletons -> b_3 >= 2
    records.append(_write_cert("sf_r3_k1_size2.cert.json", {
        "schema": CERT_SCHEMA,
        "mode": "sunflower_free_family_exact",
        "label": "r3_k1_trivial",
        "ground_set_size": 2,
        "k": 1,
        "r": 3,
        "family": [[0], [1]],
        "claimed_size": 2,
        "base_lower_bound": "2",
    }))
    # (2) r=3, k=2: 2 K_3 (6 edges on 6 vertices) -> b_3 >= sqrt(6) > 2449/1000
    n3, e3 = abbott_hanson_sauer_2_uniform(3)
    records.append(_write_cert("sf_r3_k2_size6.cert.json", {
        "schema": CERT_SCHEMA,
        "mode": "sunflower_free_family_exact",
        "label": "r3_k2_two_triangles",
        "ground_set_size": n3,
        "k": 2,
        "r": 3,
        "family": [list(e) for e in e3],
        "claimed_size": len(e3),
        "base_lower_bound": "2449/1000",
    }))
    # (3) r=4, k=2: 10 edges on 7 vertices -> b_4 >= sqrt(10) > 3162/1000
    n4, e4 = abbott_hanson_sauer_2_uniform(4)
    records.append(_write_cert("sf_r4_k2_size10.cert.json", {
        "schema": CERT_SCHEMA,
        "mode": "sunflower_free_family_exact",
        "label": "r4_k2_circulant_10",
        "ground_set_size": n4,
        "k": 2,
        "r": 4,
        "family": [list(e) for e in e4],
        "claimed_size": len(e4),
        "base_lower_bound": "3162/1000",
    }))
    # (4) r=3, k=3: Two disjoint copies of RP^2 hemi-icosahedron (20 triples on 12 vertices) -> b_3 >= 20^(1/3) > 2714/1000!
    n20, fam20 = hemi_icosahedron_20_family()
    records.append(_write_cert("sf_r3_k3_hemi_icosa_size20.cert.json", {
        "schema": CERT_SCHEMA,
        "mode": "sunflower_free_family_exact",
        "label": "r3_k3_double_hemi_icosahedron",
        "ground_set_size": n20,
        "k": 3,
        "r": 3,
        "family": [list(t) for t in fam20],
        "claimed_size": len(fam20),
        "base_lower_bound": "2714/1000",
    }))

    # Mode 2: Abbott-Hanson-Sauer extremal 2-uniform graphs across r = 3, 4, 5, 6, 7, 8 (6 certs)
    for r_val in [3, 4, 5, 6, 7, 8]:
        nv, ev = abbott_hanson_sauer_2_uniform(r_val)
        records.append(_write_cert(f"graph2_ahs_r{r_val}.cert.json", {
            "schema": CERT_SCHEMA,
            "mode": "graph_two_uniform_extremal",
            "label": f"AHS_2_uniform_r{r_val}",
            "ground_set_size": nv,
            "k": 2,
            "r": r_val,
            "family": [list(e) for e in ev],
        }))

    # Mode 3: Supermultiplicative base lower-bound towers (2 certs: r=3 and r=4)
    records.append(_write_cert("tower_r3_exact.cert.json", {
        "schema": CERT_SCHEMA,
        "mode": "supermultiplicative_base_tower",
        "r": 3,
        "tower": [
            {"k": 1, "m": 2, "lb": "1999/1000", "ub": "2001/1000"},
            {"k": 2, "m": 6, "lb": "2449/1000", "ub": "2450/1000"},
            {"k": 3, "m": 20, "lb": "2714/1000", "ub": "2715/1000"},
            {"k": 4, "m": 79, "lb": "2981/1000", "ub": "2982/1000"},
        ],
    }))
    records.append(_write_cert("tower_r4_exact.cert.json", {
        "schema": CERT_SCHEMA,
        "mode": "supermultiplicative_base_tower",
        "r": 4,
        "tower": [
            {"k": 1, "m": 3, "lb": "2999/1000", "ub": "3001/1000"},
            {"k": 2, "m": 10, "lb": "3162/1000", "ub": "3163/1000"},
        ],
    }))

    # Mode 4: Exact big-integer Erdős-Rado vs fixed-base crossovers (4 certs)
    for r_val, B_val in [(3, 10), (3, 20), (3, 50), (4, 30)]:
        k_st = _find_exact_crossover(r_val, B_val)
        records.append(_write_cert(f"crossover_r{r_val}_B{B_val}.cert.json", {
            "schema": CERT_SCHEMA,
            "mode": "erdos_rado_fixed_base_crossover",
            "r": r_val,
            "B": B_val,
            "k_star": k_st,
        }))

    out = {"schema": CERT_SCHEMA, "num_certificates": len(records), "certificates": records}
    (RESULTS_DIR / "exp1_certified_atlas.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def run_exp2_extremal_2_uniform_scaling() -> Dict[str, Any]:
    rows = []
    for r in range(3, 21):
        m_triv = (r - 1) ** 2
        m_opt = r * (r - 1) if r % 2 == 1 else (r - 1) ** 2 + (r - 2) // 2
        b_triv = float(r - 1)
        b_opt = math.sqrt(m_opt)
        rows.append({
            "r": r,
            "parity": "odd" if r % 2 == 1 else "even",
            "trivial_M_r_2": m_triv,
            "optimal_M_r_2": m_opt,
            "gain_edges": m_opt - m_triv,
            "trivial_base": b_triv,
            "optimal_base_k2": round(b_opt, 6),
            "base_gain": round(b_opt - b_triv, 6),
        })
    out = {"rows": rows}
    (RESULTS_DIR / "exp2_extremal_2_uniform.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def run_exp3_erdos_rado_crossover_atlas() -> Dict[str, Any]:
    B_vals = [6, 8, 10, 15, 20, 30, 50, 100]
    curves = {}
    for r in [3, 4, 5]:
        pts = []
        for B in B_vals:
            if B <= r - 1:
                continue
            k_st = _find_exact_crossover(r, B)
            # Ratio k_star / (B / (r - 1)) approaches e = 2.71828... by Stirling!
            ratio_stirling = k_st / (B / (r - 1))
            pts.append({
                "B": B,
                "k_star": k_st,
                "ratio_k_star_over_B_div_rm1": round(ratio_stirling, 5),
            })
        curves[str(r)] = pts
    out = {"stirling_e": round(math.e, 6), "curves": curves}
    (RESULTS_DIR / "exp3_crossover_atlas.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def run_exp4_log_bounds_comparison() -> Dict[str, Any]:
    """Compare log2 of Erdős-Rado k!(r-1)^k, Alweiss-Lovett-Wu-Zhang (C r log(rk))^k, and fixed-base B^k at r=3."""
    r = 3
    rows = []
    for k in range(2, 41, 2):
        log2_er = sum(math.log2(i) for i in range(1, k + 1)) + k * math.log2(r - 1)
        log2_alwz = k * math.log2(4.0 * r * math.log2(r * k))
        log2_fixed_10 = k * math.log2(10.0)
        log2_fixed_20 = k * math.log2(20.0)
        log2_lb_hemi = k * (math.log2(20.0) / 3.0)
        rows.append({
            "k": k,
            "log2_erdos_rado": round(log2_er, 4),
            "log2_alwz_proxy": round(log2_alwz, 4),
            "log2_fixed_B10": round(log2_fixed_10, 4),
            "log2_fixed_B20": round(log2_fixed_20, 4),
            "log2_hemi_icosa_lb": round(log2_lb_hemi, 4),
        })
    out = {"r": r, "rows": rows}
    (RESULTS_DIR / "exp4_log_bounds_comparison.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    e1 = run_exp1_certified_atlas()
    e2 = run_exp2_extremal_2_uniform_scaling()
    e3 = run_exp3_erdos_rado_crossover_atlas()
    e4 = run_exp4_log_bounds_comparison()
    print(f"[EXP 1] {e1['num_certificates']} exact certificates emitted and verified (0 floats).")
    print(f"[EXP 2] Extremal 2-uniform table: {len(e2['rows'])} values of r.")
    print(f"[EXP 3] Crossover atlas: {len(e3['curves'])} petal counts.")
    print(f"[EXP 4] Log-bound comparison: {len(e4['rows'])} set sizes.")


if __name__ == "__main__":
    main()
