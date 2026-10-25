# d13: 13-state D1-mechanism Tier-1 search. REPORT (inv-w2-d13, Opus, 2026-10-09/10)

## Verdict
- **No 12- or 13-state Tier-1 halter is supported.** The candidate C13a/C13b below passed every std screen. Its halt,
  however, is a U = 19 representative artefact (the same failure the verifier found for H14). Under the big policy,
  its round-2 end turns into a chain of mini-rounds with no halt. So halting is open.
- **What C13a does have:** a robust 12-state J0 = 1LK eater with an accumulator-sized restart counter 2R+5 (class 1
  mod 14), and a full round 2. This is a second, independent eater mechanism, not D1.
- The D1 core itself cannot host a 13-state hook. s1 and s2 are complete negatives, so direction 1 is closed and
  direction 2 has a structural answer.
- **The 12-state J0 = 0LK tree is now complete at the real depth class (n = 77).** It contains no Tier-1 halter, and
  its six accumulator-sized delta != 0 families admit no one-state hook.
- **Depth-class caveat.** n = 41 scans give false positives (3 rejected hits below) and false negatives. n = 77
  (= 35 mod 42, like the real depth 329) costs about 1.7x as much.

## Downgrade of C13a (U-variation test, bigend.py)
- **In std, the halt comes 4 stages after round 2's counter runs out:**
  - stage 59: the depth list becomes (2 0 3)^m;
  - stage 60: that block becomes far bits, and the list becomes 4 9 0 1^6 2 1^2 0^5 8 1^31, where the 1^31 comes
    from U;
  - stage 61: left event '7 1^32';
  - stage 62: HALT M1 during the unpack.
  - The list is U-sized and the far region depth-sized. In std their order is the reverse of reality.
- **Big policy (U = 2539), crafted round-2 start, cap 6e10 steps:**
  - Stages 0-19 have the same shape as in std.
  - At the round end the far region grows to about 300k bits.
  - A mini-round chain follows ('5084 5 0^3 9 1^10', then '2 5 0^3 9 1^6').
  - No left event and no halt by stage 29 (C13a) or stage 35 (C13b).
- **Conclusion:** like H14, the post-round phase is a chain driven by fresh accumulators, and the std halt is not
  evidence.

## Candidate C13a (13 states): eater and round 2 confirmed, halt NOT supported
`1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LK0LC_0RL1RM_0RI0RK_1RD---`
- **Base.** The 12-state eater is `..._0LJ0LI_1LK0LC_0RL1RC_0RI0RK` (J0 = 1LK, K = 0RL1RC, L = 0RI0RK).
- **Hook.** K1 = 1RC is redirected to M = a copy of C (M0 = 1RD), with M1 undefined, which is the halt.
- **Siblings, same family.**
  - C13b = `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LM0LC_0RL0LB_0RI0RK_0RL---`: J0 goes to M =
    a copy of K with M1 = halt.
  - The same machine with L0 = 0LH.
- **Mechanism.**
  - The eater reads J0 at n1's halting configuration, so round 1 is exactly n1's run.
  - It turns the far D2 run into a prefix of 2s and keeps the old accumulator R as a digit.
  - Round 2 then starts as `2^(k-4) 1 5 (R-2) 2 5 1^(2R+5) 0^3 9 1^z`.
  - Round 2 ends in counter class 1 mod 14, a context round 1 never produces. There the left event sends K1 onto M
    reading a 1, which halts.
- **Real start, b0 = 6, std follower (C13a_b6_std.log).**
  - Stages 0-36 are n1's round 1, and stage 37 is the eater.
  - Stage 38 restarts with `2^13 1 5 17 2 5 1^43 0^3 9 1^334`, where 43 = 2R+5.
  - Round 2's counter runs out at stage 58. The round-end phase runs from stage 59 to 61.
  - HALT M1 at stage 62.
- **Round-1 eater robustness (validate.py, std).** Restart with c = 43 at stage 1, then HALT M1 (C13a at stage 25,
  C13b at 31), for (k, n) = (17,77), (29,77), (41,77), (77,77), (17,329), (29,329), (41,371) and (17,2849).
- **Accumulator scaling (scalechk.py, big policy, R = 2539).**
  - Restart counter c = 5083 = 2R+5, with prefix `2^(k-4) 1 5 2537`, for k = 17, 77 and 137.
  - No halt in round 1.
