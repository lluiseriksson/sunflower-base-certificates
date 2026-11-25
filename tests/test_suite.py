"""Comprehensive pytest + 48 live adversarial red-team attack suite for Paper 14.

Author: Lluis Eriksson
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import (
    CERT_SCHEMA,
    CertificateVerificationError,
    abbott_hanson_sauer_2_uniform,
    count_r_sunflowers,
    hemi_icosahedron_20_family,
    verify_sunflower_certificate_exact,
)

CERTS_DIR = ROOT / "results" / "certificates"


def _load(name: str) -> dict:
    return json.loads((CERTS_DIR / name).read_text(encoding="utf-8"))


def test_all_16_emitted_certificates_verify_cleanly() -> None:
    cert_files = sorted(CERTS_DIR.glob("*.cert.json"))
    assert len(cert_files) == 16
    for path in cert_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        res = verify_sunflower_certificate_exact(data)
        assert res["schema"] == CERT_SCHEMA
        assert "CERTIFIED" in res["verdict"]


def test_extremal_constructions_are_genuinely_sunflower_free() -> None:
    _, e3 = abbott_hanson_sauer_2_uniform(3)
    assert len(e3) == 6 and count_r_sunflowers(e3, 3) == 0
    _, e4 = abbott_hanson_sauer_2_uniform(4)
    assert len(e4) == 10 and count_r_sunflowers(e4, 4) == 0
    _, fam20 = hemi_icosahedron_20_family()
    assert len(fam20) == 20 and count_r_sunflowers(fam20, 3) == 0


def test_48_adversarial_red_team_attacks_rejected() -> None:
    c_sf = _load("sf_r3_k3_hemi_icosa_size20.cert.json")
    c_g5 = _load("graph2_ahs_r5.cert.json")
    c_g6 = _load("graph2_ahs_r6.cert.json")
    c_tow = _load("tower_r3_exact.cert.json")
    c_cr = _load("crossover_r3_B10.cert.json")

    attacks: list[tuple[str, dict]] = []

    def add(name: str, base: dict, mutator) -> None:
        c = copy.deepcopy(base)
        mutator(c)
        attacks.append((name, c))

    # --- Schema & Zero-Float Enforcement (A01-A09) ---
    add("A01_wrong_schema", c_sf, lambda c: c.__setitem__("schema", "FAKE-1.0"))
    add("A02_unknown_mode", c_sf, lambda c: c.__setitem__("mode", "bogus"))
    add("A03_float_lb", c_sf, lambda c: c.__setitem__("base_lower_bound", 2.714))
    add("A04_float_nested_tower", c_tow, lambda c: c["tower"][0].__setitem__("lb", 1.999))
    add("A05_decimal_string", c_sf, lambda c: c.__setitem__("base_lower_bound", "2.714"))
    add("A06_sci_notation", c_sf, lambda c: c.__setitem__("base_lower_bound", "2e0"))
    add("A07_zero_denom", c_sf, lambda c: c.__setitem__("base_lower_bound", "5/0"))
    add("A08_bool_as_int_r", c_sf, lambda c: c.__setitem__("r", True))
    add("A09_trailing_newline_rat", c_sf, lambda c: c.__setitem__("base_lower_bound", "2714/1000\n"))

    # --- Mode 1: Exhaustive Sunflower-Free Family Attacks (A10-A20) ---
    # Inject a 3-sunflower into the 20-set hemi-icosahedron family (replace set 0 with a 3-petal star)
    add("A10_inject_sunflower_disjoint", c_sf, lambda c: c["family"].append([0, 6, 11]) or c.__setitem__("claimed_size", 21))
    add("A11_explicit_3_star_fails", c_sf, lambda c: c.update({"family": [[0, 1, 2], [0, 3, 4], [0, 5, 6]], "claimed_size": 3}))
    add("A12_explicit_3_matching_fails", c_sf, lambda c: c.update({"family": [[0, 1, 2], [3, 4, 5], [6, 7, 8]], "claimed_size": 3}))
    add("A13_duplicate_set", c_sf, lambda c: c["family"].append(c["family"][0]))
    add("A14_unsorted_set", c_sf, lambda c: c["family"].__setitem__(0, [2, 1, 0]))
    add("A15_wrong_set_size", c_sf, lambda c: c["family"].__setitem__(0, [0, 1]))
    add("A16_element_out_of_range", c_sf, lambda c: c["family"].__setitem__(0, [0, 1, 99]))
    add("A17_lie_claimed_size", c_sf, lambda c: c.__setitem__("claimed_size", 25))
    add("A18_inflate_base_lb", c_sf, lambda c: c.__setitem__("base_lower_bound", "2715/1000"))
    add("A19_r_equals_2_invalid", c_sf, lambda c: c.__setitem__("r", 2))
    add("A20_empty_family", c_sf, lambda c: c.__setitem__("family", []))

    # --- Mode 2: Extremal 2-Uniform Graph Attacks (A21-A30) ---
    add("A21_k_not_2", c_g5, lambda c: c.__setitem__("k", 3))
    add("A22_add_edge_creates_5_star", c_g5, lambda c: c["family"].append([0, 5]))
    add("A23_drop_one_edge_suboptimal", c_g5, lambda c: c["family"].pop())
    add("A24_even_r6_add_edge_star", c_g6, lambda c: c["family"].append([0, 10]))
    add("A25_even_r6_drop_edge", c_g6, lambda c: c["family"].pop())
    add("A26_wrong_r_claim", c_g5, lambda c: c.__setitem__("r", 4))
    add("A27_extra_isolated_component_matching", c_g5, lambda c: c.update({"ground_set_size": 12, "family": c["family"][:-1] + [[10, 11]]}))
    add("A28_duplicate_edge", c_g5, lambda c: c["family"].append(c["family"][0]))
    add("A29_self_loop_edge", c_g5, lambda c: c["family"].__setitem__(0, [0, 0]))
    add("A30_negative_vertex", c_g5, lambda c: c["family"].__setitem__(0, [-1, 0]))

    # --- Mode 3: Supermultiplicative Base Tower Attacks (A31-A39) ---
    add("A31_single_level_tower", c_tow, lambda c: c.__setitem__("tower", c["tower"][:1]))
    add("A32_non_increasing_tower", c_tow, lambda c: c["tower"].reverse())
    add("A33_bad_lb_too_high", c_tow, lambda c: c["tower"][1].__setitem__("lb", "2450/1000"))
    add("A34_bad_ub_too_low", c_tow, lambda c: c["tower"][2].__setitem__("ub", "2714/1000"))
    add("A35_ub_le_lb", c_tow, lambda c: c["tower"][1].__setitem__("ub", "2449/1000"))
    add("A36_equal_base_not_strict", c_tow, lambda c: c["tower"].__setitem__(1, {"k": 2, "m": 4, "lb": "1999/1000", "ub": "2001/1000"}))
    add("A37_k_zero_tower", c_tow, lambda c: c["tower"][0].__setitem__("k", 0))
    add("A38_m_zero_tower", c_tow, lambda c: c["tower"][0].__setitem__("m", 0))
    add("A39_r_lt_3_tower", c_tow, lambda c: c.__setitem__("r", 2))

    # --- Mode 4: Erdős-Rado Crossover Attacks (A40-A48) ---
    add("A40_k_star_too_small", c_cr, lambda c: c.__setitem__("k_star", 11))
    add("A41_k_star_too_large", c_cr, lambda c: c.__setitem__("k_star", 13))
    add("A42_B_le_r_minus_1", c_cr, lambda c: c.__setitem__("B", 2))
    add("A43_r_equals_2_cross", c_cr, lambda c: c.__setitem__("r", 2))
    add("A44_k_star_equals_1", c_cr, lambda c: c.__setitem__("k_star", 1))
    add("A45_k_star_dos_cap", c_cr, lambda c: c.__setitem__("k_star", 1000))
    add("A46_wrong_B_for_k12", c_cr, lambda c: c.__setitem__("B", 11))
    add("A47_bool_B", c_cr, lambda c: c.__setitem__("B", True))
    add("A48_non_dict_root", c_cr, lambda c: None)  # replaced below

    # Replace A48 with list root
    attacks[-1] = ("A48_non_dict_root", [])

    # --- Additional Hostile API & Mode-3/Mode-1 Hardening Attacks (A49-A53) ---
    add("A49_tuple_float_smuggling", c_sf, lambda c: c.__setitem__("extra", (1.5,)))
    add("A50_float_dict_key", c_sf, lambda c: c.__setitem__(1.5, "sneaky"))
    add("A51_complex_value", c_sf, lambda c: c.__setitem__("extra", 1 + 2j))
    add("A52_mode3_decreasing_k", c_tow, lambda c: c.__setitem__("tower", [
        {"k": 2, "m": 6, "lb": "2449/1000", "ub": "2450/1000"},
        {"k": 1, "m": 3, "lb": "2999/1000", "ub": "3001/1000"},
    ]))
    add("A53_mode1_k_dos_cap", c_sf, lambda c: c.update({"ground_set_size": 100, "k": 65}))

    assert len(attacks) == 53
    for name, bad_cert in attacks:
        with pytest.raises(CertificateVerificationError, match="."):
            verify_sunflower_certificate_exact(bad_cert)
