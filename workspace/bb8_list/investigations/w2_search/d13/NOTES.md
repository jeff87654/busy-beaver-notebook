# d13: 13-state D1-mechanism Tier-1 search (inv-w2-d13, Opus, 2026-10-10)

## Setup
- Tools copied from tier1/ (t1lib, t1enum, droptest, kcheck, kscan, clone13, ntrace, val2, remnant, prefix_table,
  base_table, j0view).  New: slotctx.py (every read of chosen slots per stage, with context), d13enum.py (= t1enum +
  --keepfree S: a reserved halt slot; reading S in round 1 or in kcheck prunes the branch (leaf KF1); reading it in
  phase >= 2 = HALT2 = Tier-1 hit; + --stopat).
- Speed: n = 41 ~150 leaves/s early in a tree, n = 329 ~7x slower.  Scan at n = 41, re-validate hits at
  n = 329/371/2849, k = 29/41 std, k = 77/137 big (depth caveat from inplace/NOTES.md: real depth class 35 mod 42).

## D1 slot anatomy (slotctx.py, k = 17, n = 41)
- Round-1 eater reads only: stage 0: J0 K0 | J0 K1 L0 K0; stage 7: 3 x (J0 K1 L1 M1 M1 M1 M0) = the fill loop
  (J0 at p with 1s at p-1..p-3 -> write 1 at p, J at p+1); stage 12: J0 K0 at the blank left end.
  After every round-1 K0 (state C next) the cell read is 0.
- Round-2 end (crafted round start c = 80, z = 415, d1_round2_c80.txt): new-slot reads only at stage 90:
  J0@3147 K0@3146 (then C reads 0), J0@3141 K0@3140 (then C reads **1**).  This "K0 then 1" 2-gram is exactly H14's
  hook (N = copy of C with N1 = halt; H14 halts there).
- So a 13-state version needs K0 -> a new state X whose X1 is never read in round 1 (and X0 acts like C0 = 1RD there).
  In D1 every new 1-slot (K1, L1, M1) is used by the fill loop, so the fill loop must be rebuilt with one fewer 1-slot.

## Scans
- s1 (started ~19:45): J0 = 0LK, K0 = 0LL, L1 reserved (halt), K1/L0/M0/M1 lazy.  s1_K0LL_L1free.{tsv,log}
  Design: L0 must play C0's role after K0 in round 1; K1 must not lead to L reading a 1 (the D1 fill loop's L1 step),
  so the fill loop has to be rebuilt from K1/M0/M1 (+L0).  Tree size ~50 L0 subtrees x 2-3.5k leaves.
  Early: 2 RESTART4 leaves with L1 never read (..._0LL0LM_0LJ---_0RM0RC, ..._0LL0RM_0LJ---_0RM0RC): delta 0, identical
  rounds (c = 79 every round), so no halt.
- Hook alternatives considered: K0 = 1RI (s3_1RI family) or 0LC send the head into base state C at p-2, so the hook
  cell is read by a base slot; only K0 -> new state (0LL / 1LL, TNF) can put a free slot on the hook cell.
- queue.sh (sequential after s1): s2 = D1 core (L1=1LM, M0=1RJ) with M1 reserved (direction 1); s3 = K0=1LL with L1
  reserved; e2r_* = the unscanned K0 values of the 12-state J0=0LK tree (e2_a stopped at K0=0RH): any 12-state HALT2,
  or a k-robust delta != 0 restarter to clone-split into 13 states.
- validate.py M: std k = 17/29/41 x n = 41/329 (+371, 2849) full follow; --big eater at k = 17/77/137.
- **s1 DONE (20:28): 193,857 leaves, 0 HALT2, 0 MAX2.** Restarts: 26 RESTART4 all delta 0 (c = 79 every round);
  KFAIL c = 91 (71), 77 (15), 79 (7).  Telling survivor: K = 0LL1LM, L = 1RD---, M = 0LK0RC (+ L0/M variants) =
  L12 with an H14-style C-clone hook on K0; it never fires because delta = 0.
  LESSON: an H14-style hook (K0 -> C-clone) costs a whole state, so a 13-state H14 needs a 12-STATE k-robust
  delta != 0 eater (J0 + 2 states).  K0 = 0LC is fully covered by e2_a (delta 0 only) -> the e2_a remainder
  (other K0) is the remaining place to look; queue reordered (queue2.sh: s2, e2r_*, s3).
