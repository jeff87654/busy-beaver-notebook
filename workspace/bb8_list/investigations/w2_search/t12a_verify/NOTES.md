# T12a / H13c independent verification (Opus verifier, 2026-10-09): running notes

## Tools (this dir)
- lsim.cpp/.exe: my own literal simulator (written from scratch). Modes: run to halt; stop at the k-th K-moment
  (G reading 0 right of all 1s after '1 1010'); stop at a K-moment whose tokens equal a target (-1); stop at the first
  K-moment with a round-start signature 2 5 1^c 0^3 9 1^z (-2). Reports per-slot read counts for states J.. and lo.
- lsimpy.py: wrapper (parse_k splits a K-moment word into far bits + tokens).
- fol.py / sweep.py / rs1.py / r2sweep.py / dumpw.py: drivers that use the inplace follower (ilib/igstage) only as a
  stage engine for the jumps (base-rule abstractions); every literal stage is re-run by lsim (dumpw + check).
- tower.py: stable 2-tower residue mod m (independent of numres).

## Facts
- Literal re-check: all 26 stages of T12a from far_17 + [0 1^329|1|19] (std) re-run by lsim from the follower's stage
  inputs: every K-moment matches the follower (tokens AND far bits); final stage HALT L1 at step 3743.
  New-state reads per stage: J0,K0,L0 once in stages 0, 6, 10, 24, 25 (J0 -> 1RK, K0 -> 0RL, L0 -> 0RF: a one-shot
  detour); stage 26: J0, K0, then L1 = HALT. Round 2 (stages 14-22) and stage 23 read base slots only.
- Real accumulator residue: the follower token r and the B-form A satisfy A = 2r+2 (literal, conv.py). After any deep
  clear A = 3T-8 mod Q (Coq closed form U j (3a+1)+8 = 3 arrow j 2 (a+3); T = stable 2-tower mod Q). So
  r = (3T-10)/2 = 49612750485499 mod Q/2 = numres tau(1) (agrees), r = 19 mod 2520. The lead's number
  49612750485498 is the selector.md convention R = r - 1 (f = 2R+4); r = 18 mod 2520 would be wrong here.
- Restart far region: (10101)^(k-7) + TAIL22 '1011010101010101010100' for every k = 7..60 (k = 2..6: halt without a
  restart): the round-1 D2 run is NOT eaten, it stays as a left block of k1-7 D2 tokens. Real k1 is huge: fine.
- Depth sweep n = 1..700 (std, k=17, R=19): all restart at stage 14 with c = 19 and halt L1 at stage 25/26.
- Final stage (26) with the accumulator token r = 1..39, 2539: HALT L1 for every r (steps quadratic in r).
- WHERE c2 COMES FROM (rdep.py, replace the accumulator token of one stage input, follow to the RSIG): only three
  accumulators matter: r7 (stage-7 input, output of the stage-6 jump that clears 2r+3 at depth n1+4) gives the counter
  c2 = 19 + 4(r7-19)/3 = (4 r7 - 19)/3; r11 gives the depth z = 354 + 4(r11-19)/3; r14 gives P = 2 r14 + 4 (prefix).
  All other stage accumulators (s = 1..6, 8..10, 12, 13) do not affect the restart.  Every one of r7, r11, r14 is the
  output of a clear at depth ~ n1 (the round-1 cleared list, huge), so each is = tau(1) = 19 mod 2520 in the real run.
  => real c2 = 19 mod 3360 (class 5 mod 14, 19 mod 42), as tested.
