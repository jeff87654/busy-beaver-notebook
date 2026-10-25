---
name: f3-0rc-bb9-candidate
description: "!!! f3_0RC = M8 with H0=0LI, I=0RC/1RF: 9-state machine beating M8 in EVERY class, COQ-PROVED 2026-10-20 (bb9_f3_coq, lead re-ran probe 2026-10-21); packaging PR bb9-f3 by agent f3-package; dominated by the C7 lead if that proves"
metadata:
  type: project
---

2026-10-19 (y1-fable): f3_0RC = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_0RC1RF (twin ..._1RD1RF).
Family F3: I1 = 1RF reproduces M8's H0 = 1RG at marker exhaustions; I0 fires only at far-left (top-level) exhaustions.
Pipeline: exh#1 -> digits (4, 2B-1) at depth 7 -> R'' >= 2^^9(2B) -> list 12R''+11 with digit 7 -> R2' -> top stop
L0' = (324R''-359)/25 (odd, 1 mod 3) -> M8's cascade + endgame (Coq casc_keyU reusable). sigma > f_w^2(12R''+11) > M8's
upper bound f_w^2(12B+27) in every class. Folder bb8_list/investigations/bb9_y1_fable (REPORT.txt sec. 7, runs/param,
runs/routes). Needs three new rebuild lemmas for Coq (P1 parametric in B, P2 champion phase, P3 top stop).
Y1/Y2: settled uncertifiable (theorem: no faithful 9-state extension of M8 is class-robust; no residue invariant).

**How to apply:** when BB(9) records come up, f3_0RC is the lead; check OPEN_CANDIDATES.txt for its status before redoing work.

2026-10-20: COQ DONE in bb9_f3_coq (X = 11-state C04 variant, f3 simulated by X; Statement.f3_halts, f3_lower, f3_beats_m8_bound, f3_table; probe Closed x2). Lead re-ran f3/probe.v 2026-10-21: exit 0, Closed. Packaging as BB9/verify_f3 (branch bb9-f3, agent f3-package, no merge without CI green). See [[bb9-c7-lead]].
