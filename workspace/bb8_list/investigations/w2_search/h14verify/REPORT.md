# H14 independent verification: REPORT (Opus verifier, 2026-10-09/10)

H14 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LN1LL_0LK1LM_1RJ1RM_1RD---

## FINAL VERDICT (2026-10-10): H14 HALTS (at N1), STRONG EVIDENCE (not proved on paper)
The halt does NOT happen where the screener said (stage 141 of the std world, after the chain shrinks to small z).
It happens at the 8th post-round-2 chain iteration, while the chain's list length D is still astronomically large.

| step | rule | level |
|---|---|---|
| round 1 to n1's J0 read | Coq (H14 = n1 except J0) | proved |
| eater + restart | clean start 2 5 1^(2U) 0^3 9 1^n, counter 4R+4, class 10 | strong (sample-checked parametrised stages, two rep spacings) |
| round 2 | Coq PERIODS, Per 1 (2U-2) n a -> Per ((4U-13)/7) 8 n14 a15 | proved given the start |
| round-2 end to 1st decisive form | about 20 literal stages + CLRs | strong |
| chain iterations 1-7 | D' = (9D + 10U* + C_r)/15, r = D mod 5, C_0..3 = -415, -319, -388, -412 | strong; every iteration checked with exact residues |
| iteration 8 (D_8 = 4 mod 5) | class-4 path, 12 stages, then N reads 1 = HALT | strong; uniform, prefix-independent |

Real class sequence (exact 5-adic residues of tower values): D_1..D_8 mod 5 = 0, 0, 2, 2, 3, 2, 3, 4.
- D_1 = (9 n14 + 6 a15 + 10 U* - 418)/15, with n14, a15 the depth and accumulator after round 2. It is round-2-sized.
- U* is a FIXED constant, the same in every iteration: CLR d=2 n=2 A=4, then depth-2/4 CLRs from those constants.
  It is 40 mod 2520, like every tall tower.
- So D shrinks by 3/5 per iteration toward about 5/3 U*. D_8 ~ (3/5)^7 D_1 is still far above U*.
- Halting stage (generic prefix P, never read):
  P 2^2 1 5 (z5 0)^((X2+2)/3) z5 2 (X4-6) 2 3 2 1 2^3 1 2 .. (z2 0^4 z4 2 z2 0)^(X8-4) z2 0^4 z4 2 z2 0^12 z2 (0 z5)^3 5 z4
  (0 z5)^((U7-4)/3) 0 z4 1^2 0 | 196600.
  - Here X2 = 3/5 D_8 + A_8 + 3/5, X3 = 3/5 D_8 + 3/5, X4 = (3 X3 + 1)/5, X8 = (U6 + 5)/9. U5, U6 and U7 are fixed
    constants (CLR d=7 n=1 A=4, ...).
  - The run reads N1 after about 5.9e6 steps plus terms affine in the constants.
- Deciding residues: D_8 = 4 mod 5. The path's reatomized values use D_8 mod 5^3, and D_8 mod 5^14 is known exactly.
  Other class-4 test values (9, 14, 24, 104, 229) halt the same way. Residue 19 gave a NonUniform stage, unresolved, but
  it is not the real class.
- Ones at halt: (real prefix: everything round 2 left) + 5/3 U7 + 8 X8 + 3 X4 + X2/3 + 196607 >= A_8/3.
  A_8 is the iteration-8 accumulator, a CLR output at a depth of D size.
- sigma ~ f_omega(D_8) with D_8 ~ (2/5)(3/5)^7 a15 and a15 >= f_(omega+1)(f_(omega+1)(~2^^363)).
  So sigma is in the f_(omega+1)^2 class. That beats an f_(omega+1)-class BB(14) champion, so H14 is a BB(14) record
  CANDIDATE that still needs a proof.

Remaining weak points (why this is not proved on paper):
1. Every non-Coq stage is an affine rewrite fitted on 6-9 representative assignments. It is not a symbolic proof.
2. Iterations 3-8 were run from a generic prefix. Prefix-independence was checked at iteration 8 with three prefixes,
   which gave identical step counts.
3. Size order: checked in two orders, "U* above D" (wrong) and "U* far below D" (right, constant tier). Both give
   identical rewrites, so the stages do not depend on that order.

### CORRECTION of my earlier reports (2026-10-09)
- I said "D grows each iteration (2/3 U is a fresh huge accumulator)". That was WRONG. My rank rule wrongly put
  constant-derived CLR outputs above D. U* is a fixed constant, and D shrinks by 3/5, as tier1 said.
