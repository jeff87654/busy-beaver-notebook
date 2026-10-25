---
name: bb12-t12a-coq
description: T12a 12-state f_(omega+1)^2 halter: proofs/BB12_T12a.v check.py PASS, bound file beats n1 (2026-10-10); round-2-end spec workflow and pitfalls
metadata:
  type: project
---
T12a = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF--- HALTS, Coq-checked
2026-10-10: proofs/BB12_T12a.v (check.py PASS), proofs/BB12_T12a_bound.v (sigma_lower_bound F^(2J)(w) <= 6N+11 with
F w <= 7J+9; score_ge_exact F(F Wf) <= 6N+11; beats_n1 N > BB10_n1_exact.score_value + 1). Generators and notes:
bb8_list/investigations/bb12_t12a_coq/ (NOTES.md), report investigations/bb12_t12a_coq.md.

**Why:** first machine-checked f_(omega+1)^2-class candidate (12 states), built on [[bb10-n1-coq]].
**How to apply:** for sibling machines reuse evs_end.py + vspec.py (view-string specs) + drv_end.py (fast literal
word-compare validation) + mexp. Pitfalls: mexp's loop matcher max gap (MAXLEN) must exceed the junk-unit length
(78 cells here) or loops split into unusable stacks; never `rewrite` between two separately defined arrow functions
in goals with huge closed arguments (matcher unfolds and hangs) -- compare closed forms as a function of (stepn,
arrow, JJ) on abstract arguments; the single 2.6 MB file needs ~2.5-5 h at Idle (EAT loop lemmas dominate).

**PUBLISHED 2026-10-11 (user request): github.com/jeff87654/busy-beaver PR #12 merged (abf0283): BB12/** -- write-up
BB12/1RB0RA_..._0RL---_0RF1RZ.md (standard string: K1 = ---, L1 = 1RZ), verify/multifile (16 files incl. the n1 set
byte-identical to BB10/, new BB12_T12a_fgh.v: fgh_lower2 f_(w+1)(f_(w+1)(JJ-2)) <= 6N+11, also copied to
bb8_list/proofs), from-scratch build log (11071 s, BB12_T12a.v 9989 s at Idle), probe 24 eq_refl + 5/5 closed,
sha256. An Opus reviewer fact-checked the write-up (10 fixes). No single self-contained file yet. CI does not build
BB10/BB12. Worktree C:/Users/jeffr/Downloads/busy-beaver-bb12 (branch bb12-t12a) left in place; the main clone is
on another session's zf-336 branch with uncommitted work -- never touch it.
