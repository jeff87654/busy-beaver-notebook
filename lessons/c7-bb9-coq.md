---
name: c7-bb9-coq
description: C7 = M8 + H0=0LI, I=1LC0RA: BB(9) record Coq-PROVED, N > f_omega^5(2*2^^13 3) and f_omega^6(12) (Lower5), PUBLISHED PR #32; mexp + fixpoint-unification lessons
metadata:
  type: project
---
C7 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA halts; Coq proof in
bb8_list/investigations/bb9_c7_coq (c7/Statement.v: c7_halts, c7_lower f_omega^4 (6*arrow 13 2 3+3) < N,
c7_beats_m8_bound, c7_table; probe Closed, 42-file closure; build `python tools/sched.py 2 c7/probe.v`).
PUBLISHED BB9/verify_c7 (PR #32, 09295ab, CI 37 min). c7/Lower5.v: c7_lower5 f_omega^5 (2*arrow 13 2 3) < N, c7_lower6_12
f_omega^6 12 < N (levels start at the J2 clear, depth (27B+33)/5; f (k+2) x <= U k x gives f_omega 12 <= Bx). See [[bb9-c7-lead]], [[f3-0rc-bb9-candidate]], [[m8-bb8-c04-collapse]].

Run: J-rebuilds (phase A n=1 mod 5, B frame-1 rebuild, C n=3 mod 5, D, counter 2R5+3 rounds) then C7's OWN cascade
(L -> (3L+c)/5, c1=-23 c3=-14 c0=-20 c4=-32; C04's cascade lemmas NOT reusable: they contain E0 events) and the
r=2 branch (L=15u+17, halts iff u = 1,2 mod 5; real u = 2 mod 5). All accumulators = rho mod 2^5 3^4 5^14.

**Why:** record-chasing proof; reuse its tools for similar M8-variant proofs.
**How to apply:** mexp (gen/) lessons: split phases whose loop runs over a SUM of two run vars; fix small params
(s, t, p, c) concretely when small values behave differently (check with gen/vcheck2.py); take TARGET in the
syntactic form the run reaches (Coq finish_norm cannot rotate (11111001)^t); if a generated script fails at a
crossing (`follow cr_*` on a rotated run), regenerate a longer phase without the intermediate B> moment. Coq: clear
Z-mod residue hyps (13-digit constants) before lia; Score.v exports a theorem named S1 (re-import Individual112);
`exists a, b, ...` with >5 terms failed here (one exists per witness); never `replace 7 with ...` (hits numerals).
Never let Defs.f_omega and Score.f_omega (convertible copies) be unified at a closed argument (numeral or sum):
rewrite/exact then evaluates the fixpoint f (coqc hit 19 GB). Transfer via lemmas with a variable argument (Lower5 tr5/tr6).