- What remains true: tier1's halt mechanism (z shrinking to small values, junk at z = 3/30) is not what happens.
  - The real chain reaches class 4 at iteration 8, astronomically early compared with the ~log_(5/3)(D_1/U*) iterations
    needed to get small.
  - The halt comes from the class-4 branch at huge D, not from the small-z endpoints.
- The class-4 halt result itself was obtained first under the wrong order and then confirmed under the corrected one.
- The depth/k class mod 7 finding stands: the b0 = 6 follower uses k1 = 17 (3 mod 7) and n = 329 (35 mod 42). The real
  values are k1 = 29 mod 42 and n = 29 mod 42 in the follower's convention.

### Coq route (sketch)
- Reusable from proofs/BB10_n1*.v: CLR, R1/R2, the event lemmas H, S0, P1-P4, E, and PERIODS (for round 2).
- New symbolic lemmas needed (mexp/evs.py workflow, H14 table):
  - the eater: about 8 stage rules affine in k1, w, f and U atoms, including the whole-run conversion stage;
  - the restart S0 variant;
  - the round-2 end: about 12 stage rules;
  - the 4 class iterations: about 14 stages each, most shared;
  - the class-4 path: 13 stages.
- Plus residue lemmas: tower residues mod 5^9 * 3 * 2^3 * 7 to fix D_1..D_8 mod 5.
- The prefix-independence holds automatically if each lemma is stated with an arbitrary left side.

## Rank audit (2026-10-10, after the T12a verifier's flag)
The corrected rule "a real-tier CLR output ranks above every existing real atom" is wrong for small-d CLRs:
iter d (U n) 4 with small d (2, 3) at a huge depth is far SMALLER than an earlier CLR output with a huge d. I audited
every real-tier pair that a stage reads, re-ran the stage under the true order, and added RANKMODE=min to ures.py:
an output ranks just above its own inputs.

**H14: no affected stages.** These were the mismatched pairs read by a stage; each was re-run in the true order:

| stage | pair (true order) | result |
|---|---|---|
| 8 (eater) | U5 = U_(w+1)^3(4) < f < U3 < U4 | identical rewrite (geo) |
| 16 (whole-run conversion) | U9 = U_n^3(4) < U8 | identical; its output U9 - k1 + 16 is positive since U9 >> k1 |
| 23 | U12 (d = 3) < U11 | Coq P4, holds for any values |
| 29 (round-2 end) | U16 = U_(n14-1)^3(4) < a15 | identical (geo) |
| 45 (first decisive) | U23 < U17 | identical (compact, true order) |

- The only H14 output with a negative coefficient is U9 - k1 + 16. It is positive in reality.
- Iterations and the class-4 path use only constant-tier atoms. Those are ranked above their own inputs, and their true
  order there is correct: U7 = iter 3 (U 1) 4 < U5 = iter 7 (U 1) 4 < U6.
- **The H14 verdict (halts at N1, strong evidence) stands.**

**C13a: AFFECTED at eater stage 5.**
- My first run ranked U3 = iter 2 (U (w+7)) 4 above f, the round-1 accumulator. In reality f >> U3, because f
  iterates a CLR at a similar depth a huge number of times.
- With the true order (RANKMODE=min, geo GROW 4, so U3 < f/2): stage 5 gives
  2^k1 1 6 z2 0 z(2f - 4U3 - 17) 2 1^(2U3+4) 0 1^(w+7) | 6 and then 2 5 1^(2U3-1) 0^3 9 1^(w+5) | 4.
  - The far D2 run is NOT eaten. A gap of 2f - 4U3 opens.
  - Round 2's counter is 2U3 - 1, which is 79 mod 2520: class 9, n1's standard J0 end. It is not f + 3 (class 1).
- The old output "U3 - f/2" would be negative in reality. My first C13a trajectory (round 2 with counter f+3, the
  (2 0 3) loop, M1 at stage 67) is therefore not the real one. **The C13a halt verdict is retracted.**
- The real continuation, round 2 with the far region and the gap still on the left and then a second J0 eater pass, was
  not followed (time).
- Checkpoint: c13a_min_geo.pkl (stage-9 config, true order); logs c13a_min_geo.log and c13a_min_geo2.log.

