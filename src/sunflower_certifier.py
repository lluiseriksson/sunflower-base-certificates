"""Pure-stdlib zero-floating-point-trust certificate verifier (SUNFLOWER-BASE-CERT-1.0).

Supports 4 mutually exclusive modes over exact integers Z and rationals Q:
  1. sunflower_free_family_exact     : Exhaustively verifies 0 r-sunflowers in an explicit k-uniform family.
  2. graph_two_uniform_extremal      : Verifies odd/even Abbott-Hanson-Sauer 2-uniform graphs (Delta & nu <= r-1).
  3. supermultiplicative_base_tower  : Verifies exact integer-power rational brackets p^k < m q^k for b_r.
  4. erdos_rado_fixed_base_crossover : Verifies exact big-integer crossover B^k < k! (r-1)^k.

Author: Lluis Eriksson
"""

from __future__ import annotations

from fractions import Fraction
import re
from typing import Any, Dict, List, Set, Tuple

from .sunflower_exact import count_r_sunflowers, factorial_exact, rat_to_str

CERT_SCHEMA = "SUNFLOWER-BASE-CERT-1.0"
VALID_MODES = {
    "sunflower_free_family_exact",
    "graph_two_uniform_extremal",
    "supermultiplicative_base_tower",
    "erdos_rado_fixed_base_crossover",
}

_RAT_RE = re.compile(r"\A-?[0-9]+(?:/[1-9][0-9]*)?\Z")


class CertificateVerificationError(ValueError):
    """Raised whenever an exact sunflower certificate fails any mathematical or schema check."""


