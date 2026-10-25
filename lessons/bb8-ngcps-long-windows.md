---
name: bb8-ngcps-long-windows
description: NGramCPS with long asymmetric windows (nL=10,nR=14) proved the m7 0RB0LC champion-tower machine; reusable verified Coq checker generator
metadata:
  type: project
---
2026-10-07: m7 machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE (champion recursion, unbounded tower of
rebuilt epochs; two earlier agents spent ~1M tokens on epoch-by-epoch families) was PROVED by plain NGramCPS with left
windows 10 / right windows 14 (2.86M local configs). Symmetric n<=13 and the mxdys portfolio (n<=6, 120 s) fail;
MitM summaries (RWL_mod with tail anchors, run tokens, anchored n-grams) explode or hit spurious halts.

**Why:** when the only halt lives at the right end, long right windows alone can separate the protected tail from the
halting ending; joint (state, left window, right window) set is needed (product form fails).

**How to apply:** before building macro families for a champion-like NOBOUNDARY machine, scan
`investigations/bb8_m7_0RB0LC_ctl/ngcps2.exe MACHINE nL nR` over asymmetric pairs up to ~16. If it closes, emit a
busycoq proof with `gen_ngcps_v.py CERT OUT.v FUEL` (generic sound checker `nonhalt_of_check`, window sets as data,
C recomputed by vm_compute; ~8 min for 2.9M configs; edit the tm table in the template for other machines).
Related: [[bb8-champion-subtree-lead]], [[bb8-m7-nobd-1RH1LG-r4]].