### C13a FINAL (2026-10-10, true order): DOES NOT HALT along its trajectory -- clean-round looper, STRONG EVIDENCE
Run: c13a_true.log and c13a_true2.log. Settings: RANKMODE=min (a CLR output ranks just above its own inputs); a sign
check that re-runs any stage producing a mixed-sign value with the dominant atom scaled up; re-atomization of
mixed-sign values; exact residues mod 5^14.
- **Round 1** is n1's (Coq). **Eater pass 1**, with the true order f >> U3 = iter 2 (U (w+7)) 4: the far run 2^k1 is
  NOT eaten, and a gap of 2f - 4U3 - 18 opens.
- **Round 2**: start 2 5 1^(2U3-1) 0^3 9 1^(w+5) | 4.
  - The counter 2U3 - 1 is 79 mod 2520, class 9. U3 ~ U_(w+7)(U_(w+7)(4)): a fresh f_omega-level value at the round-1
    depth. It is far above the depth w but far below the round-1 accumulator f.
  - The round is a full f_(omega+1) round: one literal period with the debris prefix, then Coq PERIODS with
    J = (U3-19)/7 periods. It ends at Per((4U3-13)/7, 7, n, a), n1's standard class-9 end.
  - The end produces FarE(k2-6) + [0, 1^(n+2/3 a) | U20], exactly round 1's end shape, behind the round-1 debris
    2^k1 1 6 z2 0 z(gap1).
- **Eater pass 2** (stages 36-41) repeats pass 1 rewrite for rewrite, including the sign-dependent stage
  (U21 vs U20/2, resolved with U20 scaled x7). The debris is never read.
- **Round 3**: start 2 5 1^(2U21-1) 0^3 9 1^n'' | 4, class 9 again, behind two debris blocks.
- **Induction.** Every round ends in class 9 (the counter is 2U - 1 with U = 40 mod 2520), so every round end is n1's
  FarE form. Every eater pass then reproduces the same rewrite and builds a new class-9 round with a fresh counter
  2U - 1. M1 is never read. So C13a runs through infinitely many full f_(omega+1) rounds and never halts on this
  route. Number of full rounds before a halt: none (no halt).
- **Followed to the start of round 4.**
  - Round 3: its literal prefix period was validated with two debris blocks, then Coq PERIODS: J = (U21-12)/7,
    class-9 end.
  - Eater pass 3 repeated pass 2 rewrite for rewrite, including the sign stage (U34 vs U33/2, U33 scaled x7).
  - Round 4 starts as 2 5 1^(2U34-1) 0^3 9 1^n | 4 behind three debris blocks.
  - No undefined slot was read anywhere. Checkpoint: c13a_true_r4.pkl.
- **Evidence level: strong for non-halting.**
  - Proved parts: the rounds are Coq PERIODS (prefix-validated literally each time).
  - Sampled parts: the eater stages are affine rewrites, and passes 1-3 were checked literally with 0, 1 and 2 debris
    blocks present.
  - The induction step (an eater pass never reads the debris, and every round ends in class 9) is supported by three
    repetitions, not proved symbolically.
- **sigma: none.** C13a does not halt, so it is not a BB(13) candidate. Each round's counter 2U - 1 comes from a
  two-fold clearing at the previous depth, so the rounds grow at f_(omega+1) rate forever.

### C13a (2026-10-10): HALT VERDICT RETRACTED by the rank audit below -- status OPEN
(The analysis below was run with a wrong size order at eater stage 5 and is kept only for the record.)
### C13a first analysis (superseded): "HALTS at M1" 
C13a = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LK0LC_0RL1RM_0RI0RK_1RD--- (M1 = halt)
Method: as for H14, with exact residues (MB with 5^14), the corrected magnitude tiers (constant-derived CLR outputs
far below all real-run values), re-atomization, plus a LOOP macro (3 consecutive identical literal rewrites with
constant deltas -> symbolic jump; the remainder is kept exact). Logs: c13a_run1.log, c13a_run2.log, c13a_r3.log.
Trajectory: c13a_traj_final.pkl.