- **Round-2 end over residues (val3.py, std, crafted `2^(k-4) 1 5 p 2 5 1^c 0^3 3 1^z | 1 | 19`).**
  - All 18 cases halt at M1 just after round 2's left event.
  - The halt stage is 25 + 18(c-43)/42, linear in c, so the halt comes after the counter runs out.
  - Values covered:

    | parameter | values |
    |---|---|
    | c | 43, 57, 71, 85, 99, 113, 127, 169, 211 (class 1 mod 14; residues 1, 15, 29 mod 42; the real one is 43 mod 5040) |
    | z | 84, 330, 1001 |
    | k | 17, 29, 77 |
    | p | 17, 59, 101, 1277, 2537, 5057 |

  - C13b: 6 of 6 crafted cases halt the same way.
- **Big-policy round-2 end.** The literal stage times out at the round end (stage 20, more than 4e9 steps), so it is
  infeasible, as it was for H14. The round-2 halt therefore rests on std residue evidence.
- **Open risks.**
  1. In the real run the prefix digit R-2 is far smaller than round 2's accumulators. In std they are comparable
     (17 vs 19). The p sweep up to 5057 showed no dependence on p.
  2. No independent simulator has checked this yet.
- **Grade, only if a halt is ever established.** Round 2 is reloaded from the accumulator (c2 = 2R+5), so sigma
  would be >~ f_(omega+1)(f_(omega+1)(~2^^363)). Under the U-variation test the halt route does not fire, so C13a
  currently scores nothing.
- **Overlap.** inplace's H13c (J0 = 1RK, in place) is a different machine. C13a's eater also keeps R as a prefix,
  like P11.

## Why D1 has no 13-state hook (slotctx.py)
- **Round 1 (k = 17).** D1's new slots are read only in three places:
  - stage 0: J0 K0, then J0 K1 L0 K0;
  - stage 7: three times the fill loop J0 K1 L1 M1 M1 M1 M0 (J0 at p with 1s at p-1..p-3 writes a 1 at p);
  - stage 12: J0 K0 at the blank left end.
  - After every round-1 K0, state C reads a 0.
- **Round-2 end (class 10, crafted c = 80).** The only new-slot reads are J0 K0 twice at stage 90. The second K0 is
  followed by C reading a 1, two cells left of J0. That "K0 then 1" event is exactly H14's hook (N = C-clone with
  N1 = halt).
- **The hook needs a spare 1-slot.** A 13-state version must send K0 to a new state X with X0 acting like C0 and X1
  free. All of D1's new 1-slots (K1, L1, M1) are used by the fill loop.
- **s1 tested this directly.** It fixes K0 = 0LL and reserves L1. Its only survivors are delta-0 L12 clones such as
  K = 0LL1LM, L = 1RD---, M = 0LK0RC: L12 plus an H14 hook that never fires.
- **Consequence.** An H14-style hook costs one state. A 13-state H14 analogue therefore needs a 12-state k-robust
  delta != 0 eater.
