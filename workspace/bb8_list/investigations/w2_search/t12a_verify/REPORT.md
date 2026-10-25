# T12a / H13c: independent adversarial verification (Opus verifier, 2026-10-09)

## Verdicts
- **T12a** = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---
  (12 states): **CONFIRMED at screening level.** Every attack failed. There is no residue condition at the round-2 end.
- **H13c** = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1LK0LL_0LM0LA_0LJ---
  (13 states): **CONFIRMED at screening level**, with one caveat:
  - The round-2-end outcome depends on the round-end accumulator r mod 9.
  - r = 1 mod 9 halts; r = 0 mod 3 or 4, 7 mod 9 gives junk that does not halt.
  - The real r is 19 mod 27, so the real run is in the halting class.
- Neither machine is broken. Evidence level is follower screening plus literal re-checks; there is no proof.
- **Update 2026-10-10: the H14-type artefact attack also fails.** I re-derived both machines symbolically with
  h14verify's absim engine in the true size order (k1 << depth << accumulator, every fresh accumulator a new atom
  with an exact tower residue). Both still halt at round 2's end, directly after counter exhaustion, through a fixed
  sequence of stages. There is no shrinking chain driven by fresh accumulators, and nothing is decided by the exact
  value of the depth. Details are in the section "True-order symbolic re-derivation" below.

## Method (as independent as possible)
- **My own literal simulator (lsim.cpp).**
  - I wrote it from scratch and did not reuse igstage.
  - I re-ran every literal stage of the follower runs from the follower's stage inputs:
    - T12a (k,n,R) = (17,329,19), (29,371,2539), (41,2849,19).
    - H13c, the same three (k,n,R).
  - Result: 0 mismatches in tokens and far bits. The final HALT steps are reproduced (T12a: L1 after 3743 steps).
- **Use of the inplace follower (ilib/igstage).** I used it only as a stage engine for the jumps, inside my own sweep
  drivers. The jumps are base-machine abstractions.
- **Real residues: my own derivation.**
  - The follower accumulator r and n1's B-form A satisfy A = 2r+2 (checked literally, conv.py).
  - After any deep clear, A = 3T-8 mod Q (Coq closed form U j (3a+1)+8 = 3 arrow j 2 (a+3)), where T is the stable
    2-tower mod Q (tower.py: T = 33075166990336 mod Q, T = 16 mod 18).
  - So r = (3T-10)/2 = 49612750485499 mod Q/2. This equals numres tau(1).
  - Consequences: r = 19 mod 2520, 19 mod 27, 46 mod 729, 1 mod 3.

## Lead's residue: convention warning
The lead's R = 49612750485498 mod 54305848396800 is the selector.md convention R = r - 1 (f = 2R+4). In the follower
convention it would give R = 0 mod 3, and then (4R-19)/3 is not an integer. The formulas below use the follower's
r = 49612750485499, which is 19 mod 2520. So the class used in the screens (19) is the real class.

## What drives the restart: one accumulator each
I replaced the accumulator token of each stage input and followed to the round-start signature (rdep.py).
- **T12a.**
  - c2 = (4 r7 - 19)/3 exactly. r7 is the output of the stage-6 jump, a clear at depth n1+4.
    - Checked for r7 = 10..200 step 3, 2539, 5059, 7579, 10099, giving 3379, 6739, 10099, 13459.
  - The prefix is P = 2 r14 + 4.
  - The depth is z = 354 + 4(r11-19)/3.
  - The other ten stage accumulators do not matter beyond r = 1 mod 3.
  - The J0-config accumulator R is irrelevant (R = 4..100, 2539, 5059).
- **H13c.**
  - c2 = (4 r3 - 10)/3 exactly (same r-list).
  - P = 2 r4 + 3.
- **Real values.** All of these accumulators are deep-clear outputs at depth about n1, so each is = 19 mod 2520.
  - T12a: c2 = 19 mod 3360, class 5 mod 14, as tested.
  - H13c: c2 = 22 mod 3360, class 8 mod 14, as tested.
- **Restart stages need r = 1 mod 3.** This holds automatically: A = 1 mod 3 implies r = 1 mod 3.