| step | result | level |
|---|---|---|
| round 1 | Coq (C13a = n1 except J0) | proved |
| eater (5 literal stages) | round-2 start 2^(k1-4) 1 5 (X4-3) 2 5 1^(f+3) 0^3 9 1^(w+5) 0 4 | strong |
| round 2 | 1 literal period with the prefix (validated), then Coq PERIODS -> Per (2/7 f - 17/7) 13 n a | proved given the start and prefix check |
| round-2 end | P-events with m = 7, 1, then the (2 0 3) loop: one block per stage, D ~ n + 2/3 a + 2/3 U11 times (LOOP macro, ~30 identical rewrites seen) | strong |
| after the loop | far pattern (0 1^4 0 9 z2 0^6 z2 0^3 z4 4 9)^X16 (X16 ~ D/6) and a mini-round 2 5 1^(2/5 U13 - 3), CLRs | strong |
| halt | stage 67: from ... (0 z5)^((U17-1)/3) 0 z4 1^(2/3 U14 + 22/3) 0 \| U18, the run reads M1 | strong; uniform in all 11-12 representatives, both orders of U17/U18, geo spacing |

Size-order answers to the lead's questions:
- **Prefix digit.** It is X4 - 3 = U3 - f/2 - 3, with U3 = iter 2 (U (w+7)) 4. That is a FRESH accumulator at the
  round-1 depth, so it is larger than round 2's counter f+3 (about the round-1 accumulator). It is not "R-2" with R
  the old accumulator. d13's std picture had the order reversed. The prefix is never read in round 2.
- **List versus far region.** The list next to the far region at the end is 1^(2/3 U14 + ..), with U14 = iter 3 (U 3) 4,
  a FIXED constant built from small exact inputs. The far region (X16 blocks) is round-2-depth-sized. So the real order
  is list << far region, the same order as d13's std run (1^31 next to 6.6k far bits). bigend.py's U = 2539 inflates
  the constant above the depth and is the unrealistic case.
- **Residues used.** The real k1 = 29 mod 42 and the real depth class (exact residues from the Coq chain) are used
  throughout. The halt stage involves only constant-tier atoms (U14, U17, U18) plus inert real-tier prefix values.

Ones at halt >= 3 X15 + 44 X16 + ... >= (6/5) U13. U13 is a CLR output at a depth of about a (round 2's accumulator).
So sigma ~ f_omega(a), with a >= f_(omega+1)(f/7) and f >= n1's accumulator. **sigma is in the f_(omega+1)^2 class
with 13 STATES.** If confirmed, that is a Tier-1 result at 13 states, beating the f_(omega+1)-class BB(13+) champions.

Recheck with wide geometric spacing (GROW 3; c13a_geo.log, c13a_geo2.log):
- Eater stages 1-8 give the same rewrites. Stage 6 differs only by re-atomization naming.
- Loop-exit stages 55-59 and stages 62-65 give the same rewrites. Stage 62 again differs only by naming.
- Halting stage 67: M reads 1 again.
- Stage 61 (the far-pattern conversion) exceeded 1e11 steps on the 14M-cell geo tape. It is checked only in the
  compact spacing (11 trials, uniform).

Weak points (same kind as H14): every non-Coq stage is an affine rewrite sampled on 6-12 representative assignments,
not a symbolic proof. The two macro extrapolations each rest on sampled uniformity: the prefix PERIOD (one literal
period) and the LOOP jump (about 30 identical rewrites). d13's withdrawal (bigend, U = 2539, no halt through stage
29) is explained by the inflated constants: in that world the constant-derived list exceeds the depth-sized structures.

## (Superseded first-pass write-up, kept for the record)
## Verdict
**The halting claim is NOT supported, and the screener's evidence for it is a representative artefact. H14's halting
is OPEN.** Claims 1-3 (round 1, eater, clean restart with delta = 1, full round 2) are confirmed (strong evidence).
Claim 4 (halt at N1 after a messy phase) fails as evidence:
- The real post-round-2 phase is a chain of iterations. Each iteration makes a fresh huge accumulator U.
- The next list length is D' = (9D + 10U + C_r)/15, so D grows every iteration.
- The screener's std world keeps U at 19. There D shrinks by 3/5 per iteration (411, 241, 139, 76, 40, 23, ...), and the
  N1 halt fires once the list is tiny. That never happens in the real run.
- The real chain branches on D mod 5. Its class sequence, computed from exact residues, is 0,0,2,2,3,2,3,4.
- Iterations 1-7 stay in classes whose rule returns to the same form. None of them halts.
- Iteration 8 enters the class-4 path. I followed it for 9 stages without a halt, then stopped for lack of time. It needs
  representatives that also fix residues mod 8.

Evidence level by step:

| step | result | level |
|---|---|---|
| round 1 up to n1's J0 read | Coq (H14 = n1 except J0) | proved |
| eater + restart | clean start, counter 2U = 4R+4, class 10 | strong evidence (sample-checked parametrised stages) |
| round 2 | Coq PERIODS macro, J = (U-5)/7 periods | proved given the clean start |
| round-2 end -> N1 halt | not reproduced; real dynamics differ | claim refuted as evidence; halting open |

## Method (all tools mine, in this dir)
- stage.exe (C++): plain literal runner to the next B-form (n1's Coq B-form: state H right of the word, word ends D0 D(A)).
  It is cross-checked against sim.py (Python) and against an independent sweep-accelerated build.
- absim.py: tapes are token runs whose values are affine in "atoms". An atom is a huge quantity known by its exact residue
  mod a lambda-closed modulus and by a magnitude rank.
  - The Coq macros CLR and PERIODS are applied symbolically, with exact residues from numth.py and ures.py.
  - CLR holds for any left side. H14 equals n1 on every slot except J0, so n1's lemmas transfer verbatim.
  - Every other stage runs literally under 1 + #atoms + 2 representative assignments, ordered by rank (the true order
    k << depth << accumulator) and congruent to the residues mod MREP.
  - Outputs must have the same shape in every trial and an exact affine fit; otherwise the stage is flagged NonUniform.
- drive.py starts from the Coq HALT_B configuration Bf (FarE k1) [0, 1^w | f] with exact residues.
  - k1 = 4JJ-3, JJ = (3T-13)/7, T = arrow 37 2 3.
  - This gives k1 = 17 mod 8640 (confirms the screener) and k1 = 2 mod 3.
  - Every huge U output is 3*tau-8 (stable 2-tower), 40 mod 2520.

## Event rules found (k1, w, f, U_i, n, a atoms; all literal stages uniform)
1. **Eater, from Bf(FarE k1)[0, 1^w | f]** (drive_r1_lin.log stages 1-19).
   - The first J0 pass eats 7 D2: 2^(k1-7) 1 4 0^2 z2 1 z4 0 7 1^9 0 (f-1) 1^(w+4) 0 | 4.
   - CLRs and small events follow. A second pass eats 5 more D2.
   - Then ONE stage converts the whole remaining run: 2^(k1-12) 1 2 (U8+1) 0 1^n | U9 -> (2k1-21) (U9-k1+16) 1^(n+k1+..) | 4.
     This needs U9 > k1, which holds in reality. CLR clears both tokens.
   - So the eater is not periodic in k. It is affine in k1, sampled at the real residue class with k1 << depth << acc.
   - No undefined slot is read and N1 is never reached.
2. **Restart** (stages 20-24).
   - Left event H: 2 1^(2U11+5) 0 1^n' | 6. Then S0 gives 2 5 1^(2U11) 0^3 9 1^(n'-2) | 4, with nothing left of the list.
   - The counter is 2U11 = 4R+4 with R = (U11-2)/2, so delta = 1 and the class is 10 mod 14. The depth is
     n' = 7/3 k1 + w + 2/3 U4 + 2/3 U8 - 6 at the Per form.
3. **Round 2** (Coq PERIODS): Per 1 (2U11-2) n U13 -> Per ((4U11-13)/7) 8 n14 a15 (r = 8).
4. **Round-2 end**.
   - P1 with m = 8 starts a short "mini-round" whose counter is (3n14 + 2a15 - 86)/5. That is ACCUMULATOR-sized in
     reality; the screener's std world makes it depth-sized.
   - The mini-round collapses after one period, because its new depth 2/3 U20 is larger than its counter.
   - Then the chain of iterations follows. Decisive stage: P 1 2^10 1^D 0 | A -> ... X' 4 1^(X'+e_r) 0^3 1 0 | 6, with
     X' = (3D + c_r)/5 for class r = D mod 5.
   - After about 13 more stages, with CLRs at depth 2..4 on huge arguments: D' = (9D + 10U + C_r)/15, with
     C_0..C_3 = -415, -319, -388, -412.
   - Class 4 enters a different path (rtest_d8.log), not resolved.
   - The real D_1 = 3/5 n14 + 2/5 a15 + 2/3 U20 - 418/15 has exact 5-adic residues (fiveadic.py, d8.py), giving classes
     0,0,2,2,3,2,3,4.

