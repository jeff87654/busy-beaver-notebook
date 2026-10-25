---
name: bb8-first-return-map-method
description: "Method that cracked a non-counter BB(8) holdout (048631 1RB0RC1LB1RD): probe the family with random states, fit the first-return map, validate on a long orbit"
metadata:
  node_type: memory
  type: feedback
---

For BB(8) holdouts that dlscan/Quick_Sim/kfit cannot fit (constant slopes, no proven rules, tape width growing like log t):
- Find the left-end return events (head back at the leftmost cell in one fixed state) and parse each return tape into a parametrized family (here `(10)^a 11 B(a+2) B(t1)..B(tk)`); width conserved inside an epoch is the tell.
- Then simulate literally from RANDOM members of the family (not just the orbit) to the next return. If every random member returns to the family, the first-return map is total and non-halting reduces to simulation lemmas for it. Fit the map from those probes (e.g. a mod 5 pushes, 1-digit count mod 10).
- Validate the fitted map on a long literal orbit with a Rust checker (1e9 steps in about 11 s; gcc is absent, rustc works). The first fit missed a regime (u mod 10) that only appeared at step 4.5e9, so run 1e10+ steps and sweep long prefixes before trusting a table.
- Generic searches that failed on it: two-DFA SAT certificates (UNSAT to 6x6), n-gram CPS (saturates), backward reasoning from the halting pattern (tree grows).

**Why:** calibration lesson from investigation bb8_048631_1RB0RC1LB1RD (Sonnet 5.5, about 370k tokens, no Coq PASS but an exact reduction to hand to Opus).
**How to apply:** try this before regular-certificate SAT searches; scripts are in `bb8_list/investigations/bb8_048631_1RB0RC1LB1RD/` (`phi.py`, `phicheck.rs`, `randlist.py`, `tabmu2.py`).
