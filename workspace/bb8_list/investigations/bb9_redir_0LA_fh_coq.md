# 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA (three-cycle sibling): machine-checked halting and score

Opus investigator (inv-bb9-redir-coq), 2026-10-08. Scratch and generators: bb9_redir_fh_coq/ (NOTES.md is the resume file).

## Verdict
- **HALTS, machine-checked.** proofs/BB9_redir_0LA_fh.v, `Theorem halt : halts tm c0.`
  check.py output (run from bb8_list/proofs):

      PASS BB9_redir_0LA_fh.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA HALTS (machine-checked, no axioms)

  - The file is 985 KB (753 lemmas and theorems).
  - It compiled in 6663 s wall at Idle priority (one coqc at a time, loaded PC).
  - The same text, split as machine part plus abstract part, had compiled earlier: 12135 s + 322 s.
- **Exact score, machine-checked.** proofs/BB9_redir_0LA_fh_bound.v imports the halting file unchanged.
  - Every Print Assumptions is "Closed under the global context".
  - The halt is in state I reading a 0 (I0 undefined), so the standard score is ones + 1.
- **It beats the two-cycle machine (0LA) and the BB(9) record, machine-checked.**
  - beats_0LA_formula compares against 0LA's exact count, with the same bf, nn and KK.
  - beats_record compares against BB9_record_bound.score_closed, imported unchanged.

## 1. Theorem statements (printed by Coq: bb9_redir_fh_coq/probe_fh.v, probe_fh.log; all six Print Assumptions closed)

    halt : halts tm c0
    score_exact  : exists c, c0 -->* c /\ halted tm c /\ ones c (86 + 9 * uu + (6 * b4 - 12 * b3 + 26) + 10 * (nn - 3))
    b3_closed    : 2 * b3 + 4 = arrow (KK + 2) 2 5
    b4_closed    : 2 * b4 + 4 = arrow (KK + 42) 2 4
    score_closed : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\
                     N + 12 * b3 = 3 * arrow (KK + 42) 2 4 + 9 * uu + 10 * (nn - 3) + 100
    sigma_lower_bound : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ arrow (KK + 42) 2 4 < N
    beats_0LA_formula : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\
                     3 * arrow (KK + 2) 2 5 + 10 * nn + 6 * (KK / 5) + 11 < N
    beats_record : exists cc Nc co No,
       c0 -[ BB9_record_1RB0RA.tm ]->* cc /\ halted BB9_record_1RB0RA.tm cc /\ BB9_record_bound.ones cc Nc /\
       c0 -->* co /\ halted tm co /\ ones co No /\ Nc + 1 < No

The definitions are:
- nn = (12 bf + 8)/5 and KK = 2 nn + 35;
- b3 = U KK (U KK (U KK 0)) and b4 = U (KK + 41) 0;
- uu = (KK + 12 b3 - 2)/5;
- bf = U 34 (U 34 0), sealed, with 2 bf + 4 = arrow 37 2 3 (bf_closed in the halting file).

U, arrow and ones are as in BB8_champ35_bound.v. The left side of beats_0LA_formula is the ones count of the two-cycle
machine (BB9_redir_0LA_bound.score_closed), with the same nn and KK, because both runs share stages 0 and 1.

In words, with K = KK: the score is about 3 * 2 ^(K+42 arrows) 4, against 3 * 2 ^(K+2 arrows) 5 for the two-cycle
machine. Here K = 2n + 35, n = (12 bf + 8)/5, and 2 bf + 4 = 2^^37 3.

## 2. The run, as proved
Family: Kf ds a r = 0^inf D(d_n)..D(d_1) D(a) D(r) (10)^4 F> 0^inf. Digit form: Kg ds suf a b = Kf (map (3d+1) ds ++ suf) (3a+1) (3b).
1. c0 -->* Kg (0^34 2) [] 0 0 in 6524 steps. CDP then gives Kg (0^35) [] 0 bf, the same values as the BB(8) record.
2. **Stage 0.**
   - Literally it is the same as in the two-cycle machine: the same E0 configuration, and it ends at
     Kf(1^(2n+34) 7 6 8 9^n | 1 | 0).
   - The proof needs different pieces, because G and H differ:
     - P0 and P0B lead into the hop phase.
     - HOP_loop3 is a hand-specified loop: the 35 zero digits hop right one per round.
     - P0C ends at E0 = 0LI. The glue uses r = 3 bf = 3 + 5w.
     - P0D leads to the first macro-round point.
     - MR1 is four rounds of the D9-producing loop as one rule (20 zero digits). It is iterated in Coq by MR_iter.
     - P0E is the exit.