def _assert_no_floats(obj: Any, path: str = "root") -> None:
    if isinstance(obj, (float, complex)):
        raise CertificateVerificationError(f"Floating-point or complex value forbidden at {path}: {obj!r}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _assert_no_floats(k, f"{path}.<key>")
            _assert_no_floats(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for i, v in enumerate(obj):
            _assert_no_floats(v, f"{path}[{i}]")


def _parse_int(val: Any, name: str) -> int:
    if isinstance(val, bool) or not isinstance(val, int):
        raise CertificateVerificationError(f"{name} must be an exact int.")
    return val


def _parse_rat(val: Any, name: str) -> Fraction:
    if isinstance(val, bool):
        raise CertificateVerificationError(f"{name} cannot be bool.")
    if isinstance(val, int):
        return Fraction(val)
    if isinstance(val, str):
        if not _RAT_RE.match(val):
            raise CertificateVerificationError(f"{name} is not a canonical rational string: {val!r}")
        if "/" in val:
            num_s, den_s = val.split("/")
            return Fraction(int(num_s), int(den_s))
        return Fraction(int(val))
    raise CertificateVerificationError(f"{name} must be exact int or rational string.")


def _parse_uniform_family(cert: Dict[str, Any]) -> Tuple[int, int, int, List[Tuple[int, ...]]]:
    n = _parse_int(cert.get("ground_set_size"), "ground_set_size")
    k = _parse_int(cert.get("k"), "k")
    r = _parse_int(cert.get("r"), "r")
    if n < 1 or k < 1 or k > 64 or r < 3 or k > n:
        raise CertificateVerificationError("Require ground_set_size >= k >= 1 (k <= 64) and r >= 3.")
    raw_fam = cert.get("family")
    if not isinstance(raw_fam, list) or not raw_fam:
        raise CertificateVerificationError("family must be a non-empty list of k-element sets.")
    family: List[Tuple[int, ...]] = []
    for idx, s in enumerate(raw_fam):
        if not isinstance(s, list) or len(s) != k:
            raise CertificateVerificationError(f"family[{idx}] must be a list of length {k}.")
        elems = tuple(_parse_int(e, f"family[{idx}]") for e in s)
        if tuple(sorted(elems)) != elems or len(set(elems)) != k:
            raise CertificateVerificationError(f"family[{idx}] must be strictly increasing distinct elements.")
        if any(e < 0 or e >= n for e in elems):
            raise CertificateVerificationError(f"family[{idx}] element out of range [0, {n}).")
        family.append(elems)
    if len(set(family)) != len(family):
        raise CertificateVerificationError("Duplicate sets in family are forbidden.")
    return n, k, r, family


def _verify_mode1_sunflower_free(cert: Dict[str, Any]) -> Dict[str, Any]:
    n, k, r, family = _parse_uniform_family(cert)
    if len(family) > 40 and r >= 3:
        raise CertificateVerificationError("Family size > 40 exceeds exhaustive O(m^r) verification cap.")
    sf_count = count_r_sunflowers(family, r)
    if sf_count != 0:
        raise CertificateVerificationError(f"Family is NOT {r}-sunflower-free: found {sf_count} sunflowers.")
    m = len(family)
    if "claimed_size" in cert and _parse_int(cert.get("claimed_size"), "claimed_size") != m:
        raise CertificateVerificationError("claimed_size mismatch.")

    base_lb = None
    if "base_lower_bound" in cert and cert["base_lower_bound"] is not None:
        lb = _parse_rat(cert.get("base_lower_bound"), "base_lower_bound")
        if lb <= 0:
            raise CertificateVerificationError("base_lower_bound must be positive.")
        if lb.numerator ** k > m * (lb.denominator ** k):
            raise CertificateVerificationError(f"Claimed base_lower_bound {lb} violates {lb}^{k} <= {m}.")
        base_lb = rat_to_str(lb)

    return {
        "schema": CERT_SCHEMA,
        "mode": "sunflower_free_family_exact",
        "verdict": "SUNFLOWER_FREE_CERTIFIED",
        "ground_set_size": n,
        "k": k,
        "r": r,
        "family_size": m,
        "sunflowers_found": 0,
        "base_lower_bound": base_lb,
    }


def _max_matching_upper_via_components(n: int, edges: List[Tuple[int, int]]) -> int:
    """Exact upper bound on matching number nu(G) via sum_{comp C} floor(|C|/2)."""
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    visited = [False] * n
    nu_upper = 0
    for i in range(n):
        if visited[i] or not adj[i]:
            continue
        stack = [i]
        visited[i] = True
        comp_sz = 0
        while stack:
            cur = stack.pop()
            comp_sz += 1
            for nxt in adj[cur]:
                if not visited[nxt]:
                    visited[nxt] = True
                    stack.append(nxt)
        nu_upper += comp_sz // 2
    return nu_upper


def _verify_mode2_graph_two_uniform(cert: Dict[str, Any]) -> Dict[str, Any]:
    n, k, r, edges_raw = _parse_uniform_family(cert)
    if k != 2:
        raise CertificateVerificationError("graph_two_uniform_extremal requires k == 2.")
    edges = [(e[0], e[1]) for e in edges_raw]
    # 1. Verify max degree <= r - 1 (no r-star, i.e., no r-sunflower with core size 1)
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    max_deg = max(deg) if deg else 0
    if max_deg >= r:
        raise CertificateVerificationError(f"Graph contains an {r}-star (max degree {max_deg} >= {r}).")
    # 2. Verify matching number <= r - 1 via exact component parity bound sum floor(|C|/2) <= r - 1
    nu_upper = _max_matching_upper_via_components(n, edges)
    if nu_upper >= r:
        raise CertificateVerificationError(f"Component matching bound {nu_upper} >= {r} fails to exclude {r}-matching.")

    m = len(edges)
    expected_opt = r * (r - 1) if r % 2 == 1 else (r - 1) * (r - 1) + (r - 2) // 2
    if m != expected_opt:
        raise CertificateVerificationError(f"Edge count {m} does not match Abbott-Hanson-Sauer optimum {expected_opt}.")
    if m <= (r - 1) * (r - 1):
        raise CertificateVerificationError("Graph does not beat trivial block bound (r - 1)^2.")

    return {
        "schema": CERT_SCHEMA,
        "mode": "graph_two_uniform_extremal",
        "verdict": "EXTREMAL_2_UNIFORM_CERTIFIED",
        "r": r,
        "ground_set_size": n,
        "num_edges": m,
        "max_degree": max_deg,
        "matching_upper_bound": nu_upper,
        "beats_trivial_block": True,
    }


def _verify_mode3_base_tower(cert: Dict[str, Any]) -> Dict[str, Any]:
    r = _parse_int(cert.get("r"), "r")
    if r < 3:
        raise CertificateVerificationError("Require r >= 3.")
    raw_steps = cert.get("tower")
    if not isinstance(raw_steps, list) or len(raw_steps) < 2:
        raise CertificateVerificationError("tower must be a list of at least 2 entries.")

    prev_k = None
    prev_m = None
    verified_steps = []
    for idx, st in enumerate(raw_steps):
        if not isinstance(st, dict):
            raise CertificateVerificationError(f"tower[{idx}] must be a dict.")
        k = _parse_int(st.get("k"), f"tower[{idx}].k")
        m = _parse_int(st.get("m"), f"tower[{idx}].m")
        lb = _parse_rat(st.get("lb"), f"tower[{idx}].lb")
        ub = _parse_rat(st.get("ub"), f"tower[{idx}].ub")
        if k < 1 or k > 64 or m < 1 or lb <= 0 or ub <= lb:
            raise CertificateVerificationError(f"Invalid parameters at tower[{idx}].")
        # Verify lb^k < m < ub^k strictly in exact integer arithmetic
        if not (lb.numerator ** k < m * (lb.denominator ** k)):
            raise CertificateVerificationError(f"tower[{idx}]: lower bound lb^k < m failed.")
        if not (m * (ub.denominator ** k) < ub.numerator ** k):
            raise CertificateVerificationError(f"tower[{idx}]: upper bound m < ub^k failed.")
        if prev_k is not None and prev_m is not None:
            if k <= prev_k:
                raise CertificateVerificationError(f"tower[{idx}].k={k} must strictly exceed previous k={prev_k}.")
            # Verify strict improvement: prev_m^{1/prev_k} < m^{1/k} <=> prev_m^k < m^{prev_k}
            if not (prev_m ** k < m ** prev_k):
                raise CertificateVerificationError(f"tower[{idx}] does not strictly improve previous base bound.")
        prev_k, prev_m = k, m
        verified_steps.append({"k": k, "m": m, "lb": rat_to_str(lb), "ub": rat_to_str(ub)})

    return {
        "schema": CERT_SCHEMA,
        "mode": "supermultiplicative_base_tower",
        "verdict": "BASE_TOWER_CERTIFIED",
        "r": r,
        "num_levels": len(verified_steps),
        "strictly_increasing": True,
        "highest_lb": verified_steps[-1]["lb"],
    }


def _verify_mode4_crossover(cert: Dict[str, Any]) -> Dict[str, Any]:
    r = _parse_int(cert.get("r"), "r")
    B = _parse_int(cert.get("B"), "B")
    k_star = _parse_int(cert.get("k_star"), "k_star")
    if r < 3 or B <= r - 1 or k_star < 2 or k_star > 500:
        raise CertificateVerificationError("Require r >= 3, B > r - 1, and 2 <= k_star <= 500.")

    # Verify k_star is the EXACT first integer where B^k < k! * (r - 1)^k
    lhs_prev = B ** (k_star - 1)
    rhs_prev = factorial_exact(k_star - 1) * ((r - 1) ** (k_star - 1))
    lhs_curr = B ** k_star
    rhs_curr = factorial_exact(k_star) * ((r - 1) ** k_star)
    if not (lhs_prev >= rhs_prev and lhs_curr < rhs_curr):
        raise CertificateVerificationError(
            f"k_star={k_star} is not the exact first crossover where B^k < k! (r-1)^k."
        )
    # Verify persistence condition for all k >= k_star: B <= (k_star + 1) * (r - 1)
    persists = B <= (k_star + 1) * (r - 1)
    if not persists:
        raise CertificateVerificationError("Persistence condition B <= (k_star + 1)(r - 1) failed.")

    return {
        "schema": CERT_SCHEMA,
        "mode": "erdos_rado_fixed_base_crossover",
        "verdict": "CROSSOVER_CERTIFIED",
        "r": r,
        "B": B,
        "k_star": k_star,
        "persists_for_all_ge_k_star": True,
    }


def verify_sunflower_certificate_exact(cert: Dict[str, Any]) -> Dict[str, Any]:
    """Verify a SUNFLOWER-BASE-CERT-1.0 JSON dictionary using exact integer/rational arithmetic only."""
    if not isinstance(cert, dict):
        raise CertificateVerificationError("Certificate must be a JSON object.")
    _assert_no_floats(cert)
    if cert.get("schema") != CERT_SCHEMA:
        raise CertificateVerificationError(f"Unsupported schema: {cert.get('schema')!r}")
    mode = cert.get("mode")
    if mode not in VALID_MODES:
        raise CertificateVerificationError(f"Unknown mode: {mode!r}")

    if mode == "sunflower_free_family_exact":
        return _verify_mode1_sunflower_free(cert)
    if mode == "graph_two_uniform_extremal":
        return _verify_mode2_graph_two_uniform(cert)
    if mode == "supermultiplicative_base_tower":
        return _verify_mode3_base_tower(cert)
    return _verify_mode4_crossover(cert)
