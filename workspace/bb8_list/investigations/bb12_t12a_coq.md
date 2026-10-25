# T12a `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---`: machine-checked halt and score

Opus investigators inv-t12a-coq (round 1, restart, round 2) and inv-t12a-coq2 (round-2 end, assembly, score),
2026-10-09/10. Scratch and generators: `bb12_t12a_coq/` (resume notes in NOTES.md).

## Verdict
- **HALTS, machine-checked.** `proofs/BB12_T12a.v`, `Theorem halt : halts tm c0.`
  check.py (run from bb8_list/proofs on 2026-10-10):

      PASS BB12_T12a.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF--- HALTS (machine-checked, no axioms)

- **Score, machine-checked.** `proofs/BB12_T12a_bound.v` imports the halting file unchanged:
  it proves three results, and every `Print Assumptions` says "Closed under the global context":
  - sigma_lower_bound (the f_(omega+1)^2 shape);
  - score_ge_exact (with the exact round-1 depth Wf);
  - beats_n1: T12a's count exceeds n1's exact standard score (BB10_n1_exact.score_value + 1).
- **The screening was right.** Every event spec was validated literally before symbolic execution, and Coq accepted
  every step. Nothing contradicted bb12 screening or `w2_search/t12a_verify/REPORT.md`.
- T12a is n1 (BB10_n1.v) with J0 := 1RK and two new states. It runs n1's round 1, restarts in place from the
  accumulator, runs a second full round of J periods (J >= (F(w) - 9)/7, w = round-1 depth), and halts on L1.
  So sigma is an f_(omega+1) iterate whose count is itself f_(omega+1)-sized: about f_(omega+1)^2.

## 1. Statements
    halt : halts tm c0
    sigma_lower_bound : exists c N J w, c0 -->* c /\ halted tm c /\ ones c N /\
        iter (2 * JJ + 1) F 34 <= w /\ F w <= 7 * J + 9 /\ iter (2 * J) F w <= 6 * N + 11
    score_ge_exact : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ F (F Wf) <= 6 * N + 11
    beats_n1 : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ BB10_n1_exact.score_value + 1 < N

Definitions: F n = arrow n 2 4 = 2 ^(n arrows) 4; JJ = (3T - 13)/7 with T = 2 ^(37 arrows) 3 (sealed);
Wf = the round-1 zero-block length in closed form (fst fin + 2 snd fin - 6, fin = stepn JJ (34, g0), exactly
BB10_n1_exact.Wf); `ones c N` = the tape holds exactly N ones (definition of BB10_n1_bound.v, for the 12-state
symbols).

Halt conventions: T12a halts in state L reading 1, so its standard score (1RZ) is N. n1 halts in state J reading 0
with exactly BB10_n1_exact.score_value ones (BB10_n1_exact.score_closed), standard score score_value + 1. Coq
proves BB10_n1_exact.score_value equals this file's closed form (agreement lemmas arrow_n1, stepn_n1, JJ_n1 on
abstract arguments) and that 6 (score_value + 2) + 11 < F (F Wf) <= 6 N + 11.

## 2. Structure of the proof
B-form as for n1: `Bf L ts A` = L D(t_1)..D(t_n) D(0) D(A) H> 0^inf, D(m) = (10)^m 1, ts nearest-first.
1. Round 1 = n1's run up to n1's halting B-form `Bf (FarE k) (1^w ++ [0]) f` (round1_12.v.in, from BB10_n1).
2. Restart (restart.v.in): R1END, E0..E12 with 12 shallow and deep clearings (CLR4), the junk (0 z5)^x of E5
   eaten into the counter by E11; ends at `Per (lfr [p;3] (FarR k)) 1 (14 J + 3) n a` with F w <= 7 J + 9.
3. Round 2: PERIODS with the left context L (J periods): `Per L (4J+1) 3 n' a'`, n' >= F^(2J)(w).
4. Round-2 end (this work; specs evs_end.py, abstract part end_head/eat/tail.v.in):
   - E20: Per L (4+K) 3 n a -> [L 2^K R20 2 2 0 | a 1^3 0 1^n | 6], R20 = raw cells 111 00 1 00000 1 00000 1 00000.
   - CONV0, then CONV once per depth unit (lemma CONVS, induction), Z0, Z1, CLR (d = 3 at depth 3 from 4):
     [.. 2 2 0 X 2 0 (3 2 0)^(n+1) 1^4 | A24], X = a - 7, A24 = iter 3 (U 3) 4 = 40 + 9 y (lemma acc9:
     clearing outputs from 4 are 4 mod 9, since towers of 2 are 1 mod 3).
   - EAT: the blocks are eaten right to left, six per loop round (the generated loop lemma), one junk unit per
     round; six cases by (n+1) mod 6, written n + 1 = 6 + 6 j + r:
     r = 0, 1 -> [.. 2 4 0 A24 1^3 0 1^3 | 6] -> CONVERT again (3 blocks), SM3, then as below;
     r = 2, 3 -> [.. 10 1^5 0 2 0 (A24+3) 0 1^3 | 6] -> F23 (A24 + 3 = 43 + 9 y becomes y junk units), F24,
                 CLR (d = 2 at depth 3), HALT1;
     r = 4, 5 -> [.. 4 9 0 1^6 2 1^2 0^3 1 2 (A24+3) 0 1^3 | 6] -> G1, CLR (d = 2 at depth 2a + 6), G2, G3,
                 CLR (d = 2), HALT2.
   - HALT1 / HALT2: state L reads 1.
   All three classes are proved, so the real depth class is never needed.
5. Score: every side in the chain is a finite list (`side_ones`); the EAT output side holds j junk units, so the
   halting tape has N >= j >= (n' - 11)/6 ones.

## 3. Tooling notes
- mexp.py (local copy) has two changes, both off for the round-1/restart events: the loop matcher's maximum gap
  length is a module variable (MAXLEN, 200 for the end events; the EAT junk unit is 78 cells and the old limit 64
  split it into two stacks whose final sweep had no loop), and rotated single-gap insertions are tried before split
  stacks (ROTATE).
- gen_final12.py writes the single file: one machine-generation run (round 1/restart lemmas with the original
  settings, identical to the compiled dev/M.v up to fresh variable names), then the end events, one crossing-lemma
  set, then all abstract parts.
- Compile times at Idle: the six EAT lemma sets dominate (dev/M2b.v: 8603 s).
- proofs/BB12_T12a.v (2.64 MB) compiled at Idle in 5 h wall-clock (10:41-15:40). About 15 Normal-priority python workers
  from other jobs were running, so the compile got about half a core. The EAT lemmas are about 45% of the file and
  most of the time. proofs/BB12_T12a_bound.v takes 967 s. check.py, once the .vo exists, takes 4 min (probe only).
- Probe of the statements: bb12_t12a_coq/probe_bound.v (log probe_bound.log).

## 4. Files
- proofs/BB12_T12a.v (gen_final12.py), proofs/BB12_T12a_bound.v (gen_bound12.py from bound12.v.in).
- bb12_t12a_coq/: evs_end.py, vspec.py, probe.py, drv_end.py (specs and literal validation), gen_machine_end.py,
  gen_wrap_end.py, mk_end.py with end_head/eat/tail/main.v.in, wrap_pre.v.in, mkE.sh / mkE1.py / mkB.sh (dev builds
  dev/M2a.v, M2b.v, E.v, B.v), end/ (analysis: r2end.py, chain.py, mid.py).