3. **Champion part, as in 0LA.**
   - CDP clears the 2.
   - The suffix tokens are borrowed 6 -> 3 -> 0 (CLRS).
   - Result: Kf(1^K 0 8 9^n | 1 | 3 b3).
4. **Stage 2** (ST2): Kf(1^m 0 8 9 9 l | 1 | 11 + r) -->* Kf(1^(m+41) 3 (4 + 2r) 8 l | 1 | 0) for all m and r.
   - Here m = K and 11 + r = 3 b3, so the new token is 6 b3 - 18.
   - The borrow 3 -> 0 at depth K+41 (CLRS) gives Kf(1^(K+41) 0 (6 b3 - 18) 8 9^(n-2) | 1 | 3 b4), with b4 = U (K+41) 0.
5. **Stage 3.**
   - ST3E: Kf(1^M 0 (3+T) 8 9 l | 1 | r) -->* Yc(T, 2r+5, M+2).
   - Y1: one round, Yc(T+1, a+2, z) -->* Yc(T, a, z+2) for a >= 1. It is iterated by Y_iter: T rounds.
   - ST3X: Yc(0, 21+a, 3+5u) -->* halt in state I reading 0.
   - The real values are a = 6 b4 - 12 b3 + 26 and z = K + 12 b3 + 1 = 3 + 5u.
   - The explorer showed that every residue of z mod 5 halts. The proof uses only the real one.
6. **Arithmetic.**
   - bf = 16 mod 25 and b3 = 16 mod 25: each of 2x + 4 is a power tower, which is 36 mod 50 (arrow_mod50).
   - b3 >= 14.
   - b4 >= 2 b3 + 2 (U_deep_ge), using arrow (K+42) 2 4 >= arrow (K+1) 2 (arrow (K+2) 2 5) >= 2 (2 b3 + 4).
7. **Ones at the halt:** 86 + 9u + a + 10 (n - 3). Literally exact on small instances (129 and 187).

## 3. Corrections to FINDING_9state_0LA.md (Siblings section)
- **Stage 2's target [D9^(x-2), D8, D(2r-18), D0, D4^(m+40), D1 | D37 | D18] is a champion-rule snapshot.**
  - The machine part ends earlier, at [D9^(x-2), D8, D(2r-18), D3, D1^(m+41) | D1 | D0].
  - The third clearing is then a single borrow 3 -> 0 at depth K+41, with counter U (K+41) 0.
  - This matches the FINDING's "third clearing over D4^(m+40)", seen from one step earlier.
- **Stage 3, in the real regime (accumulator far above T):**
  - first T rounds, each lowering T by 1, the accumulator by 2, and adding 2 zero digits;
  - then a short exit.
  - The exit halts for every zero count mod 5. The real one is 3 mod 5.
- **Ones = 86 + 9u + a + 10(n-3), with a = 6 b4 - 12 b3 + 26.** The dominant term is 6 b4 = 2 R3, as the lead said.
  The follower's 13/5 R3 is not right.

## 4. Structure and tooling (bb9_redir_fh_coq/)
- **Generators.**
  - gen_machine_fh.py writes all machine-level lemmas, generated by mexp.
  - gen_final_fh.py assembles the halting file from abstract_fh_base.v.in, run_fh.v.in, arith_fh.v.in and main_fh.v.in.
  - mk_bound_tmpl.py and gen_bound_fh.py build the bound file.
- **Machine-specific shapes:** st0a.py, hop.py, st0b.py, mr.py, st2c.py, st3e.py, st3y.py, st3x.py.
- **New techniques compared with 0LA:**
  - drive_peel (phases.py): drive the explorer and peel a big run whenever the head reads into it. This finds the
    natural targets of stages 2 and 3.
  - Multi-round loops whose rounds contain hand-type inner loops are written as one-round (or four-round) rules between
    natural stuck points, and iterated in Coq by induction. The explorer cannot generalize them as loops itself.
  - Hand-specified transfer loops (handloop.make_loop), as in 0LA.
- **Cost.** All coqc ran at Idle, one at a time.

| run | wall time |
|---|---|
| machine part (dev) | 12135 s |
| abstract part (dev) | 322 s |
| bound file (dev) | 373 s |
| bound file (final, proofs/) | 238 s |
| final halting file | 6663 s |

## 5. Lessons
- `Opaque` flags are not exported. In a file importing the halting proof, `fold (B3 s)` unfolded U and hung.
  Restate `Opaque U arrow` in importing files.
- `replace (3 * b3) with ...` also rewrites inside `3 * b3 - 11` elsewhere in the goal. Name such terms first
  (`set (r' := 3 * b3 - 11) in *`).
- A 955 KB generated machine part costs about 3.4 hours at Idle on this PC. Most of it is concrete configurations in
  the statements of the stage-2 and stage-3 lemmas.