- **s2 DONE (20:32): D1 core (L1=1LM, M0=1RJ) with M1 reserved, K0/K1/L0 lazy: 17,837 leaves, 0 HALT2.** Restarts:
  3 RESTART4 all delta 0; KFAIL c = 91 (k=17 accidents) and c = 79.  Direction 1 (the M1-free subtree) is closed.
- tier1's second delta-1 family (s3_1RI: K = 1RI0LL, L = 0LM0LC (L1 in {0LC,0RJ,1LF,1RI,1RM}), M = 1LL0LJ):
  slotctx k = 17: stage 0 has an L0/M0 loop that writes '10' pairs leftward (pattern planting), then M1 -> 0LJ;
  stage 7 reads J0 K1 L1 once; stage 11 J0 K0 at the blank end.  Round-2 end (crafted c = 80): reads only J0, K1,
  L1, K0 (a subset of round 1's slots, L0/M0/M1 never) -> no spare-slot hook in this family either.
- queue3.sh (20:35) replaced queue2: rest of e2r (J0=0LK, 12 states), e2_b remainder (J0=1LK, K0 >= 0LL), full
  12-state trees J0=0RK and J0=1RK, then s3.  A 12-state k-robust delta != 0 eater would be the seed for a 13-state
  H14-style clone hook (clone13.py).
- **e2r DONE (21:05): 12-state J0=0LK, K0 in 0RH..1RL (29 subtrees, n = 41): 136301 leaves {'HALT1': 2839, 'NORESTART': 124801, 'W': 5779, 'T': 2705, 'KFAIL': 94, 'RESTART4': 71, 'MAX2': 12}, 0 HALT2.**
  With e2_a (K0 0LA..0RG) the 12-state J0=0LK tree is complete at n = 41.  0 twelve-state Tier-1 halters.
- e2r MAX2 restarters (12, all slots used, 6 families) are ACCUMULATOR-SIZED (scalechk.py): std c = 41/47/49/55 for
  every k and n (prefix of 2s grows with k), big policy (R = 2539) c = 5081/5087/5089/5095 = 2R+3/9/11/17, and
  0RL0LC_0RK0RA: 6769 = (8R-5)/3.  Round-2 classes 13, 5, 7 mod 14.  They never halt (no free slot).
- clone13.py (--xs all, 220 stages) on all 12: 3 HITs, all on base ..._0LK0LC_0RL0RH_0RK0RA (J0 -> 0LM with
  M = 0RL---; H0 -> 1LM with M = ---0LB; K1 -> 0RM with M = ---0RG): restart c = 49 at stage 14, HALT at stage 35,
  k = 17/29/41 (n = 41).  BUT at n = 329 and 371 (real depth class 35 mod 42) the base never restarts (MAX@120):
  DEPTH ARTEFACT, discarded (scratch/val_hits.txt, clone13_e2r.txt).
- Depth class matters for J0 trees too: n = 41 vs n = 77 on the same 1585-leaf J0=1LK prefix gives different leaves
  (n = 77 finds a RESTART4 that n = 41 misses).  So n = 41 scans (all of tier1's and mine) have false negatives as
  well as false positives.  n = 77 (= 35 mod 42) costs ~1.7x n = 41.
- queue4.sh (21:11): 12-state J0=0LK tree redone at n = 77, K0 subtrees in a priority order (0LC 0LA 0LB 0LL 1LL
  0RL 1RL 1RK 1LK 0RK ...).  queue3 (e2b remainder, J0=0RK/1RK, s3) was stopped before it produced anything.
- (21:12) killed queue4 (an over-broad Stop-Process pattern also killed my shell; nothing lost but the n77_0LC
  prefix).  queue5.sh = resumable (skips DONE subtrees).
- **clone13 at n = 77 (real depth class, 260 stages, --xs all) on the 11 depth-robust accumulator-sized e2r
  restarters: 0 variants restart at all (every eater-slot clone's undefined symbol is read in round 1; base-slot
  clones halt at once).  Negative.** (clone13_n77.txt)
- **n77 rescan DONE (22:08): 12-state J0=0LK tree, all 48 K0 subtrees, n = 77 (real depth class): 192,048 leaves,
  0 HALT2.** {HALT1 4000, NORESTART 175520, W 8305, T 3999, KFAIL 124, RESTART4 89 (delta 0), MAX2 11}.  The 11
  MAX2 = exactly the depth-robust accumulator-sized e2r families (the n = 41 artefact base is gone).  R1 counters seen:
  79 (116), 91 (32), 88 (28), 77 (15), 46 (13), 40 (9), 48 (8), 41/60 (4), 49/55 (3), 47/54 (1).
- queue6.sh (22:10): 12-state J0=1LK tree at n = 77 (priority K0 order), run until the time budget ends.
- j1 (12-state J0=1LK, n = 77): K0 = 0RL (18,241 leaves, DONE) and 1RL (18,529, DONE); 1RK stopped at 3,800.
  13 MAX2 restarters, new classes: c = 43 (= 2R+5, class 1 mod 14) on 1LK0LC_0RL{0LB,0LH,1RC,1RJ}_0RI0RK,
  c = 42 (class 0) on 1LK0LC_1RL0RA_{0RB,0RG,1LH,1RH}0RK, plus the 2R+11 / 2R+3 families.
- **clone13 n77 on the 13 j1 restarters: 3 HITs, on the c = 43 family (bases ..._1LK0LC_0RL1RC_0RI0RK and ..._1LK0LC_0RL0LB/0LH_0RI0RK).**

## TIER-1 SCREENING CANDIDATE (13 states): C13a
C13a = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LK0LC_0RL1RM_0RI0RK_1RD---
  (12-state base ..._1LK0LC_0RL1RC_0RI0RK with K1 = 1RC redirected to M = copy of C (M0 = 1RD) with M1 = halt:
  exactly the H14 C-clone hook, now on a 12-state eater)
Sibling C13b = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LM0LC_0RL0LB_0RI0RK_0RL---
  (J0 = 1LM, M = copy of K with M1 = halt) and the same with L0 = 0LH.
- Mechanism: J0 = 1LK at n1's halting config; the eater turns the far D2 run into a prefix and keeps the old
  accumulator: round 2 starts as '2^(k-4) 1 5 (R-2) 2 5 1^(2R+5) 0^3 9 1^z' (c2 = 2R+5, class 1 mod 14).
- Real start b0 = 6 (std, C13a_b6_std.log): n1's round 1 stages 0-36, eater 37, restart 38 (c = 43), counter
  exhausted at 58, round-end 59-61 (left event '7 1^32'), HALT M1 at stage 62.
- Robustness (std, validate.py): restart c = 43 at stage 1 then HALT M1 (C13a @25, C13b @31) for (k,n) = (17,77),
  (29,77), (41,77), (77,77), (17,329), (29,329), (41,371), (17,2849).
- Big policy (scalechk): restart c = 5083 = 2*2539+5 for k = 17, 77, 137 (prefix 2^(k-4) 1 5 2537), no round-1 halt.
- Round-2 end residue sweep (val3.py, std; crafted '2^(k-4) 1 5 p 2 5 1^c 0^3 3 1^z|1|19'): ALL halt at M1 just
  after round 2's left event, halt stage = 25 + 18(c-43)/42 (linear in c = after exhaustion), for c in
  {43,57,71,85,99,113,127,169,211} (class 1 mod 14, all residues mod 42 hit: 1, 15, 29), z in {84,330,1001},
  k in {17,29,77}, p in {17,59,101,1277,2537,5057}.  C13b: 6/6 halt likewise.
- Big-policy round-2 end: literal stage timeout (T) at stage 20 (> 4e9 steps), infeasible, as for H14.
- Grade: 2 full rounds, round 2 reloaded from the accumulator (2R+5): sigma >~ f_(omega+1)(f_(omega+1)(~2^^363)),
  Tier 1, 13 states.  Screening evidence only.

## C13a/C13b DOWNGRADED (after lead's U = 19 warning, h14verify/REPORT.md)
- The std halt is 4 stages after round 2's counter runs out.  Real-start log stages 58-62: the depth list 1^497
  becomes (2 0 3)^m (stage 59), then ~6.6k far bits plus a U-derived list 1^31 (stage 60), then left event '7 1^32',
  then HALT M1 during the unpack.  The relative order (U-sized list vs depth-sized far region) is reversed in std.
- bigend.py (crafted round-2 start, big policy U = 2539, cap 6e10): stages 0-19 identical in shape to std; at the
  round end (20-21) far grows to ~281k-301k bits and a mini-round chain follows ('5084 5 0^3 9 1^10' at stage 28,
  '2 5 0^3 9 1^6' at 31).  NO left event and NO halt through stage 29 (C13a) / 35 (C13b).
- So the std halt is a U = 19 artefact (same failure as H14).  C13a/C13b halting is OPEN, not supported.
  Confirmed parts: round 1 = n1 (exact), eater + restart with c2 = 2R+5 (std + big policy, k = 17..137, n = 77..2849),
  full round 2 (std).
