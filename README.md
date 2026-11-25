# Exact-Z/Q Extremal Sunflower-Free Families, Supermultiplicative Base Lower Bounds, and Fixed-Base Crossover Certificates for the Fixed-Petal Sunflower Theorem

**Author:** Lluis Eriksson (prepared with AI assistance — Google Antigravity)  
**License:** MIT (`LICENSE`)  
**Lean 4 Toolchain:** `leanprover/lean4:v4.35.0` (zero external dependencies, 18/18 theorems, 0 `sorry`, 0 `Classical.choice`, 0 warnings)  
**Certificate Schema:** `SUNFLOWER-BASE-CERT-1.0` (pure Python stdlib exact integers & `fractions.Fraction`, zero floating-point trust)

## Overview

Complementing OpenAI's November 24, 2026 proof of the Erdős–Rado fixed-petal sunflower conjecture ($M_r(k) \le B_r^k$), this repository establishes and machine-checks exact finite-$k$ extremal lower bounds on the optimal sunflower base $b_r = \sup_k M_r(k)^{1/k}$, parity dichotomies in $2$-uniform graphs, an explicit $20$-set double $\mathbb{RP}^2$ hemi-icosahedron construction for $M_3(3) \ge 20$, and exact big-integer crossover thresholds $k^*(r, B)$ against Erdős–Rado's factorial bound $k!(r-1)^k$.

## Quick Verification

```bash
python scripts/verify_all.py
```