## Attacks and results
| attack | T12a | H13c |
|---|---|---|
| k1 huge (real k1 = 17 mod 8640, but only size matters) | restart for every k = 7..60 and k = 8657; far after restart = (10101)^(k-7) + 22-bit tail (round-1 D2 run kept) | every k >= 9 and k = 8657; far = (10101)^(k-12) + 42-bit tail |
| round-1 depth class (real 35 mod 42; 41 is the wrong class) | n = 1..700: 700/700 restart c=19 and HALT L1 | n = 1..700: 700/700 restart c=22 and HALT M1 |
| large depth | n = 2000, 5001, 10002 x k = 17, 8657 x R = 19, 2539: all halt | same: all halt |
| c2 scales with R in one class mod 2520 | yes, exact linear formula (19, 3379, 6739, ...) | yes (22, 3382, ...) |
| round-2 counter class (c sweep, harness = stage-14 jump output) | c = 19..1405 step 14 (k2 = 5..401): 100/100 HALT L1 at the round end | c = 22..1408 step 14: 100/100 HALT M1 |
| other counter classes (c = 6..130) | classes 1, 4, 5, 6, 8, 10, 11, 12 halt at the round end; 0, 3, 13 (7 for c >= 49) junk; 2 small restart; 9 (n1's J0 class) restarts c = 19 | 1, 5, 8 halt; 9 restarts c = 22; 0, 3, 12, 13 junk; rest mixed |
| prefix token P (real = 2r+4, huge) | P = 0..200, 5082, 10122, 15162: 204/204 halt | P = 0..200, 5081, 10121: 203/203 |
| round-1 D2 remnant K1 (real huge) | K1 = 0..60, 200, 1000: 63/63 | K1 = 0..60, 1000: 62/62 |
| round-2 depth z (real round-end depth astronomically large, unknown fine residues) | z = 1..1200, 1201..3000 step 7, 5000-5002, 10001-10006, 20002: all halt (two end paths by z mod 6, both halt) | z = 1..1200, 1201..3000 step 7, 5000..5005: 1464/1464 |
| round-2 / round-end accumulators | r at stages 15..25: any r = 1 mod 3 halts; final stage halts for every r = 1..59, 2539 (both end paths) | **r mod 9 matters at the round-end stages**; all r = 1 mod 9 in 1..730 halt (s = 12..15 at c=22; s = 37..40 at c=92); real r = 1 mod 9 |
| joint big values in one run | K1=8650, P=5082, c=3379 (241 full periods), z=3714: HALT L1 at stage 1451 | K1=8645, P=5081, c=3382, z=3714: HALT M1 at stage 1451 |
| real start b0=6 (std) | RSIG c=79 at 0, restart c=19 at 51, HALT L1 at 63 | c=22 at 41, HALT M1 at 53 |

## Follower validity (jumps vs new states)
- New-state slots are read only in literal stages. Counts are from lsim per stage:
  - T12a reads J0, K0, L0 once in stages 0, 6, 10, 24, 25 (J0 -> 1RK -> 0RL -> 0RF: a 3-step detour). Stage 26 reads
    J0, K0 and then L1 (HALT).
  - H13c reads new states in stages 0, 2, 4 and in the final stage 16.
  - In both machines, round 2 and its end-game jumps read base slots only.
- The jumps abstract n1's champion moves (R1, R2M, CLR, PERIOD). These are Coq-proved non-halting transitions of n1
  with an arbitrary left context. In n1, J0 is undefined, and K, L, M are reachable only through J0. So no jumped
  segment can read a new-state slot.
- The remaining trust is in follow2.jump faithfully composing those rules. This is the same trust n1's screening
  relied on before its Coq proof.

## Round 2 is a full round
- Round 2 is not a shortcut.
  - The joint run consumed c = 3379 by 241 periods: 1451 stages, about 6 per period.
  - Every period jump clears the whole depth list (a full cycle at depth about W1).
- The halt comes only after the round-2 counter is exhausted:
  - T12a: Per k 3 end-game (c2 = 5 mod 14).
  - H13c: m = 6 end-game (class 8).
- The halting stages:
  - T12a: the depth list is turned into (2 0 3)^m blocks (stage 23), most blocks are eaten into far junk (stage 24),
    then '7 1^2' (or '7 1^32'). In the last stage J0 is read at a cell followed by 0, 1, so K0 -> L reads 1 -> HALT.
  - H13c: left event '7 1^z'. The final stage walks back across the depth list and halts at M1 in the end-game junk,
    right of the prefix and D2 runs.

## sigma estimate
- **Notation** (n1 Coq): F n = arrow n 2 4 (about f_omega). W1 = n1's final depth >= iter (2 JJ+1) F 34, with
  JJ = (3T-13)/7 and T = 2^(37 arrows) 3.
- **Restart.**
  - c2 = (4 r7 - 19)/3, where r7 = (A7-2)/2.
  - A7 = U_d(x) = 3 arrow d 2 (x/3+3) - 8 at depth d of about W1.
  - So c2 is about 2 arrow W1 2 (.), which is >= F(W1).
  - The depth also jumps to about (4/3) r11 >= F(W1).
- **Round 2.**
  - JJ2 = (c2-5)/14 periods, each with n -> >= F(F n).
  - W2 >= iter (2 JJ2) F (F W1) ~ f_(omega+1)(f_omega(W1)).
- **sigma.**
  - sigma >= W2 (the halting configuration holds about W2/3 junk blocks).
  - So sigma ~ f_(omega+1)(f_omega(f_(omega+1)(JJ))) > f_(omega+1)^2(JJ), versus n1's f_(omega+1)(JJ).
  - H13c has the same shape, with JJ2 = (c2-8)/14.

## Remaining gaps (why this is screening, not proof)
1. The jumps are the follower's abstraction of n1 rules. They are trusted, not re-proved here.
2. Huge parameters (k1, P, k2, round-end depth z2, about f_omega-sized) are covered by wide sweeps that show uniform
   behaviour, not by inductive lemmas. The halting stages are linear sweeps over the depth list and the blocks; they
   need inductive Coq lemmas (z mod 6 case split for T12a).
3. H13c's halt needs the round-end accumulator = 1 mod 9. The real value satisfies this (19 mod 27), but a proof
   needs the arrow residue lemma below.

## True-order symbolic re-derivation (answers the lead's H14-artefact, depth-chain and k2 questions)
**Tool.** h14verify's absim/drive, unchanged except for the machine string. I used a snapshot in snap/, rebuilt
stage.exe from their stage.cpp, and raised the block-period limit in group() from 8 to 24.
- It starts from the Coq HALT_B configuration Bf (FarE k1) [0, 1^w | f] with exact residues: k1 = 1457 mod 2520,
  w = 2130 mod 2520, f = U-outputs = 40 mod 2520.
- Coq CLR and PERIODS run as macros.
- Every other stage runs literally under about 10 rank-ordered representative sets (k1 << w << f << U3 << U4 << ...),
  with an affine-uniformity check that stops on any difference.
- My additions:
  - tdrive.py / tdrive2.py drivers.
  - REAT2: a value combining several atoms becomes a fresh atom with its exact residue and the rank of its dominant
    atom.
  - PREOK: PERIODS is allowed with a left prefix. Round-2 periods never visit the prefix (lsim lo >= the round-2 D2
    run).
  - LOOP acceleration: three uniform consecutive stages with constant field differences jump N iterations at once.
    This is an induction step.

**T12a** (tdrive_t12a*.log; MREP 840, then 2520 from stage 73; GROW 3, then 2).
- **Restart.**
  - The start configuration is `3 (U12+2) 2 5 1^((2 U7-23)/3) 0^3 9 1^(w+2/3 U10-5/3) | 4`.
  - B-form A = 2r+2, so the counter is (4 r7-19)/3 and the prefix is 2 r14+4. All stages are uniform in k1, w, f and
    U3..U12.
- **Round 2.**
  - PERIODS gives J = (U7-40)/21 periods with r = 17 left over.
  - The D2 run is k2 = (4 U7-139)/21, accumulator-sized. The lead's k2 point is covered symbolically: the end-game
    stages are affine in k2.
  - The last three periods run literally. Each adds 2/3 of a fresh U to the depth (normal n1 periods).
- **Round-2 end.**
  - Stage 39 starts from Per k2 3 with depth X23 and accumulator U22.
  - Then comes a uniform LOOP, one depth unit per B-form stage: `(2 0 3)^j 2 0 10 1^3 0 1^(X23-j-1) | 6`. There is no
    fresh accumulator in it.
  - CLR d=3 n=3 gives U24 = iter 3 (U 3) 4. This is a FIXED constant (a shallow clear) with an exact residue.
  - One stage turns (2 0 3)^X23 into (junk)^(X23/6 - 4/3). This uses X23 mod 6, the exact real class; the follower
    showed that every class halts.
  - One stage turns U24 into (junk)^((U24-40)/9). This uses U24 mod 9: it is non-uniform at MREP 840 and uniform at
    2520.
  - CLR d=2 n=3 gives U25.
  - Stage 76: **HALT, state L reads 1**, identical in all 10 representative sets (k1, U7, U12, X23, U22, U24, U25
    varied).
**H13c** (tdrive_h13c.log; MREP 2520, GROW 2; final stage run separately by final30.py with lsim).
- **Restart.**
  - The start configuration is `(U5+1) 2 5 1^((2 U4-14)/3) 0^3 9 1^(w+9) | 4`, so the counter is (4 r3-10)/3.
  - PERIODS gives J = (U4-40)/21 with r = 20. Three literal periods follow.
- **Round-2 end.**
  - Stage 27 turns the round-end accumulator U14 into (junk)^((U14-31)/9). This is the r = 1 mod 9 condition found
    earlier, and it holds exactly: U14 = 40 mod 2520 gives r = 19 mod 2520.
  - Stage 28 turns U16 (a deep clear) into (0 z5)^((U16-4)/3).
  - CLR d=2 at depth X15 gives a fresh U17.
- **Final stage.**
  - It is too slow for the 10-trial absim run (about 5.7 U17^2 steps), so I ran it separately with lsim from the
    rendered B-form.
  - 6 true-order representative sets: k1 << U4 << U5 << U14 << U16 << X15 (one set per class X15 mod 6, about
    50 000) << U17 (about 100 000-118 000).
  - All 6 give **HALT M1** after 6.6-7.4e10 steps. The number of J0 detours is (U16-4)/6 + 1, so the final stage eats
    the U16 junk two blocks per detour.
**Answers.**
- **Residue-decided, not value-decided.**
  - Neither halt passes through a chain on the exact depth or counter. The depth enters only through a uniform
    one-unit loop or walk, plus its class mod 6 (T12a), where every class halts.
  - The accumulators enter only through fixed residues: T12a U24 mod 9 (a constant); H13c U14 mod 9 and U16 mod 3
    (real class).
  - The follower's many exact depths (z = 1..20002) agree with this.
- **Accumulators after counter exhaustion.**
  - T12a: two shallow CLRs (constants U24, U25), then the halt.
  - H13c: U16 and U17 are fresh huge accumulators. Each is consumed once by a uniform stage (junk conversion, R1
    rounds), not fed back into a shrinking list.
  - So the H14 mechanism, where D' = (9D + 10U + C)/15 grows without bound, does not occur.
- **Real residues.** As established above (r = 19 mod 2520). The lead's R = ...498 is the r-1 convention. The
  B-form U = 40 mod 2520 used by absim is the same quantity, since A = 2r+2.
- **Proof consequences.**
  - T12a's end-game needs these lemmas:
    - an induction lemma for the one-unit loop over the depth list;
    - a mod-6 case split for the block regrouping (or a 6-step loop lemma);
    - a mod-9 residue of the constant iter 3 (U 3) 4;
    - two shallow CLRs.
  - H13c additionally needs the round-end accumulator = 4 mod 9 (B-form) lemma.
  - No backward-tree argument is needed for either machine.


## Addendum 2 (2026-10-10): absim rank-rule fix and the mod-49 depth correction
**Rank rule.**
- I copied the CURRENT h14verify absim/drive/ures into snap2/. My binary is renamed stage_t12v.exe, so it cannot
  collide with theirs. Driver: tdrive3.py.
- In the T12a checkpoints, every CLR before stage 71 has a real-run depth as its n:
  - w+4, w+3, w+1, w, w + 2/3 U10, X14, n16, X20.
  - So the old "new output ranks above everything" rule placed no fixed constant above real-run values there.
- The only small-input CLRs in the whole run are stage 71 (d=3, n=3, A=4, giving U24) and stage 75 (d=2, n=3, A=4,
  giving U25).
- Re-run from stage 72 with U24 and U25 in the constant tier (rank 33 and 32, below k1 = rank 1000):
  - stages 72-75 give identical rewrites;
  - stage 76: **HALT, state L reads 1**, uniform over all 10 representative sets (tdrive_t12a_h.log).
- H13c has no small-input CLR at all. Every CLR has n = w+11, w+9, n8-1, X12-2, X15-1 or X15, so its run is unaffected.
- Caveat on the old rule (not changed by the fix): a deep clear with d = 3 (for example U8 = iter 3 (U (w+1)) 4) is
  really smaller than the earlier accumulator U7 = iter (U6/3) (U (w+3)) 4, but absim ranks it above U7.
  - At the follower level, both orders were tested: rdep set r7 = 10099 >> r8 = 19, and r8 = 2539 >> r7 = 19. Both
    give the same restart.
  - So this misordering does not affect the restart.


**Rank-rule confirmation (lead's question).**
- The first true-order runs (stages 1-76 of T12a, and all of H13c) used the OLD rule.
- Under the old rule, U24 (CLR d=3 n=3) and U25 (CLR d=2 n=3) were ranked above the depth X23.
- I then re-ran T12a stages 72-76 with the CURRENT h14verify absim (snap2/, tdrive3.py). There U24 and U25 are
  constant-tier atoms (ranks 33 and 32), far below k1 and the depth. The rewrites and the HALT (L reads 1) are
  identical under both rules.
- H13c has no small-input CLR, so the two rules coincide there.

**mod-49 classes.**
- The true-order drive starts from round1_end with atoms that are exact mod 7^2: k1 = 29 mod 42 (36 mod 49),
  w = 30 mod 42 (B-form; the follower's n = 29 mod 42), U outputs = 40 mod 2520 (12 mod 49).
- PERIODS uses U7's exact residue: J = (U7-40)/21 = 1 mod 7, and the left-over r = 17, i.e. the end class m.
- The round-2-end depth X23 has its exact residue mod 6 (= 2). Its modulus does not include 49, but no end-game stage
  depends on it.
- The representative sets differ mod 49 and every stage stayed uniform, so no stage depends on a residue mod 49.
- Follower at the real classes: k1 in {29, 71, 113, 1457} x n in {29, 71, 113, 2129}, std.
  - T12a: 16/16 restart with c = 19 at stage 14 and HALT L1 at stage 26.
  - H13c: 16/16 restart with c = 22 at stage 4 and HALT M1 at stage 16.
- Nothing changes. The earlier n = 1..700 and k >= 7 sweeps already contained these classes.


## Addendum 3 (2026-10-10): rank audit of the round-2 end games (inputs-based / true order)
**Setup.**
- Tools: snap3/ is the current h14verify absim/ures/vals, with RANKMODE=min and my own binary stage_t12v.exe.
- endrun.py starts from the round-2-end Per form with fresh atoms whose ranks I set from a magnitude argument.
  - Two facts drive the order:
    1. A clear with a huge iteration count d dominates any clear at a depth w+O(1) with small d.
    2. A clear at a larger depth dominates anything built at depth w+O(1).
  - New CLR outputs get RANKMODE=min ranks, or explicit overrides where min is wrong: iter 2 (U X) 4 is ABOVE
    iter 3 (U (X-1)) 4.
- Representatives: MREP 2520, geo GROW 2.

**T12a**, from Per(prefix) k2 3 N | U22 (spec_t12a_end.py, endrun_t12a.log).
- True order: k1 << k2 = (4U7-55)/21 << P = U12+2 << N (round-2 end depth) << U22.
  - U12 is a clear at depth X14 = w + 2/3 U10, far deeper than U7's depth w+3, so P >> k2.
- This is the same order my earlier runs used. The CLR outputs at X14 / n16 / X20 depths are all consumed during the
  Coq-proved round 2; only U19 (inside N) and U22 reach the end game.
- The only end-game CLRs have exact inputs: U24 (d=3 n=3) and U25 (d=2 n=3). Both are constant tier, ranks 33 and 32.
- Result: LOOP x (N-12), CLR d=3 n=3, the blocks-by-6 stage, the U24/9 stage, CLR d=2 n=3, then **HALT L1**.
  - Every rewrite is identical to the earlier runs.
  - The final steps are uniform over the 10 representative sets.
- **The T12a halt is unchanged.**

**H13c**, from Per(prefix) k2 6 X15 | U14 (spec_h13c_end_1130/1133.py, endrun_h13c_*.log, final30b.log).
- True order: k1 << P (U5 = iter 2 (U (w+11)) 4) << k2 (U4, huge d) << X15 << U16 = iter 3 (U (X15-1)) 4
  << U17 = iter 2 (U (X15-1)) 4 << U14 (huge-d round-end clear).
  - My earlier drive had U14 below U16/U17, and final30 had U16 < X15. Both orders were wrong.
- Re-run in the true order:
  - Stages 1-6 (two depth classes, X15 = 2 and 5 mod 6) give rewrites identical to the earlier drive.
  - The final stage was run with lsim from the rendered B-form under 6 true-order representative sets, one per class
    X15 mod 6, with U14 about 80k > U17 about 50k > U16 about 35k > X15 about 22k.
  - All 6 give **HALT M1** (1.6-2.1e10 steps). The number of J0 detours is still (U16-4)/6 + 1.
- **The H13c halt is unchanged.**

## Recommended next step: Coq, T12a first
T12a comes first: 12 states, and the round-2 end needs no accumulator residue condition. Reuse bb10_n1_coq's mexp
workflow.
1. **Base lemmas.** Run gen_machine.py for T12a with n1's spec lists unchanged (PASS, PRO, R2M, CLR, S0, P1-P4, E).
   States A-J agree with n1 except J0, which n1's specs never read.
   - Generalise Per from Bf0 to Bf L. n1's Per uses a blank left; round 2 has P + far on the left. The events are
     already stated for an arbitrary L.
2. **Round 1.** Use main.v.in up to `Bf (FarE k1) (1^w ++ [0]) f`, replacing HALT_B by the restart chain.
3. **Restart.** 14 literal-stage events and 13 CLR jumps (evs.py-style specs, validated literally first).
   - Stages 6-7 and 13-14 build and consume the r7-sized junk (100000)^x into the counter. They need induction over
     the junk count.
   - Residues: every deep-clear r = 1 mod 3 (from A = 1 mod 3), and c2 = 5 mod 14. The latter needs
     arrow d 2 x = 2 mod 14 for d >= 2: towers of 2 are 2 mod 7 and even. This is like n1's mod-7 residue lemma.
4. **Round 2.** Iterate the PERIOD lemma JJ2 = (c2-5)/14 times (PERIODS_G with left context L).
5. **Round-2 end.** Prove these as inductive events:
   - stage 23: 1^z -> (2 0 3)^m, with a case split on z mod 6;
   - stage 24: block eating;
   - stages 25-26: constant size plus an r-linear part.
   The stage-24 excursion goes about 4 D2 cells into the round-1 D2 run.
6. **Score.** sigma >= iter (2 JJ2) F (F W1), using the bound.v.in / fgh templates.
For H13c, add the lemma "round-end r = 1 mod 9". It follows from A = 3 arrow - 8 with arrow = 4 mod 6 (even, and
1 mod 3).

## Files (this dir)
- lsim.cpp/.exe, lsimpy.py: my own literal simulator. Run with `python recheck.py M PREFIX` after dumpw.py.
- fol.py, sweep.py, rs1.py, r2sweep.py, rdep.py, dumpw.py, t14.py, t26.py, tower.py, conv.py: drivers and checks.
- Logs:
  - T12a: sw_n1_700, r2_c6_300, r2_c5mod14, r2_P, r2_K1, r2_z, r2_zbig, r2_joint, rdep7, sw_bign, t12a_real_std.
  - H13c: hsw_n1_700, h_c6_100, h_c8mod14, h_P, h_K1, h_z, h_joint, hrdep3, hsw_bign, h13c_real_std.
- Stage word dumps: w/ (T12a) and wh/ (H13c). NOTES.md has the running notes.
- Symbolic: snap/ (h14verify absim snapshot), tdrive.py, tdrive2.py, final30.py, dbg73.py.
  - Logs: tdrive_t12a.log, tdrive_t12a_d/e/f/g.log (T12a), tdrive_h13c.log, final30.log (H13c).
  - Pickles: tdrive_t12a_s25.pkl, tdrive_t12a_d/e/f/g.pkl.
