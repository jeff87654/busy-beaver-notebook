---
name: screening-lessons
description: "Lessons on our screening pipeline (2026-10-22 after champ_231): rank by estimated size not grade name; never dismiss a top grade by base rate; positive controls; re-screen after bug fixes"
metadata:
  type: feedback
---
Every big find of October 2026 (C04, M8, h003, champ_231) had first been set aside by a screen or by the lead:
- C04: dismissed as "Collatz-hard"; M8: dismissed by a small-world screen (halt_redirect/c7/set8 row 189).
- h003: filed TIME by a grader with t hard-coded to 0, then mis-tested in an unfaithful world (B = 6, wrong mod 25).
- champ_231: dlscan2 graded it CHAMPION correctly, but the lead set ALL CHAMPION rows aside as constant-slope false
  alarms because earlier CHAMPION rows were (R1 0b+c). 11 of 17 CHAMPION rows actually had Ackermann slopes.

**Why:** a grade name is a coarse label; base rates from earlier batches don't transfer; hard-coded world parameters
silently break grades. **How to apply:**
1. Rank hits by an ESTIMATED SIZE (rule slopes + digits in the first K-config from blank + halting along the real run),
   not by grade name: bb7_holdouts/rank/rank7.py (agent bb7-rank, 2026-10-22) once built; run it after every scan.
2. Never dismiss a top-grade row without reading its rule line (R1 slope 0 = counter; >= 1 = Ackermann).
3. Keep positive controls in every screen's calibration set (BB(7) champion, champ_231, M8, h003, C7) and check
   they still grade/rank correctly after any tool change.
4. Tools' fixed parameters (t, B, world residues, small b in dlscan3 chains) are assumptions: list them per tool;
   when one is found wrong, re-screen everything that tool dismissed.
5. Interesting fact: the BB(7) champion itself is in the June 2026 holdout list (halt undefined), so record
   machines can sit in holdout lists.
Related: [[bb7-champ231-lead]], [[bb7-holdout-triage]], [[open-candidates-log]].
6. dlscan2 BUG (found 2026-10-22 via X33/Z16 false alarms): its R3 fit only uses borrows over k = 1 zero and stops at
   the first tail digit 2, so the reported "tail=1, e3=0" is an unconstrained DEFAULT, not a measurement. Never feed
   dlscan2's tail/e3 into a parity or halting argument; measure k >= 2 borrows literally. rank7 is being fixed (probes
   k = 2..4, any tail digit). Fix dlscan2 itself after the BB(7) scan finishes (report "tail=?" when k>=2 unmeasured).
