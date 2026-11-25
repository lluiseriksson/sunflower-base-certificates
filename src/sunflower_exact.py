"""Pure-stdlib exact-Z/Q extremal sunflower-free family constructors and exhaustive checkers.

Zero floating-point operations anywhere in this module.
Author: Lluis Eriksson
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import List, Sequence, Tuple


def rat_to_str(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def factorial_exact(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial requires n >= 0.")
    res = 1
    for i in range(2, n + 1):
        res *= i
    return res


def is_r_sunflower(sets: Sequence[frozenset[int]]) -> bool:
    """Return True iff the r distinct sets form an r-sunflower (all pairwise intersections identical)."""
    r = len(sets)
    if r < 2:
        return False
    core = sets[0] & sets[1]
    for i in range(r):
        for j in range(i + 1, r):
            if (sets[i] & sets[j]) != core:
                return False
    return True


def count_r_sunflowers(family: Sequence[Sequence[int]], r: int) -> int:
    """Exhaustively count all r-sunflowers in family (exact integer check, 0 floats)."""
    fsets = [frozenset(s) for s in family]
    cnt = 0
    for tup in combinations(fsets, r):
        if is_r_sunflower(tup):
            cnt += 1
    return cnt


def abbott_hanson_sauer_2_uniform(r: int) -> Tuple[int, List[Tuple[int, int]]]:
    """Construct exact optimal 2-uniform r-sunflower-free graph for any r >= 3.

    - Odd r = 2t + 1: two disjoint copies of K_r on 2r vertices, |E| = r(r - 1).
    - Even r = 2t: circulant graph on n = 2r - 1 vertices with max degree r - 1
      and |E| = (r - 1)^2 + (r - 2)/2 edges (one vertex of degree r - 2, rest r - 1).
    """
    if r < 3:
        raise ValueError("Require r >= 3.")
    if r % 2 == 1:
        n = 2 * r
        edges: List[Tuple[int, int]] = []
        for u in range(r):
            for v in range(u + 1, r):
                edges.append((u, v))
        for u in range(r, 2 * r):
            for v in range(u + 1, 2 * r):
                edges.append((u, v))
        return n, sorted(edges)

    # Even r = 2t >= 4: n = 2r - 1 vertices (odd).
    # Degree r - 1 = 2t - 1 is odd!
    # Step 1: Add all circulant chords at distances 1, 2, ..., t - 1 => every vertex has even degree 2t - 2 = r - 2.
    # Step 2: Add a matching of size (n - 1)/2 = r - 1 connecting (i, i + t) for pairs skipping vertex n - 1,
    # using vertices 0..2r-3 paired into r - 1 disjoint non-edges (distance t, since t > t - 1)!
    # Wait: check that distance t does not collide with distances 1..t-1 mod n (n = 4t - 1 >= 7):
    # t <= (4t - 1) // 2 = 2t - 1, and n - t = 3t - 1 > t - 1! So distance t is 100% disjoint from 1..t-1!
    t = r // 2
    n = 2 * r - 1
    edge_set = set()
    for d in range(1, t):
        for i in range(n):
            u, v = i, (i + d) % n
            edge_set.add((min(u, v), max(u, v)))
    # Add (r - 1) disjoint edges of distance >= t on {0, ..., n - 2} (even count 2r - 2 = 4t - 2):
    # Simply pair i with i + (2t - 1) for i = 0, ..., 2t - 2!
    # Check cyclic distance of (2t - 1) mod (4t - 1): min(2t - 1, 2t) = 2t - 1 >= t (for t >= 1)!
    # So NONE of these edges collide with distances 1..t-1!
    for i in range(r - 1):
        u = i
        v = i + (r - 1)
        assert (u, v) not in edge_set
        edge_set.add((u, v))
    return n, sorted(edge_set)


def hemi_icosahedron_20_family() -> Tuple[int, List[Tuple[int, int, int]]]:
    """Construct exact 20-set 3-uniform 3-sunflower-free family on 12 elements:
    two disjoint copies of the 10-triangle RP^2 hemi-icosahedron triangulation.
    """
    base10 = [
        (0, 1, 2),
        (0, 2, 3),
        (0, 3, 4),
        (0, 4, 5),
        (0, 1, 5),
        (1, 2, 4),
        (2, 3, 5),
        (1, 3, 4),
        (2, 4, 5),
        (1, 3, 5),
    ]
    copy2 = [(a + 6, b + 6, c + 6) for (a, b, c) in base10]
    return 12, sorted(base10 + copy2)