- Stage-14 literal with r14 = 4..40, 2539, 5059, 7579: always '3 (2r14+4) 2 5 1^19 0^3 9 1^354', far 72 (lsim).
- Round-2 start harness (r2sweep.py: far (10101)^K1 + TAIL22, [3, P, 2, 5, 1^c, 0^3, 3, 1^z | r]):
  - c = 6..130 all classes: class 5 always HALT L1 at the round end; classes 1,4,6,8,10,11,12 also halt at the round
    end; 0, 3, 13 (and 7 for c >= 49) junk/MAX; 2 restarts with a small counter; 9 (n1's J0 class) restarts c = 19.
  - c = 19..1405 step 14 (class 5, k2 = 5..401): 100/100 HALT L1 at the round end.
  - P = 0..200, 5082, 10122, 15162: 204/204 HALT L1 at stage 11 (P-independent).
  - K1 = 0..60, 200, 1000: 63/63 HALT L1 at stage 11 (round-1 D2 remnant irrelevant, even K1 = 0).
  - z = 1..1200, 1201..3000 step 7, 5000-5002, 10001-10006, 20002 (round-2 START depth; end depth ~ z+54):
    1468/1468 HALT L1 at the round end.  Two end paths by z mod 6 (z = 4,5 mod 6: last K '7 1^32'; else '7 1^2'),
    both halt.
  - joint big start: K1 = 8650, P = 5082, c = 3379 (241 full periods), z = 3714, r = 2539: HALT L1 at stage 1451.
- c2 = (4 r7 - 19)/3 exactly for r7 = 10..200 step 3 and 2539, 5059, 7579, 10099 (c2 = 3379, 6739, 10099, 13459).
- Stage-0 accumulator R (the J0-config R) irrelevant: R = 4..100 step 3, 2539, 5059 -> same restart c = 19.
- Round-2 / end accumulators: replacing r at the input of stages 15..25 by 4..61 step 3, 2539, 5059: 22/22 HALT L1
  for every stage.
- Restart + halt at large depth / long far run: k in {17, 8657} x n in {2000, 5001, 10002} x R in {19, 2539}: all
  RSIG c = 19 at stage 14 (z = n+25), HALT L1 at stage 25/26.
- Real start (b0 = 6, std, my fol.py): round 1 RSIG c=79 stage 0, restart RSIG c=19 at stage 51, HALT L1 at stage 63.
- Restart-side residues: every restart stage needs its accumulator = 1 mod 3 (r = 1..61, 2539: only r = 1 mod 3
  restarts; T12a s=7 also fails for r = 1, 4, 7 because c2 < 6).  Every deep-clear output has A = 1 mod 3, so
  r = (A-2)/2 = 1 mod 3 automatically in the real run.
- 1^32 end path (z = 4, 5 mod 6): final stage HALT L1 for every accumulator r = 1..59, 2539.

## H13c
- Literal re-check (lsim) of all 17 stages for (k,n,R) = (17,329,19), (29,371,2539), (41,2849,19): 0 mismatches.
  New-state reads only in stages 0, 2, 4 (restart) and the final stage 16; round 2 and its end are base-only.
- Restart: far = (10101)^(k-12) + TAILH '101101010101010101000010000010100011100100' for k >= 12 (k = 9..11 also restart,
  k <= 8 no restart).  c2 = (4 r3 - 10)/3 exactly (r3 = 10..200 step 3, 2539, 5059, 7579, 10099), r3 = output of the
  stage-2 deep clear; P token = 2 r4 + 3 (r4 = stage-3 left-event clear).  Real: c2 = 22 mod 3360 (class 8 mod 14).
- n = 1..700 (k=17): 700/700 restart c=22 at stage 4 and HALT M1 at stage 16.  k in {17, 8657} x n in {2000, 5001,
  10002} x R in {19, 2539}: all HALT M1 at 16.  Real start std: RSIG c=79 stage 0, c=22 stage 41, HALT M1 stage 53.
- Round-2 harness (far (10101)^K1 + TAILH, [0 10 0 0 0 P 2 5 1^c 0^3 3 1^z | r]):
  c = 22..1408 step 14: 100/100 HM1; P = 0..200, 5081, 10121: 203/203; K1 = 0..60, 1000: 62/62;
  z = 1..1200, 1201..3000 step 7, 5000..5005: 1464/1464 HM1; joint K1=8645 P=5081 c=3382 z=3714: HM1 at stage 1451.
  c = 6..100 by class: 1, 5, 8 always halt at the round end; 9 restarts (c=22); 0, 3, 12, 13 junk; others mixed.
- RESIDUE SENSITIVITY (new): the accumulator entering the round-end stage (s=13 at c=22; s=37..40 at c=92) decides
  the outcome by r mod 9: r = 1 mod 9 -> HALT M1, r = 2 mod 3 -> HALT, r = 0 mod 3 or 4, 7 mod 9 -> junk (MAX).
  All r = 1 mod 9 in 1..730 (every class mod 729 above 1 mod 9) halt at s = 12..15 (c=22) and s = 37..40 (c=92).
  Real r = (3T-10)/2 = 19 mod 27 = 46 mod 729 (T = 16 mod 18), so r = 1 mod 9: the real class halts.  (The std rep
  19 and big rep 2539 are both 1 mod 9, so the screen was faithful here, but only because 9 | 2520.)

## 2026-10-10: TRUE-ORDER SYMBOLIC DRIVE (lead's H14-artefact attack)
Tool: tdrive.py / tdrive2.py = h14verify's absim/drive (snapshot in snap/, stage.exe rebuilt from their stage.cpp,
group() block period raised to 24) with only the machine changed.  B-form configurations; atoms = huge values with
EXACT residues (Coq U closed form, stable towers) and magnitude ranks (k1 << w << f << each fresh U); Coq CLR and
PERIODS macros; every other stage literal under 10 rank-ordered representative sets with an affine fit (NonUniform =
stop).  Additions: REAT2 (a multi-atom count/value is replaced by a fresh atom with its exact residue, rank just above
its dominant atom, to keep literal sizes small), PREOK (PERIODS macro with a left prefix; round-2 periods never visit
the prefix, lsim lo values), LOOP acceleration in tdrive2 (three consecutive uniform stages with constant integer
field differences -> jump N iterations; an induction step).
T12a (logs tdrive_t12a.log stages 1-25 MREP 840 GROW 3; tdrive_t12a_d/e/f/g.log after):
- restart, symbolic: '... 3 (U12+2) 2 5 1^(2/3 U7 - 23/3) 0^3 9 1^(w + 2/3 U10 - 5/3) | 4': counter (2U7-23)/3 =
  (4 r7 - 19)/3 (A = 2r+2), prefix U12+2 = 2 r14 + 4, depth w + 2/3 U10.  Uniform in k1, w, f, U3..U12.
