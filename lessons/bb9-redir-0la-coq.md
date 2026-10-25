---
name: bb9-redir-0la-coq
description: BB(9) redirect candidates 0LA and its three-cycle sibling (..._1LC1RH_0LH0RF_---0LA) proved halting in Coq with exact scores beating the BB(9) record (2026-10-08); tooling lessons
metadata:
  type: project
---

Proved, check.py PASS:
- **0LA:** proofs/BB9_redir_0LA.v plus _bound.v.
  - ones = 3*arrow(KK+2) 2 5 + 10nn + 6KK/5 + 11, with nn = (12bf+8)/5, KK = 2nn+35, 2bf+4 = arrow 37 2 3.
- **Sibling:** proofs/BB9_redir_0LA_fh.v plus _fh_bound.v.
  - ones + 12 b3 = 3*arrow(KK+42) 2 4 + 9uu + 10(nn-3) + 100.
  - beats_0LA_formula and beats_record are closed.

Reports: investigations/bb9_redir_0LA_coq.md and investigations/bb9_redir_0LA_fh_coq.md. Generators are in
investigations/bb9_redir_0LA_coq/ and bb9_redir_fh_coq/:
- handloop.py: hand-specified transfer loops;
- phases.drive_peel: peel big runs;
- multi-round loops as rules plus Coq induction.

**Why:** later 9/10-state redirect candidates reuse these generators.

**How to apply:**
- FINDING "events" are often plain champion rules: BB8 X3 is generic in the borrowed token.
- Stage targets with D4^k lists are later champion snapshots.
- The kernel can hang at Qed when lia ran with closed arrow terms; state the final arithmetic over variables.
- Opaque is not exported: restate `Opaque U arrow` in importing files.
- A 1 MB generated proof takes 2-3.5 h at Idle here.

Related: [[bb8-champion-subtree-lead]], [[coq-selfcontained-merge-lessons]].