- **The other delta-1 family (tier1's s3_1RI) fails too.** It is K = 1RI0LL, L = 0LM0LC, M = 1LL0LJ. Round 1 has an
  L0/M0 loop that plants '10' pairs leftward. Its round-2 end reads only J0, K1, L1 and K0, a subset of round 1's
  slots, so no spare slot exists there either.

## Scans (d13enum.py = t1enum + --keepfree reserved halt slot; kcheck at k = 29, 41)

| run | space | leaves | result |
|---|---|---|---|
| s1 | 13 states: J0 = 0LK, K0 = 0LL, L1 reserved; K1, L0, M0, M1 lazy; n = 41 | 193,857 (complete) | 0 HALT2. 26 delta-0 loopers; KFAIL c = 91/77/79 |
| s2 | 13 states: D1 core L1 = 1LM, M0 = 1RJ, M1 reserved; K0, K1, L0 lazy; n = 41 | 17,837 (complete) | 0 HALT2. 3 delta-0 loopers |
| e2r | 12 states: J0 = 0LK, K0 = 0RH..1RL (the part e2_a never reached); n = 41 | 136,301 (complete) | 0 HALT2. 12 MAX2 restarters (below) |
| clone13 n41 | one-state clone splits of the 12 MAX2 restarters, all slots, 220 stages | 12 bases | 3 HITs, all depth artefacts |
| clone13 n77 | the same for the 11 depth-robust bases, 260 stages | 11 bases | 0 (no variant even restarts) |
| n77 | 12 states: J0 = 0LK, all 48 K0 subtrees, n = 77 | 192,048 (complete) | 0 HALT2. MAX2 = the same 11 restarters |
| j1 | 12 states: J0 = 1LK at n = 77, K0 = 0RL and 1RL complete, 1RK stopped at 3,800 | 40,570 | 0 HALT2. 13 MAX2 restarters (c = 43, 42, 49, 41) |
| clone13 j1 n77 | one-state clone splits of the 13 j1 restarters | 13 bases | 3 std HITs (C13a / C13b family); the halt is a U = 19 artefact under the big policy |

## Side result: 12-state accumulator-sized restarters with delta far from 0 (J0 = 0LK, all slots used)
- The six families are:
  - 0RK1RL_0LI1RK
  - 0RL0LC_0RK0RA and 0RL1RD_0RK0RA
  - 1LK1LL_1LK0RA, 1LL0RA_0RL1LK and 1LL0RA_1LL1LK
  - 1RK1LL_0LI1LK
  - 1RL1LK_0RD0RJ and 1RL1LK_0RD1RL
  - 1RL0RC_0RK0LA and 1RL0RC_0RK0RA
- Each string is the K_L part; the base is n1 with J = 0LK0LC.
- **Restart counter (scalechk.py).**
  - In std the counter is c = 41, 47, 49 or 55, the same for every k and n. A prefix of 2s left of the round start
    grows with k.
  - Under the big policy (R = 2539) the counter is c = 5081, 5087, 5089 or 5095, i.e. 2R + 3, 9, 11 or 17.
  - 0RL0LC_0RK0RA gives 6769 = (8R-5)/3.
  - So these are genuine accumulator-reloaded rounds. Round-2 classes are 13, 5 and 7 mod 14.
- **Round 2.** No further restart and no free slot within 110 stages (MAX2), and no single clone-split hook works
  (clone13 at n = 41 and n = 77).
- This is relevant to inv-w2-inplace. It is the J0 = 0LK analogue of P11's counter 2R-3. I did not check whether
  these restarts are in place.

## Rejected hits (depth artefacts)
- **Base:** `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0RL0RH_0RK0RA`.
- **Clones:** J0 -> 0LM with M = 0RL---; H0 -> 1LM with M = ---0LB; K1 -> 0RM with M = ---0RG.
- **At n = 41:** restart c = 49 at stage 14, then HALT at stage 35, for k = 17, 29 and 41.
- **At n = 329 and 371:** the base never restarts (MAX at 120 stages), so all three are discarded
  (scratch/val_hits.txt).

## Not done
- Direction 4 (a targeted eater search for delta 2/6, where '1' at gap 2 gives class 11 and '10101' at gap 2 gives
  class 1) was not run as a separate search. The reserved-slot trees accept any delta, and every k-robust
  delta != 0 restarter they produced is listed above.
- s3 (K0 = 1LL with L1 reserved) was not run, because the s1 lesson made it low value.
- The full J0 = 0RK and J0 = 1RK 12-state trees were not run (inplace's ienum covers their in-place part).

## Tools (d13/)
- slotctx.py: per-stage reads of chosen slots, with context.
- d13enum.py: t1enum plus --keepfree and --stopat.
- validate.py: std k x n grid, plus --big for the eater.
- scalechk.py: restart counter under std, n = 329 and big policy (CASES env).
- val3.py: crafted round-2 starts of the C13a family (prefix, c, z, k sweep).
- stagelog.py: per-stage K summary.
- queue*.sh: resumable sequential runners. Also copied from tier1: clone13, kcheck, kscan, val2, ntrace and others.

## Recommended next steps
0. **The C13a eater (J0 = 1LK, counter 2R+5) is a clean round-2 reloader.** Any Tier-1 use of it needs a hook that
   fires at the round-2 END itself, decided by fixed residues (counter class 1 mod 14, k class, depth class). A hook
   reached after the mini-round chain does not count. Screens must vary U, as the verifier's rtest.py/ures.py do.
   Old step: **Verify C13a independently.** Use your own simulator. Check the round-1 eater at large k with big policy and
   bigk >= 3. Then follow the round-2 end abstractly (event rules), since the big literal is infeasible. Also finish
   the j1 tree (J0 = 1LK at n = 77): its other K0 subtrees may hold more 2R+c families, and C13a-type hooks may
   exist with c in other classes.
1. Re-screen tier1's n = 41 trees (b3, d1c, d1c2, e2_b) at n = 77. The n = 41 results can miss eaters that only work
   in the real depth class.
2. A 13-state D1-type halter needs a 12-state k-robust delta != 0 eater. C13a is one such case. The J0 = 0LK space has only the 2R+c
   families above, and they are not hookable. The remaining 12-state places are J0 = 1LK (j1, partial) and the
   non-in-place parts of J0 = 0RK and 1RK.
3. The D1 core itself is exhausted for 13 states. C13a is not a live candidate: its halt was not supported under U variation.
