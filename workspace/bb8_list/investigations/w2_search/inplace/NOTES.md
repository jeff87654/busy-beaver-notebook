# In-place reload route (inv-w2-inplace, Opus, 2026-10-09/10): notes

## Tools (this dir)
- igstage.cpp/.exe: gstage + per-stage leftmost visited cell (LO), leftmost CHANGED cell (MW), leftmost 1 (L1) and the
  farthest-token cell (P), all relative to the stage's input word; optional left limit (job fields LLIM LVS): a change
  left of LLIM or a visit left of LLIM-LVS stops the stage with 'L'.  Built with C:/msys64/ucrt64/bin g++ -static
  (PATH must include that dir, else g++ silently produces nothing).
- ilib.py: follower stage on igstage with ABSOLUTE left tracking (abs 0 = the start word's first cell = the far
  region's left end); rsig() = round-start signature 'P 2 5 1^c 0^3 9 1^z'; follow(); CLI: python ilib.py M [--policy].
- rscan.py: from a no-far (or --far BITS) round start [P 2 5 1^c 0^3 9 1^z|1|1], follow to the next RSIG; per c.
- ival.py: follow machines from far_k + [0 1^n|1|R] under std/big and several k; RSIG list + min visited cell.
- dumpst.py: far bits + tokens at a given stage.
- ienum.py: lazy TNF enumeration (J0 + NS new states) with the left limit as a pruning leaf (LEFT); records RSIGs.

## Task 1: M13a restarts (start far_17 + [0 1^41|1|19])
- Round-2 restart (stage 20, counter 142 std / 13582 big): NOT in place.  It writes 230 cells (std) / 20394 cells (big,
  ~3*depth) LEFT of the far region's left end (log m13a_std.log; big run in this session).  The counter is
  2*depth-52 and the depth before the restart is itself accumulator-sized (big: 6817 vs std 97), so the round-2 counter
  IS accumulator-sized; but it is laid out by a leftward unpack over the far region (far erased).
- Round-3 restart (round-2 end, stage 86 std): in place (leftmost visit 1 cell left of round 2's word start), counter
  c3 from round 2's OWN D2 run: rscan c = 100,114,128,142,156 (class 2 mod 14) -> P = [54,18],[62,14],[70,10],[78,6],
  [86,2], c3 = 21,25,29,33,37 = 21 + 4(c-100)/14 (~ 2c/7); c = 170 junk.  Not accumulator-sized (c3 ~ 0.29 c2).
- Round 3 (c3 = 33, class 5) is NOT a real round: after 2 periods it degenerates into the known growing-far junk cycle
  (stage 15 on: '1 3 1^2 0 1^2 7 0 3 ...' 8-stage cycle, far +202 bits per cycle).  Big policy for the round-2 end: JF.

## P11: an 11-state IN-PLACE accumulator-reloaded restarter (found by ienum ns=1, J0=1RK)
P11 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1RC---  (J0=1RK, K=1RC---, K1 never read)
- From far_17 + [0 1^41|1|19]: stage 7 RSIG 'R 2 5 1^(2R-3) 0^3 9 1^37' (std 19/35, big 2539/5075, also big k=77,137,
  std k=17..101): the old accumulator R stays as a prefix digit, counter 2R-3 = accumulator-sized.  The head NEVER
  visits a cell left of the far region's left end (minlo = 0 in every stage, std and big): fully in place.
- Mechanism: J0 (tail idx 22) -> 1RK -> K0 1RC writes two 1s into the tail; the base then treats tail + part of the
  D2 run as list digits; the eater-like stages 1-6 leave an R-sized junk block (100000)^~R in the far region; stage 7
  is a copy loop that reads J0+K0 once per junk block and builds the counter 1^(2R-3) to the right.
- Round 2 (c = 2R-3, class 7 mod 14) runs fully (std stages 7-21), ends WITHOUT a J0 event: the base borrows from the
  prefix digit (19 -> 16; big 2539 -> 2536), then the gadget copy loop restarts round 3 (stage 25) with c = 2R+3
  (std 41, big 5081: accumulator-sized again), in place.  Round 3 (class 13) ends in n1's constant-growth junk cycle
  (8-stage cycle, far +~6R per cycle, only base slots read) -> P11 never halts.
- k-grams (kgc.py, kmax 4, k = 17/29/41): the round-2 end (stages 22-25) and the round-3 end (42-47) contain NO slot-read
  k-gram absent from earlier stages (181 grams in total).  So no clone-split hook of <= 3 clones fires only there.

## ienum ns=2 (12 states), J0 = 1RK (running) and J0 = 0RK (stopped at ~22k nodes, K0 up to 0RL)
Start far_17 + [0 1^41|1|19], left limit: change < abs -8 or visit < abs -12 = LEFT leaf.  Leaves so far (1RK ~29k
nodes, 0RK ~22k): mostly NORS (no restart within 40 stages); LEFT ~2-2.5k; RS4 (4 restarts) ~190 / ~190.
**0 HALT leaves after a restart** (no free slot is read after an in-place restart in either tree).
Class-9 in-place accumulator-reloaded restarters (infinite rounds, all slots used, 12 states):
- Q12a = ..._0LJ0LI_1RK0LC_0RL0LB_1LE1LJ: restart at stage 4 (!) 'P 2 5 1^(2R-1) 0^3 9 1^z' (std c=37, big 5077),
  P = '3 1 0 R' rebuilt every round, rounds every 23 stages (std), depth +135 per round; minlo = 0 (never left of the
  far's left end); the far grows by ~79 bits (std) per round: each round deposits [its D2 run remnant + old prefix].
- Q12b = ..._0LJ0LI_0RK0LC_0LL1RC_0LK0LC (and 2 siblings): c = 23 std / 3383 big (~4R/3), class 9, P3, minlo = -1.
- ..._0RK0LC_0RL0RK_0LD0RK: c = 79 std but 103 big -> NOT accumulator-sized.
- kgc.py Q12a (normal 0-20, special 21-27 = round-2 end + restart, k = 17/29/41, kmax 5): 0 special-only grams
  (309 grams in total).  Rounds are locally identical: no clone hook.

## Structural observation (in place => blind to the left)
An in-place restarter (minlo = 0) never reads anything left of the far region's left end, and the round-end event
(J0 at the round's tail) has the round's own D2 run (k_i ~ 0.29 c_i, R-sized) plus every older round's deposit between
it and the far left.  So a far-left marker survives trivially (P11, Q12a, Q12b: never visited), but nothing in the
machine can read it: a d parked there needs a walker across R-sized, '00'-containing junk and back (>= 3 states on
top of the 1-2 restart states).  Tier 1 on these bases needs a locally distinct round-2 end, and kgc finds none.

## DEPTH CAVEAT (new, important for every gadget screen)
The real round-1 end depth (cleared list) is in class 35 mod 42 (b0=6 real start: std 329, big+ctrim 37289), NOT 41.
ienum/kscan at n = 41 (also genum5 ns=3's start) is the wrong class.  Gadgets that eat the depth list (geometric
mini-rounds n -> ~0.58 n) are depth-FRAGILE: e.g. H13b = ..._1RK0LC_0LL1LG_1LM0LL_1RK--- halts after an R-sized
round from the real start (std, stage 116) and at n = 329, but halts with no restart at n = 77..497, 2849.
Required re-tests for a hit: n in {329, 371, 2849} and k in {17, 29, 41} std, big k in {17, 77, 137}, real start.
(robust.py does the std part.)

## Hook scan at the real depth (kscan2.py, n = 329) + robustness (robust.py)
83 real-round restarters (from the ns=2 trees) re-run at n = 329; special-only grams in the round-2 end window;
then robust.py keeps machines whose first two RSIGs agree for (k,n) = (17,329) (17,371) (17,2849) (29,329) (41,371).
Robust + 2-gram hook: family J0=1RK, K=1LK0LL, L=0LI.. with gram L0,I1.

## H13c: TIER-1 CANDIDATE (screening)
H13c = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1LK0LL_0LM0LA_0LJ---
(base F12 = ..._1RK0LC_1LK0LL_0LI0LA; M = clone of I with M1 = halt, entered from L0 only: halts iff 'L0 then I1').
- far_k + [0 1^n|1|19], std: stage 4 in-place restart '0 10 0^3 (2R+3) 2 5 1^c2 0^3 9 1^n', c2 = 22 (std) / 3382 (big)
  = (4R-10)/3 (accumulator-sized; class 22 mod 42 = 8 mod 14 for every R = 19 mod 2520), depth kept; round 2 runs
  stages 4-14 (counter 22 -> 0), round-2 end (class 8 = J0 on another tail) -> L0,I1 -> HALT M1 at stage 16.
- Same for k = 17/29/41 and n = 35, 77, 329, 371, 413, 2849 (std).  minlo = 0 (never left of the far region).

## H13c validation (all follower screening)
- real start b0=6 std: n1 round 1 (J0 at stage 37), in-place restart at stage 41 (c2 = 22, P6), HALT M1 at stage 53.
- real start b0=6 big (realbig.py: the R-sized restart counter trimmed to its class mod 42): restart at stage 41 with
  c2 = 3382 (z = 37298), HALT M1 at stage 53.  (A plain ctrim=41 run trims the round-1 counter 79 -> 37, k1 -> 5:
  unfaithful, gave HALT without restart; do not use small ctrim on round 1.)
- constructed std k = 17/29/41, n = 35/77/329/371/413/2849: restart stage 4 c=22, HALT M1 stage 16.
- constructed big (ctrim 41) k = 17, 77, 137: restart c = 3382, HALT M1 stage 16.
- round-2 counter sweep (rscan from the stage-4 word, prefix kept): c2 = 22 + 42j, j = 0..9 std -> HALT M1 at the end
  of the round (stage 12 + 18j); big j = 0, 2 -> HALT (12, 48), j = 4 T (time limit).
- marker.py: markers 1, 11, 101, 1101, 10101, 111 at gaps 1-4 left of the far region: same outcome, leftmost changed
  cell = far + 28 (H13c), +18 (P11), +58 (Q12a, 3 restarts): markers survive untouched.

## Other hook candidates (rejected)
- H13a (..._0LL0RC_0LK0LM_0LL---, L1,K1) and H13b (..._0LL1LG_1LM0LL_1RK---, L0,J1): depth-fragile.
- G12a = ..._1RK0LC_1LK1LL_1RI1LG hooks E0,I0 / G1,G1 / L1,G1: fire in the restart-1 stage (kscan window overlapped
  the first restart stage when s2 - s1 < s1 + 3) -> halt before any RSIG.
- B family ..._0RK0LC_0LK0LL_1LL1LF hooks K1,L1 (H13d) / L1,F1 (H13e): std halts after the c=26 round, but big
  (c = 3386, prefix R-sized: P3393) restarts again at stage 21 instead of halting -> std artefact.
- ..._0RK0LC_0RL0LD_0RK1LD hook L0,K0: RSIG c=49 with z=0, first-restart stage varies with n -> fragile.

## 12-state halters inside the ienum trees (found at the end of the 1RK tree)
13 leaves HALT after a restart, family J0=1RK, K0=0RL (e.g. T12a = ..._1RK0LC_0RL---_0RF---, halts L1):
restart at stage 14 c = 19 std / 3379 big = (4R-19)/3, class 5 mod 14; HALT at stage 26 (round-2 end eats the depth
list into the far region first).  std: k = 17/29/41, n = 41/329/371/2849 all HALT L1@26; real start std: restart 51,
HALT L1@63.  Big: round-2 end stage 23 needs > 3e9 steps (T); re-run with 4e10 (t12a_big.log).
- Affine fit (big, bigk = 1/2/3): T12a c2 = 3379/6739/10099 = (4R-19)/3; H13c c2 = 3382/6742/10102 = (4R-10)/3.
- T12a sweep with 3e9 steps: c2 = 313, 397 -> HALT L1 at the round end (stages 137, 173).
- T12a real start big (realbig): restart 51 c2 = 3379 z = 40674; round-2-end stage > 6e10 steps (T); re-run 5e11.
- T12a real start big (5e11 steps): restart 51 c2 = 3379 z = 40674, HALT L1 at stage 63 (= std).

## Follow-ups after the lead's messages (fixed-U warning, D1)
- T12a big k=137: HALT L1@26 (c2 = 3379).
- order.py (size-order test, U raised to 19+2520*20 for the last period): H13c HALT M1@16, T12a HALT L1@26, same
  paths.  Both halts are direct (H13c) / one absorption pass (T12a); no mini-round chain.
- D1: restart 1 writes 184 (std) / 20344 (big) cells left of the far (not in place, c = 4R+4); later phase in place,
  prefix survives; counters depth-derived and shrinking (like M13a round 3).  Subtrees not enumerated (d13 owns them).
