---
name: bb8-m7-nobd-1RH1LG-r4
description: R4 structure of the m7 NOBOUNDARY machine 1RB0RA..1RH1LG_0RG1LD_0RH0RF (rebuild to a P-less list, D2 stage, final cycler) and the P-less K-parser trick
metadata:
  type: project
---

For champion-rule machines whose R4 probes all time out, parse snapshots as K words WITHOUT the leading 11 and with arbitrary token values (gen/gk3.cpp in investigations/bb8_m7_1RB0RA_1RH1LG): the first clean K configuration after R4 shows up in a few hundred steps. The old P=11, m=1 mod 3 detectors miss it.

For 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF: K(0^n;0;b) -->+ P-less tokens [6b+5, 1^(n+2)], r=2 (Coq-proved, 41 lemmas); champion rules R1-R3 continue; residue-2 token deleted by a D2 stage [2,1^k] -> [2r+3,1^(k-1)]; used-up list enters a period-70 translated cycler. Never halts (strong evidence); Coq gap is the used-up transient (mexp.explore stuck at D bouncing on (100100)^x) plus abstract glue.

**Why:** report bb8_list/investigations/bb8_m7_1RB0RA_1RH1LG.md; mexp.py of the BB(9) record pipeline ports to other TMs by swapping TM and tail in common.py/shapes.py (R1-R3, REBUILD explore in seconds).
**How to apply:** for sibling machines of the m7 subtree try gen/gen_full.py first; see [[bb8-first-return-map-method]].
