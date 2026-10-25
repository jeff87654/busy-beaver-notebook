# h14verify: independent adversarial check of H14 (Opus verifier, 2026-10-09)

H14 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LN1LL_0LK1LM_1RJ1RM_1RD---

## Method (own tools, this dir)
- stage.cpp/.exe: plain literal TM runner, stops at the next B-form (state H, head right of the word, word ends D0 D(A)),
  at an undefined slot, or at a step cap.  sim.py: Python literal simulator (cross-checks).
- numth.py / ures.py: residues of iter d (U n) A (n1's CLR output) mod a lambda-closed modulus MB = 2^12 3^8 5^2 7^2 11 13;
  checked against exact values.  Huge U outputs = 3*tau(m) - 8 (tau = stable 2-tower) = 40 mod 2520.
- vals.py: affine values over atoms (huge quantities: exact residue mod MB/3^i + magnitude rank).
- absim.py: B-form configurations as token runs with affine counts/values.  At each B-form:
  (1) Coq PERIODS macro when the tape is exactly Per k m n a with m >= 21 and Inv n a (provenance-checked);
  (2) Coq CLR macro when the list ends [c+3d, 1^n | A], d >= 1, n = 0 or A = 1 mod 3 (valid for ANY left side);
  (3) otherwise ONE literal stage to the next B-form, run under 1 + #atoms + 2 representative assignments
      (rep = residue mod MREP + MREP*slot, slots ordered by magnitude rank), outputs fitted as affine forms in the
      atoms; a different shape/kind or a failed fit = NonUniform (stop).
  H14 = n1 on every slot except J0, so the Coq lemmas (proved for n1, which never reads J0 inside them) apply verbatim.
- drive.py: start = Coq HALT_B configuration Bf (FarE k1) [0, 1^w | f] with exact residues:
  k1 = 4JJ-3, JJ = (3T-13)/7, T = 2^^..(arrow 37 2 3) -> k1 = 17 mod 8640 (confirms screener), k1 = 2 mod 3.

## Log
- 20:40 first full eater pass (drive_r1_lin.log, REPMODE=lin, MREP=840): from Bf(FarE k1)[0,1^w|f] with k1, w, f atoms:
  stage 1 (J0 pass) eats 7 D2: 2^(k1-7) 1 4 0^2 z2 1 z4 0 7 1^9 0 (f-1) 1^(w+4) 0 | 4; CLRs + small events;
  stage 11 eats 5 more (2^(k1-12)); stage 16: ONE literal stage converts the whole remaining run
  2^(k1-12) 1 2 (U8+1) 0 1^n | U9  ->  (2k1-21) (U9-k1+16) 1^(n+k1+..) | 4   (uniform in k1; needs U9 > k1, true);
  CLRs clear both tokens; stage 20 = left event H: 2 1^(2U11+5) 0 1^n' | 6; stage 21 = S0:
  CLEAN round-2 start 2 5 1^(2 U11) 0^3 9 1^(n'-2) | 4 (nothing left of the list).  Counter 2*U11 = 4R+4 with
  R = (U11-2)/2, i.e. delta = 1, class 10 mod 14 (U = 40 mod 2520).  Matches the screener's claim.
  No undefined slot read; every literal stage passed the affine-uniformity test.
- 20:20 round 2 via Coq PERIODS macro: Per 1 (2U11-2) n a -> Per ((4U11-13)/7) 8 n14 a15  (J = (U11-5)/7, r = 8: class 10 end).
  Round-2 end (stages 26-44, MREP 840): P1 with m = 8 -> ... -> a short "mini-round" 2^3 5 1^X' ... with counter
  X' = (3 n14 + 2 a15 - 86)/5 -- ACCUMULATOR-sized in reality (a15 >> n14), depth-sized only in the screener's std world.
  It collapses after one period (stage 43: 2^9 (U22+7) 1^(X'+2/3 U20+..)) because its depth (2/3 U20) is >> X'.
- stage 45 NONUNIFORM at MREP 840: the token X = (3 n14 + 2 a15 - 11)/5 has a class mod 5 that needs residues mod 25;
  840 fixes only mod 5.  Atoms carry exact residues mod MB (5^2), so this is a representative problem, not a real
  ambiguity.  Resumed at stage 45 with MREP = 1050 = 2*3*5^2*7 (drive_r2_1050.log).
- stage.cpp sweep accelerator (stage2.exe) verified identical but slower: the quadratic cost is not monotone sweeps.
- 21:00 post-round-2 structure (drive_r2_1050.log, block runs added): iteration i has the decisive literal stage
  P 1 2^10 1^D 0 | A  ->  ... X' 4 1^(X'+e) 0^3 1 0 | 6, X' = (3D + c)/5, branching on D mod 5; the rest of the iteration
  (about 13 stages: CLRs at depth 2..4 on huge arguments, so fresh accumulators U) gives the next decisive length
  D' = (9 D + 10 U + C_r)/15, U a NEW huge accumulator (= phi mod everything).  So in reality D grows each iteration;
  in the screener's std world U-rep = 19 and D shrinks by 3/5 (411, 241, 139, 76, 40, 23, ...) until the list is tiny,
  and the N1 halt at stage 141 comes from that tiny list (tier1/H14_b6_std.log stages 90-141): a REPRESENTATIVE ARTEFACT.
- rtest.py (generic decisive stage, fresh atoms D, A): classes D = 0,1,2,3 mod 5 return to the same form after one
  iteration with C_r = -415, -319, -388, -412; D = 4 mod 5 enters a different path.  None halts.
- fiveadic.py / d8.py: exact 5-adic residues of the real D_1 (from the Coq chain residues): real class sequence
  0, 0, 2, 2, 3, 2, 3, 4  -> iterations 1-7 stay in the known classes, iteration 8 enters the class-4 path.
- rtest_d8.log: class-4 path from the real D_8 residue (MB5=8, MREP=1875): 9 stages, no halt; stage 10 depends on a
  residue (parity-type) of a depth-1 CLR output that MREP=1875 (no factor 2) does not fix -> stopped (time).
- 22:20 lead updates (chain map z -> (3z-r)/5 from tier1; depth class 35 mod 42).
  * geo reps (GROW 4, U rep 4x D rep) reproduce the class-0 iteration exactly: D' = 3/5 D + 2/3 U4 - 83/3 (geo_checks.log).
    Provenance of U4 (exact, no representatives): stage 2 of the iteration gives "... 0 1 7 1^2 0 | 4" (small exact
    tokens), so CLR gives U2 = iter 2 (U 2) 4 = U_2(196600), a 2-tower of height ~65534; then U3 = iter((U2+2)/3)(U 2) 4,
    U4 = iter((U3-1)/3)(U 4) 4, and the inner mini-round deposits 1^(2/3 U4 + 10/3) as the new depth.  So the real next
    depth is >= 2/3 U4, astronomically larger than D.  tier1's map (3z-r)/5 omits this term because its follower
    replaces U4 by 19 (std) or 2539 (big).  The chain never becomes small in reality, so the small-z junk/halt
    endpoints (z = 3, 30, ...) are unreachable; the backward-tree attack does not apply.
  * Depth/k classes mod 7 (coq chain, T = 23 mod 49): JJ = 1 mod 7, k1 = 29 mod 42 (= 1457 mod 2520), round-1 end
    w = 30 mod 42 (my convention: right side z2 D1^(w+1) at J0; follower n = w-1 = 29 mod 42).  The b0 = 6 follower has
    J = 5 periods, k = 17 (3 mod 7) and n = 329 (35 mod 42): WRONG class mod 7, because B = (T-4)/2 = 34 mod 49 while
    b0 = 6 matches B only mod 2520 (J mod 7 needs B mod 49).  n in {329, 371, 2849} are all 35 mod 42 = wrong class.
    My runs use the true classes (atoms exact mod 7^2, reps = residue mod 840/1050) at sizes w ~ 3000-4000 (lin) and
    larger (geo).
- 23:30 geo recheck (GROW 3, ranks spaced x3: k1 ~ 1.5k, w ~ 3k, accs up to ~70k) of every literal stage 1-21 of the
  eater and restart: all SAME as the lin run (geo_checks.log, geo_recheck16.log; stage 16 = whole-run conversion,
  1.3e10 steps).  Stage 23 recheck crashed the runner (650k-cell tape); it is Coq's P4 (q = 0) anyway.
- (next day session) H14 class-4 step resumed. New: reatomize() in absim.py (REATOM=3): any value whose coefficient
  denominators are not 1 or 3 is replaced by a fresh atom with its EXACT residue (MB5=14: residues mod 5^14), values with
  the same coefficient vector share the atom.  Keeps MREP = 2520 while following 5-adic digits exactly.
- rtest_d8b.log: class-4 path from the exact real D_8 residue (mod 2^12 3^8 5^14 7^2 11 13): 12 stages, then
  stage 13 = HALT, state N reads 1 (H14's undefined slot), uniform over all 7 representative assignments.
  Halting stage start: ... (0 z5)^((U7-4)/3) 0 z4 1^2 0 | 196600 (after CLR d=2 n=1 A=4 -> 196600 exact).
- pfx.log: same run with two other prefixes (incl. the screener's '2 91 1 2^6 1 44 48 61 0 26 1'): identical stages and
  identical step counts -> the prefix is never read.
- rtest_d3.log (running): the real chain from the exact D_3 through iterations 3..8 directly (no class map).
- ORDER ERROR FOUND AND FIXED (2026-10-10): my rank rule put every CLR output above all atoms.  The accumulators made
  inside each post-round iteration come from exact small inputs (CLR d=2 n=2 A=4, then depth 2/4) and are FIXED
  constants, far below the round-2-sized D.  ures.iterU now gives such outputs a 'const' tier below all real-run atoms.
  With the fix, every post-round stage gives the SAME affine rewrite (r2end.log stages 1-31; final2.log), so the class
  map and the class sequence are unchanged.  But the earlier claim "D grows" was WRONG: D' = 3/5 D + 2/3 U* + c with U*
  a fixed constant, so D shrinks by 3/5 per iteration toward ~5/3 U* (the screener's shrink picture is right in kind).
  D_8 ~ (3/5)^7 D_1 is still astronomically larger than U*.
- iter_check.py (one iteration from the exact D_i, fresh atoms, generic prefix): iterations 1-7, both size orders,
  D_(i+1) residue mod 5^10 = class-map prediction every time (iters.log, final.log, final2.log).
- Class-4 path from the exact D_8 (both size orders, 3 prefixes): stage 13 = HALT, N reads 1 (final2.log, rtest_d8b.log,
  pfx.log, halt_d8.log).  Other class-4 test residues 9, 14, 24, 104, 229 halt the same way; 19 gave NonUniform (not real).
- 2026-10-10: T residues checked: tau gives T = 65536 mod 88200 (0 mod 8, 7 mod 9, 11 mod 25, 23 mod 49), matching
  the lead's independent value.  Runner renamed to stage_h14.exe (guard against name-based kills by other sessions).
  The class-4 run was NOT lost: final2.log completed normally (class-4 path HALT at stage 13; iterations 3-7 matched).

## C13a (2026-10-10) = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LK0LC_0RL1RM_0RI0RK_1RD---
- Same tools (TM env), start = Coq HALT_B config with exact residues, tiers fixed (k1, w, f ranks 1000-1002).
- c13a_run1.log: eater = 5 stages + CLRs, uniform: round-2 start 2^(k1-4) 1 5 (X4-3) 2 5 1^(f+3) 0^3 9 1^(w+5) | 4
  with X4 = U3 - f/2 and U3 = iter 2 (U (w+7)) 4: a FRESH accumulator at the round-1 depth.  So the prefix digit is
  larger than round 2's counter (f+3, about the round-1 accumulator), not "R-2" as in d13's std picture.
  Round 2: one literal prefix period validated, then PERIODS: -> Per (2/7 f - 17/7) 13 n a (class 1 end, r = 13).
- Round-2 end (stages 21-31): P1/DEP9/P2/P3-like events with m = 7, 1, then a LOOP: each stage moves 3 ones of the depth
  list D = n + 2/3 a + 2/3 U15 + .. into a (2 0 3) block: (U17-3) (2 0 3)^j 2 0 10 1^3 0 1^(D-3j) | 6 (15 identical
  rewrites seen).  Real D is round-2-sized, so this loop is astronomically long; added a LOOP macro to drive.py (3
  consecutive literal outputs with identical shape and constant integer deltas -> jump J, exact remainder kept).
- Rerun (c13a.log) with TRUSTPREFIX (the literal prefix period of run 1) and per-stage pickles.
- C13a RESULT (c13a_r3.log): after the loop macro, stage 61 converts the (2 0 3) run into far blocks
  (0 1^4 0 9 z2 0^6 z2 0^3 z4 4 9)^X16 plus a mini-round '2 5 1^(2/5 U13 - 3)'; CLRs on constant-tier values (U14, U17,
  U18); stage 67 = HALT, M reads 1.  Halting stage re-run under the U17/U18 orders and geo spacing: halts each time
  (c13a_orders.log).  Geo recheck of eater + end stages consistent (c13a_geo*.log; stage 61 too big for geo).
  Verdict: C13a HALTS, strong evidence; sigma in the f_(omega+1)^2 class at 13 states.  REPORT.md has the section.
- RANK AUDIT (2026-10-10): RANKMODE=min added (real-tier CLR output just above its own inputs).  H14: re-ran stages
  8, 16, 29, 45 with the true order (rr.log, rr2.log): identical rewrites -> no affected stages.  C13a: eater stage 5
  changes when U3 < f/2 (true): far run not eaten, gap 2f-4U3, round-2 counter 2U3-1 (class 9) -> C13a halt verdict
  RETRACTED, status open; checkpoint c13a_min_geo.pkl.
- C13a TRUE ORDER (c13a_true.log, c13a_true2.log; RANKMODE=min, SIGNCHECK with targeted slot scaling, REATOM also for
  mixed-sign values):
  round 2: start 2 5 1^(2U3-1) 0^3 9 1^(w+5) | 4 (U3 = iter 2 (U (w+7)) 4), debris 2^k1 1 6 z2 0 z(2f-4U3-18) on the left;
  1 literal prefix period (validated), PERIODS J = (U3-19)/7, end Per((4U3-13)/7, 7, n, a) = class 9 = n1's standard
  end; ENDGAME-like stages 31-35 -> FarE(k2-6) + [0, 1^(n+2/3 a) | U20] = the round-1-end shape behind the debris.
  Eater pass 2 (stages 36-41) = pass 1 rewrite for rewrite (sign stage resolved with U20 scaled x7):
  round 3 start 2 5 1^(2U21-1) 0^3 9 1^(n'') | 4 behind debris block 2.  -> clean-round looper, debris never read.
- C13a continued: round 3 prefix validated (2 debris blocks), PERIODS J=(U21-12)/7, class-9 end; eater pass 3 = pass 2
  (sign stage U34 vs U33/2 scaled x7); round 4 start 2 5 1^(2U34-1) 0^3 9 1^n | 4 behind 3 debris blocks.  Stopped
  there; checkpoint c13a_true_r4.pkl.  VERDICT: C13a non-halting clean-round looper (strong evidence).
