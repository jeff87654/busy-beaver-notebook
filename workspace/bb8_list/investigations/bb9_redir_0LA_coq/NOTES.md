# Coq proof of 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA (scratch notes, resume here)

## Findings so far (2026-10-07, literal + symbolic checks)
- Family Kr ds a r = ([1;0]^^2 *> 1 >> [1;0]^^(S r) *> 1 >> [1;0]^^a *> 1 >> lfr ds) {{G}}> const 0,
  lfr (d::t) = [1;0]^^d *> 1 >> lfr t (token D(d)). Kc of BB8_champ35 = Kr (map (3d+1) ds) (3a+1) (3b).
- Champion rules hold for raw tokens (hand lemmas R1F/R2F/X3 are generic in the token):
  R1 Kr ds (3+a) r -> Kr ds a (2r+6); R2 Kr ((3+x)::t) 1 r -> Kr (x::t) (2r+7) 0;
  R3 Kr (1^(M+1) ++ (3+x)::t) 1 r -> Kr (1^M ++ (2r+7)::x::t) 1 0, for every x >= 0 (also x = 0: borrow from D3 is plain R3;
  the FINDING's "Stage 1 event" is just a champion-rule snapshot).
- Stage 0 (machine level, explored by mexp in 2 s, st0.py): from c_end J (5n+1) (E reading 0, now E0 = 0LI)
  to Kr (1^(2n+J) ++ [7;6;8] ++ 9^n) 1 0. The FINDING's "D4^k" list is produced afterwards by plain R3 with r = 0.
- Champion process: Kg (0^(2n+J) ++ [2]) [6;8;9^n] 0 0 -> CDP -> Kg (0^K) .. (U K 0), K = 2n+J+1;
  borrow 6->3 and 3->0 (R3 from the suffix + CDP): b3 = U K (U K (U K 0)); 2 b3 + 4 = arrow (K+2) 2 5.
- Stage 2 (mexp phases, st2.py/st2d.py/p3loop.py): Kr (1^m ++ 0::8::l) 1 r halts in state I reading 0 whenever m = 5u, u >= 1
  (phase 1 auto; regroup m = 5u; phase 2 auto; units U = 3u; phase 3 = hand loop X(v,i) (p3loop.X), end auto).
  Literal: ones = 2r + 10p + 6m/5 + 23 (p = number of D9 tokens), checked m = 5..95 (step 5), several p, r.
  The FINDING's "halts unless m' in {0,7}" and the mod 7 / mod 35 dependence are about OTHER residues; the real
  path only needs m' = 0 mod 5, i.e. B = 16 mod 25 (2B+4 = tower of 2s = 36 mod 50).
- Real values: bf = U 34 (U 34 0) (2 bf + 4 = arrow 37 2 3), bf = 25 s + 16, n = 60 s + 40, K = 2n+35 = 5(24 s + 23).
  Score N = 2 r + 10 n + 6K/5 + 23 with r = 3 b3: N = 3 * arrow (K+2) 2 5 + 10 n + 6K/5 + 11.

## Tools
- lit.py, trace0.py, trace2.py, snap.py, grid2.py: literal simulation (tm_old.Sim).
- common.py (autoproof for this machine, KR/tok shapes), mexp.py (copy), phases.py (drive, regroup),
  handloop.py (make_loop: hand-specified transfer loop proved by mexp.run_round), inst.py / litcheck.py (instantiate
  symbolic configs; exact literal pass-through check).

## Proof files (state 2026-10-07 late)
- gen_machine.py: header + ported 8-state lemmas (h8_*) + generated STAGE0, ST2A (phases 1+2 with (D1^5)^u),
  ST2B, hand loop S2L_loop* (p3loop3.X3, 3 units per round), ST2C (+ ST2C_halted). Writes machine_info.pkl.
- abstract.v.in (Kr/Kg, rules, CDP, CLRS, init_reach, R4P, STAGE0_Kr, STAGE2_Kr), arith.v.in (arrow, U_closed,
  bf sealed, bf_closed, tower mod 50 -> bf_mod25), main.v.in (reach_stage2, Theorem halt).
- gen_final.py OUT.v assembles everything; gen_bound.py OUT.v fills bound.v.in (c_halt, ones, score, vs record).
- Dev compile: dev/M.v (machine part, compiled with coqc_dev.py so it is Dev.M), dev/A.v imports it.
- The read of proofs/BB9_record_bound.v was blocked by the permission classifier; the bound template uses the
  names documented in ../bb9_record_1RB0RA_1LI0LC_coq.md (score_closed, Bx_arrow13, Bx, ones, arrow).
