# Coq proof of T12a (scratch notes, resume here)

Agent: Opus inv-t12a-coq, 2026-10-09/10. Work stopped early (see "Status").

## Infrastructure (done, tested)
- proofs/BB122.v, proofs/Individual122.v: 12-state setup (states A..L). State L shadows busycoq's direction L,
  so tables write directions as TM.L / TM.R. Tested: eq_refl table checks and a step lemma compile, closed.
- proofs/check.py: extended to states A..P, accepts `TM.L`/`TM.R` in tables, probe emits TM.<dir> for n >= 12.
  (Diff vs the original is 9 lines; file kept LF.)
- Generators copied from bb10_n1_coq; common.py/lit.py/planner8.py/coqgen_util.py switched to T12a / 12 states.
  gen_base.py -> dev/Base.v (PASS, PRO, R2M) compiles in 11 s.

## Analysis tools (ana/)
- bsim.py / macro2.py: B-form macro simulator (literal events, CLR jumps with representative accumulators).
  `python macro2.py K W F` starts at Bf (FarE K) (1^W ++ [0]) F (n1's round-1 end).
- view.py: full-word token view with zero gaps (zN). reach.py: how far left each event reads.
- vary.py / vary2.py: dependency of event outputs on each CLR representative. eat.py: the round-2-end eat event.

## Event chain (w=36, k=17, all accumulators 40; full list from `python full.py 17 36 40 ev.pkl`)
Restart (all events read only the right end of the far region, except R1END which consumes 6 D2s, E004 one D2):
- R1END: [2^(k) 1 6 z2 0 z5 1 0^3 z2 0 z2 0 z2 0 z2 0 z2 0 1^w 0 | f] -> [2^(k-6) 1 5 z5 0 z5 0 z5 0 z5 1 0 5 1^3 0 (f-1) 1^(w+4) 0 | 4]
- E000..E004 deposit A+c tokens (CLR to residues); E005 turns token A+3 into (0 z5)^x junk (x ~ A/3);
  E006-E010 deposits; E011 eats the junk into the counter: [.. | 1^z | a] -> [.. 3 (a+5) 1^c 0 1^(z-1) | 6];
  E012 (S0-like) -> [Far72 3 P 2 5 1^c2 0^3 9 1^z' | 4], round 2 = n1's P4(q=0), then periods (P1,R2,P2,P3,R2,P4)
  with left context Far72 + D3 D(P). Far72 = 2^(k-7) 1 8 z2. c2 = (2A-23)/3 (A = accumulator before E004).
- Round-2 end from Per L k 3 n a: E020 -> [.. 2^2 0 a 1^3 0 1^n | 6]; CONV0 (a -> a-7 2 0 10), CONV x n
  ([.. 10 1^3 0 1^(z+1)|6] -> [.. 3 2 0 10 1^3 0 1^z|6]), Z0, Z1, CLR -> [.. 2 2 0 X 2 0 (3 2 0)^(m-1) 1^4 | A], m = n+1.
- EAT: left sweep eating 2 blocks per round (constant cost), then into X, P (P -> (0 z5)^x junk) and 4 D2s of the far.
  Outcome periodic in m mod 6 (m >= 8), independent of X and A:
  m=2,3: [.. 2 4 0 A 1^3 0 1^3 | 6]; m=4,5: [.. 10 1^5 0 2 0 (A+3) 0 1^3 | 6]; m=0,1: [.. 4 9 0 1^6 2 1^2 0^3 1 2 (A+3) 0 1^3 | 6].
  All three classes reach HALT L1 within 2-3 more events (checked m = 14..19).
- No counterexample to the screening found: every check agrees with the verifier's report.

## Next steps
1. Write event specs (start/target in shapes) for R1END, E000-E012, E020, CONV0, CONV, Z0, Z1, EAT (6 cases m mod 6,
   with the block run in 6-block units), the three continuations and the halt; validate literally, then mexp.
2. Regenerate P1-P4 with a variable far side (far = V('l')).
3. Arithmetic: c2 = 5 mod 14 from A mod 42 (towers: 2 mod 7, even); restart CLR residues from r1.
4. Bound file via bound.v.in.


## Progress 2026-10-10 (resumed with the user's approval)
- Specs: evs12.py (plain n1 style: shapes helpers W/tok/ONES/TWOS/T3, far side = V('l')). Restart events R1END, E0-E8,
  E10-E12 (E9 is n1's R2), and LP1-LP4 = n1's P1-P4 with a variable far side. Accumulators and depths are shifted
  (a+4, w+2, ...) so that mexp's v = 0 branches stay generic (small values read further left: R1END needs f >= 4).
  Validate: `python drv12.py NAME lit explore` (all OK).
- gen_machine12.py -> dev/M.v (805 KB, 981 lemmas, compile 345 s at Idle).
- gen_wrap.py: B-form wrappers W_x (Bf side ts A, side = raw cells after the first gap). wrappers.v.in.
- mk_a2.py: abstract2_12.v.in (events, P1-P4 for any L, FarP L) + round1_12.v.in (n1's main.v.in with Per L, PERIOD L,
  PERIODS L r, ENDGAME/reach_end also giving r1 f, 4 <= f, 13 <= k). arith12.v.in: iterU, arrow_mod7, acc_form.
- mkA12.sh -> dev/A.v (compile 170 s). restart.v.in (mkR.sh -> dev/R.v, imports Dev.A, 6 s): CLR4, Bf_snoc, FarR,
  FarE_7, `restart` (round-1 end -> Per (lfr [p;3] (FarR k)) 1 (14 J + 3) n a), `reach_round2_end`
  (c0 -->* Per (lfr [p;3] (FarR k)) (4 J + 1) 3 n a, Inv, 6 <= k, W1 <= w, F w <= 7J+9, F^(2J)(w) <= n). ALL CLOSED.
- c2 = 5 mod 14 comes from acc_form: the accumulator before E4 is 4 + 3 x4 with (x4 + 4) mod 7 = 2 (a tower).
- Pitfalls met: a failing `follow` takes ~4 min (unifier) -> check depths by hand first (ones count after each event);
  `follow (Lem _ ...)` with a hole for the first argument fails -> use `follow (fun L => Lem L ...)`; destruct every
  CLR4 output before `exists`; `replace k0 with ..` also rewrites the goal (use rewrite .. in H).
- check.py on proofs/BB10_n1.v after the 12-state change: PASS (10 states, backward compatible).
- Held (lead): round-2-end halting events, until the true-order test (t12a_verify/tdrive_t12a.log) reports.

## 2026-10-10: output blocked again
After the lead lifted the hold on the round-2-end events, my next response was stopped by a safety classifier.
Per the lead's instruction I did not reword around it: work stopped there and the lead was messaged.
State at the stop: everything listed under "Progress 2026-10-10" compiles; the round-2-end events
(E20, CONV0/CONV, Z0/Z1, EAT x 6, continuations, halt) have no specs yet.

## 2026-10-10: output blocked a third time
After the lead re-confirmed the lifted hold, my next response was stopped by a safety classifier again.
Per instructions, no rewording: work stopped and the lead was messaged. State unchanged (reach_round2_end compiles; no round-2-end specs).

## 2026-10-10 (inv-t12a-end, Opus): round-2 end specs, machine lemmas, abstract chain
- Specs: evs_end.py (EVE), written as view strings with vspec.py ('L 2^{K} 1 T{24,x} ... [UNIT]^{j} ...';
  T{c,v} = D(c+v), T3/T9 = D(c+3v)/D(c+9v), m^{v} = token run, [view]^{v} = raw cell run). Validate with
  `python drv_end.py NAME lit explore` (lit = fast word compare via probe.py/bsim, random values 0..6).
  Events (all validated literally AND explored): E20, CONV0, CONV, Z0, Z1, EAT0..EAT5 (blocks = r + 6 + 6 j),
  SM3 (3-block eat of classes 0/1), F23 (A24+3 = 43+9y -> y junk units), F24, G1, G2, G3, HALT1, HALT2 (L reads 1).
- Event outputs (left-to-right, | A = B-form accumulator):
  classes 0,1 -> [.. 2 4 0 A24 1^3 0 1^3 | 6] -> CONVERT (n=2) -> SM3 -> F23 -> F24 -> CLR(d=2,n=3) -> HALT1
  classes 2,3 -> [.. 10 1^5 0 2 0 (A24+3) 0 1^3 | 6] -> F23 -> F24 -> CLR -> HALT1
  classes 4,5 -> [.. 4 9 0 1^6 2 1^2 0^3 1 2 (A24+3) 0 1^3 | 6] -> G1 -> CLR(d=2, n=2a+6) -> G2 -> G3 -> CLR(d=2) -> HALT2
  A24 = iter 3 (U 3) 4 = 40 + 9y (acc9: clearing outputs from 4 are 4 mod 9, since towers of 2 are 1 mod 3).
- mexp.py local changes (mexp_orig.py = before): (1) MAXLEN (max inserted gap in the loop matcher) is a module
  variable, drivers set 200: the EAT junk unit is 78 cells and with the old 64 the matcher split it into two stacks
  (26 + 52 cells), whose final right sweep then had no loop; (2) rotated single-gap insertion variants (ROTATE).
- gen_machine_end.py -> dev/M2a.v (small events + halts, 279 KB, compile 304 s) and dev/M2b.v (EATs, 1.47 MB).
- gen_wrap_end.py -> wrappers_end.v.in; mk_end.py fills end_head/eat/tail.v.in -> end.v.in; end_main.v.in = theorem.
  mkE.sh -> dev/E.v (imports M M2a M2b A R). mkE1.py -> dev/E1.v = everything except the EATs: COMPILES (7 s).
- Final assembly: gen_final12.py -> final/BB12_T12a.v (2.64 MB; machine part regenerated in one run: gen_machine12
  with the original mexp settings (MAXLEN 64, ROTATE off; identical lemmas to dev/M.v up to fresh names), then
  gen_machine_end with MAXLEN 200; one crossing-lemma set). Then copy to proofs/ and run check.py there.
- Bound: bound12.v.in + gen_bound12.py SRC OUT (fills EV_HALT1/2 end configurations, EAT*_ones). Counting via
  side_ones (a side = finite list with >= N ones; so_tac). Results: sigma_lower_bound (F^(2J)(w) <= 6N+10,
  F w <= 7J+9, w >= F^(2JJ+1)(34)), score_ge_exact (F(F Wf) <= 6N+10, round 1 tracked exactly with the ported
  BB10_n1_exact lemmas), beats_n1 (N > BB10_n1_exact.score_value + 1; agreement lemmas arrow_n1/step_n1/JJ_n1).
- 2026-10-10 11:xx: dev/E.v (everything on top of M, M2a, M2b, A, R) COMPILES, `Print Assumptions halt` closed.
  (M2b = the six EAT lemma sets took 8603 s at Idle.) Bug fixed on the way: END_PER needs 6 <= n (blocks S n >= 7).
- Bound test dev/B.v (= final/BB12_T12a_bound.v with the import switched to Dev.*) COMPILES in 312 s;
  sigma_lower_bound, score_ge_exact, beats_n1 all closed.  Pitfall: never `rewrite` an equation between the two
  arrow definitions (BB10_n1.arrow vs ours) in a goal with huge closed arguments -- the matcher unfolds and hangs.
  Compare closed forms as a function vf of (stepn, arrow, JJ) and use vf_ext on abstract arguments.
- proofs/BB12_T12a.v (copy of final/) compiling at Idle with coqc_dev.py (started 10:41, expect ~3 h); afterwards
  run `python check.py BB12_T12a.v` in proofs/ (the .vo is then up to date, so check.py only runs its probe), and
  compile proofs/BB12_T12a_bound.v.

## Status 2026-10-10 15:50 (done)
- proofs/BB12_T12a.v: check.py PASS (no axioms). Compile 5 h at Idle under load; check.py afterwards 4 min.
- proofs/BB12_T12a_bound.v: compiled 967 s; sigma_lower_bound, score_ge_exact, beats_n1 closed.
- Report: ../bb12_t12a_coq.md. Probe: probe_bound.v / probe_bound.log.
- If the end specs are ever regenerated: gen_machine_end.py (MAXLEN 200), gen_wrap_end.py > wrappers_end.v.in,
  mk_end.py, then gen_final12.py and gen_bound12.py SRC OUT.