- PERIODS macro: J = (U7-40)/21 periods, r = 17 left; k2 = 4/21 U7 - 139/21 (accumulator-sized D2 run).
- 3 literal periods (17 -> 11 -> 5 -> 3), each adding 2/3 of a fresh accumulator to the depth (normal n1 periods).
- round-2 end (stage 39): Per k2 3 with depth X23 (= n + 2/3 a + 2/3 U19 ..) and acc U22 ->
  '2^(k2-4) 0^3 z2 (0 z5)^3 2^2 0 (U22) 1^3 0 1^X23 | 6'; then a uniform LOOP, one depth unit per B-form stage:
  (2 0 3)^j 2 0 10 1^3 0 1^(X23-j-1) | 6 -> j+1 (accelerated x (X23-...)); ends '... (U22-7) (2 0 3)^X23 2 0 10 1^3 0 | 4'.
- CLR d=3 n=3 (a SHALLOW clear: U24 = iter 3 (U 3) 4, a fixed constant, exact residue), then ONE literal stage turns
  (2 0 3)^X23 into (junk11)^(X23/6 - 4/3) (uses X23 mod 6, exact real residue), then ONE stage turns U24 into
  (junk6)^((U24-40)/9) (needs U24 mod 9: NonUniform at MREP 840, uniform at MREP 2520), CLR d=2 n=3 -> U25, and
  stage 76: HALT, state L reads 1, uniform over all 10 representative sets (k1, U7, U12, X23, U22, U24, U25 varied).
- So the halt is reached directly after counter exhaustion by a FIXED sequence of macro stages; no fresh accumulator
  ever feeds a list that must shrink (no H14-type chain).  Residue dependences: X23 mod 6 (both classes halt in the
  follower), U24 mod 9 (a constant), nothing value-decided.
H13c (tdrive_h13c.log, MREP 2520 GROW 2): restart counter (2U4-14)/3 = (4r3-10)/3, PERIODS J=(U4-40)/21 r=20, 3 literal
periods, end: U14 -> (junk)^((U14-31)/9) (the mod-9 condition, exact), U16 -> (0 z5)^((U16-4)/3), CLR d=2 at depth X15 ->
U17; final stage (10-trial absim too slow, ~5.7 U17^2 steps) run by final30.py with lsim from the rendered B-form under
6 true-order rep sets (one per X15 mod 6): 6/6 HALT M1 (6.6-7.4e10 steps).
Incident: while stopping my first slow drive I killed every stage.exe, including one of another agent (PID 1095748,
parent 918388); reported to the lead.  Since then I stop processes only by my own PIDs.
## 2026-10-10 late: rank-rule fix + mod 49
- snap2/ = current h14verify absim (constant-tier ranks), my binary renamed stage_t12v.exe; tdrive3.py converts old
  pickles (real tier, rank+1000) and puts exact-input CLR outputs (U24: d=3 n=3; U25: d=2 n=3) in the const tier.
  Only those two CLRs in T12a have small inputs (all earlier CLRs have n = real depth).  Re-run 72-76: HALT L1 again,
  uniform over 10 reps (tdrive_t12a_h.log).  H13c has no small-input CLR.
- Follower at real classes k1 in {29,71,113,1457} x n in {29,71,113,2129}: T12a 16/16 RSIG c=19 @14, HL1@26; H13c
  16/16 RSIG c=22 @4, HM1@16.  Drive atoms exact mod 49 for k1 (36), w (16), U (12); J = 1 mod 7.
## Rank audit (2026-10-10): snap3 + endrun.py with explicit true-order ranks.  T12a end (endrun_t12a.log): identical,
HALT L1.  H13c end stages 1-6 (1130/1133 classes) identical; final stage final30b.py (U14 > U17 > U16 > X15): 6/6 HM1.
