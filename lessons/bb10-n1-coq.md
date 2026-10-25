---
name: bb10-n1-coq
description: n1 (10-state, f_(omega+1)) halting proof BB10_n1.v passes check.py; bound file beats BB(10) champion and 0LJ0LC (2026-10-08)
metadata:
  type: project
---
n1 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC HALTS, Coq-checked 2026-10-08:
proofs/BB10_n1.v (check.py PASS), proofs/BB10_n1_bound.v (ones >= F^N(34), N = (6T-19)/7, T = 2^^37 3,
F n = 2^(n arrows) 4; beats_champion, beats_lead (0LJ0LC), dominates/beats_M3_bound). Generators and notes in
bb8_list/investigations/bb10_n1_coq/ (NOTES.md), report investigations/bb10_n1_coq.md.

**Why:** first f_(omega+1)-class BB(10) candidate with a machine-checked proof.
**How to apply:** reuse its mexp event-spec workflow (evs.py + drv.py lit) for sibling machines; M3 still lacks a
proved upper bound, so "n1 > M3" is only by domination. Related: [[bb8-champion-subtree-lead]].
