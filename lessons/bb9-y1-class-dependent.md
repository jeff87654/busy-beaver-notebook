---
name: bb9-y1-class-dependent
description: Y1 (M8 + H1->0LI, I=0RA---) is OPEN/not certifiable: halts at M8's point (sigma(M8)-1) in key31 rho 0/4; extensions of M8's halt are class-dependent
metadata:
  type: project
---

2026-10-18, bb8_list/investigations/bb9_y1/REPORT.txt. Y1 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG0LI_0RA---.
M8/C04 halting configs (Coq Hc d s G l R n t) have the head on the last 1 of token D(d). d = 0 for key31 rho=0,4; d >= 1 otherwise.
So left-moving H1 extensions branch on the uncomputable class at their first step. Y1 halts with sigma(M8)-1 there, about 20% heuristic.
Other classes: rounds of escalation (f_w^3, f_w^4, ...), each with halting chances that depend on uncomputable residues. Verdict OPEN, not a record.

**Why:** the class (key, rho) depends on B's full base-5 orbit [[c04-bb9-parity-record]].
**How to apply:** prefer right-moving H1 extensions (the right side HR is class-independent). In representative worlds use R = 366 + 3600i: every tower accumulator is 366 mod 3600. Fixed R makes rounds repeat exactly, which is an artefact.