## Discrepancies with the screener
- The eater does not chip away periodically. After 12 D2's, a single stage converts the rest.
- The restart and round 2 are as claimed.
- The "depth-derived mini-round counters" (419, 249, 147, ...) and the stage-141 halt are std-world artefacts of U = 19.
  - The real counters carry 2/5 or 2/3 of a fresh accumulator each iteration.
  - val2.py's sweeps over c and z all keep U at 19, so they never tested this.
- The real outcome depends on 5-adic digits of tower residues. It must be followed with exact residues, not with
  representatives.

## sigma (only if a halt is later established)
- Round 2 alone gives sigma >~ f_(omega+1)(f_(omega+1)(~2^^363)), as the screener estimated. That beats an
  f_(omega+1)-class BB(14) champion.
- The post-round iterations add at least 8 more f_omega-level steps but do not change the class.
- If H14 never halts, it scores nothing.

## Next steps (for whoever continues)
1. Re-run rtest.py from the real D_8 residue with MREP = 2^3*3*5^4*7 (slow: ~10 min per stage) or with a smarter rep
   scheme. Follow the class-4 path to a halt or to a return to the decisive form.
2. If class 4 returns to the decisive form, extend the class map. If every branch returns, H14 runs forever by
   induction (no N1 read).
3. Re-check the uniform stages with REPMODE=geo (wider rank spacing). recheck.py is ready; traj_r1_840.pkl and
   traj_r2_1050.pkl hold the trajectories.

## Addendum (after the lead's updates, 2026-10-09 late)
1. **The chain map z -> (3z - r)/5 is a representative artefact.**
   - The exact per-iteration map is D' = 3/5 D + 2/3 U4 + c_r.
   - U4 comes from exact small structure inside the iteration: "... 0 1 7 1^2 0 | 4", so CLR gives U2 = iter 2 (U 2) 4,
     a 2-tower of height ~65534, then U3 = iter((U2+2)/3)(U 2) 4 and U4 = iter((U3-1)/3)(U 4) 4.
   - The inner mini-round then deposits 1^(2/3 U4 + 10/3) as the new depth. Confirmed with geo-spaced representatives,
     with the U rep 4x the D rep (geo_checks.log).
   - tier1's follower replaces U4 by 19 or 2539, which drops the term. With depths of hundreds to thousands, the map
     then looks like (3z - r)/5. A big-policy U rep 2539 against z of a few hundred also distorts it.
   - Consequence: in the real run z never becomes small, so the small-z endpoints (junk at z = 3, 30; the N1 halt) are
     unreachable. A backward tree of the small-z junk set proves nothing about H14.
   - The real question is the branching on D mod 5 at large D. The class map and the real class sequence
     (0,0,2,2,3,2,3,4) are given above. Class 4 is still unresolved.
2. **The depth and k classes mod 7 in the b0 = 6 follower are wrong.**
   - From the Coq chain, T = arrow 37 2 3 = 23 mod 49, so JJ = (3T-13)/7 = 1 mod 7.
   - Real k1 = 4JJ-3 = 1457 mod 2520 = 29 mod 42. The follower uses k1 = 17, which is 3 mod 7.
   - Real round-1-end depth: w = 30 mod 42 in my convention (z2 D1^(w+1) right of the J0 cell), i.e. n = w-1 = 29 mod 42
     in the follower convention. The follower's 329, 371 and 2849 are all 35 mod 42, the wrong class.
   - Cause: b0 = 6 matches B = (T-4)/2 only mod 2520. B = 34 mod 49, and J mod 7 needs B mod 49.
   - My runs use the exact classes, since atoms are exact mod 7^2 and representatives are residues mod 840/1050.
3. **Eater and restart re-verified with widely spaced representatives** (geo, ratio 3 between ranks; w rep ~3000-4000 in
   lin, larger in geo; k1 rep 1457 and 2297 in the real class mod 840). All literal stages 1-21 give identical affine
   rewrites, including the 1.3e10-step whole-run conversion and the left event. So the eater and restart are not
   depth-fragile in the real class at these sizes. I did not test n in {329, 371, 2849}: they are in the wrong class.

## Files
- sim.py, stage.cpp/.exe, stage2.exe (accelerated, verified identical), xcheck.py, cmpacc.py
- numth.py, ures.py, vals.py, absim.py, drive.py, recheck.py, rtest.py, fiveadic.py, d8.py
- Logs: drive_r1_lin.log (round-1 end through stage 44), drive_r2_1050.log (stages 45-58), rtest_all.log,
  rtest_all2.log, rtest_d8.log
