# n1 w+2 slice: notes (Opus investigator, 2026-10-09)

## Tools (this dir)
- sim.py: Python literal simulator (any #states), far_of(k) = (10101)^k + 44-bit tail, word_of(tokens).
- gstage.cpp/.exe: stage35g generalised to <= 16 states (server protocol identical; U mask 64-bit).
- nfol.py: follower (copy of ord_run.follow) on gstage; --start "0 1^60 1 19" --fark K for constructed starts.
- fstep.py: one follower stage as a function; genum.py: follower-level lazy TNF enumeration (slow, ~4 nodes/s).
- gtrace.cpp/.exe: literal tracer (prints reads of chosen slots, stops at HALT / K-moment).
- lenum.cpp/.exe: C++ literal lazy TNF enumeration of J0 + NS new states from a start tape, leaf = first K-moment
  after the first J0 read (prints far ones, ntok, leftmost-1 offset vs the list start, nearest tokens).
- per.py: Per-pattern ('2^x 5 1^m 0') detector.

## Facts established
- Halting-stage J0 tape (far_k + [0 1^n | 1 | R], state G at the right end): HALT J0 at tail idx 22 (k-independent
  steps). Left: D2^k + tail[0..21] = '1011010101010101001000'; right: z2 D0^4 z2 D0 z2 D0 z2 D0 z2 D(2R+4) z2 D1^(n+2).
  The walk: E0 at tail idx 25 (first E0 read of the stage), I1 at 24, I0 at 23, J0 at 22.
- Divergence with the no-far world: same run until step 4181 (state C at list-start-3 reads the tail's last D0 instead
  of blank). WITHOUT far bits the base restarts a full new round by itself (literal + follower, start "0 1^60 1 19",
  no far): [7 1^140] -> [2 5 1^79 0^3 9 1^138] -> normal periods (counter 79 = 4*19+3 with r rep 19), depth kept.
  So the far region (D2^k + tail) is exactly what turns n1's restart (G6-like infinite rounds) into a halt.
- The no-far restart unpacks the accumulator LEFTWARDS (~6R cells): any far structure must be erased completely
  before that (and nothing can be stored there across rounds).
- Junk residues (b0 = 11, 16, 21): after exhaustion the run enters a 16-stage cycle with constant growth (+6 zeros per
  cycle), far region partly eaten; never reads J0; not a round restart.
- 10-state J0 completions (40): none restarts a proper round (some convert the cleared list into a counter in place
  every couple of periods: 1RC, 1RD, ...; depth restarts at ~2; messy).

## 2026-10-09 midday
- genum.py ns=1 (follower-level, start far_5 + [0 1^60|1|19], 40 stages): 2828 leaves; restarts seen are 'in-place'
  (the depth list becomes the new counter, depth resets to ~2; e.g. J0=0LK K=0LF---); messy, counters split.
- KEY OBSERVATION: J0=0LK, K=0LA0LC (11 states, no halt) from far_5 + [0 1^60|1|19] eats the far region in two
  J0-passes (3 D2 per pass; the remnant becomes digit tokens that the champion process consumes), then the borrow
  reaches the blank left end and the base performs n1's OWN no-far restart: [7 1^168] -> [2 5 1^79 0^3 9 1^166]
  (counter 79 = 4r+3, depth kept) -> a full clean round 2 (12 periods, identical to round 1) -> round-2 end J0 ->
  eating starts again but with k = 17 leaves junk (no clean round 3).  Works only for k = 5 (k = 2,3,4,6,7,8,11,14,17
  fail): an accident of the remnant shape, not a periodic eater.
- lenum literal screens (ns=1 1805 leaves, ns=2 >23k leaves, k=4 n=5): no leaf reproduces the no-far K-moment
  [2 1^89] directly (expected: the clean restarts go through several follower stages).
- genum3.py: multi-k clean-restart search (pass = for every k in 5,2,3,4,6,7,8,9,10,11 the follower reaches a K-moment
  with NO far bits and tokens '2 5 1^m', m >= 50, within 32 stages).  ns=1: 3433 nodes, 0 pass (none passes 3 k's).

## 2026-10-09 afternoon: CLEAN-ROUND LOOPER FOUND (12 states, no halt)
L12 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK0RC
  (J0 = 0LK, K = 0LC1LL, L = 0LK0RC; all slots defined)
- From the real start (b0 = 6, follower std): rounds start at stages 0, 47, 94, 141 with the IDENTICAL n1 round start
  [2 5 1^79 0^3 9 1^n], depth n = 32 -> 472 -> 912 -> 1352 (log L12_b6.log).  Each restart = n1's own no-far restart
  (left event at blank -> H): counter 4R+3 from the left-event accumulator R, depth kept.
- Eater mechanism: one J0 pass converts most of the far D2 run into a few big DIGIT tokens (k=17: 2^10 -> '26 33'),
  which the champion process consumes by full clears; then '7 1^N' -> left event -> clean restart.
- k-scan (start far_k + [0 1^30|1|19]): clean restart at stage 10 for every k = 1,2 mod 3 with k >= 7 (k = 3, 4 too),
  junk (no restart in 120 stages) for k = 0 mod 3.  Real class: k = 17 (follower) = 2 mod 3.  Depth scan n = 28..37: all
  clean.  R in {19, 22, 25, 2539} (literal start accumulator): same restart (the counter comes from the later left event).
- Rounds are identical mod 10080 (counter 4R+3 with R = 19 mod 2520 every round), so k_end = 17 every round: L12 never
  halts.  f_(omega+2)-SHAPED (u_(i+1) ~ f_(omega+1)(u_i)), the n1 analog of G6.
- 11-state sibling J0=0LK, K=0LC1LJ (L unused): clean restart with counter 91 (R-class 22): round 2 runs (7 periods)
  and ends in a JUNK class (91 = 7 mod 14, n1's halting class needs 9 mod 14): b11-type junk, no halt.
- Tier-1 route identified: the round-2 counter class c2 = 4R+3 depends on the restart's left-event accumulator class;
  k2 = 4(c2-9)/14 - 3.  If c2 = 9 mod 14 (J0 class) but k2 != k1 mod 3 and the eater HALTS for that k-class, the machine
  halts after exactly 2 rounds (f_(omega+1)^2).  Needs R = 12 mod 21 (k2 = 0) or R = 5 mod 21 (k2 = 1).

## 13-state multi-class restarter M13a (no halt)
M13a = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC0LL_0LA1RM_0RM0LE
- found by genum5 --ns 3 --fix K0=0LC (n = 41 start).  From far_17 + [0 1^41|1|19]: eater + restart at stage 20 with
  counter c2 = 142 = 2*depth - 52 (big policy: 13582 = 2*6817 - 52: DEPTH-sized counter, depth also kept);
  round 2 (counter class 2 mod 14) ends differently and restarts round 3 in place: '78 6 2 5 1^33 ..' (the D2 run became
  a digit 78 that stays as a prefix).  All 7 new slots are read by stage 14 (dropslot.py): no spare slot for a halt.
- cscan.py (round start [2 5 1^c 0^3 9 1^32|1|1], no far): M13a restarts for most counter classes c (14 of 42 tested
  values end in junk/MAX); restart counters vary (79, 142, 169, 179, 1689 (far-sized), 13, 11, ...).
- All restarting leaves found so far use every new slot (u = 0); no HALT after a complete restarted round.

## Wrap-up 2026-10-09 evening
Searches stopped (partial): g5s3_0LC 42239 leaves, g5s3_0LA 80089, g5_0LK 13459, g5_1LK 11112: 0 HALT after a restarted round. REPORT.md written.

## Exact coverage of stopped trees (for other agents; all genum5, J0 = 0LK, TNF new states, leaf caps: --stages 120,
## --cut 26/30 stages without a period signature, --maxs 2e7 steps per literal stage)
- g5_0LK: ns=2, fixed {J0=0LK}, start far_17 + [0 1^329|1|19], cut 30: 13459 leaves, DFS stopped inside K0=1R* options
  (last leaf printed in g5_0LK.tsv). 0 HALT-after-round.
- g5_1LK: ns=2, fixed {J0=1LK}, same start: 11112 leaves (partial, see tsv tail), 0 restarts.
- g5s3_0LC: ns=3, fixed {J0=0LK, K0=0LC}, start far_17 + [0 1^41|1|19], cut 26: 42239 leaves; covered K1 = 0LA..0LK fully,
  K1 = 0LL partially (stopped at L0=0LM, L1=1LM, M0=1LH); K1 = 0LM.. and 1***, 0R*, 1R* NOT covered.
- g5s3_0LA: ns=3, fixed {J0=0LK, K0=0LA}, same start: 80089 leaves; stopped at K1=0LL, L0=0RC, L1=0RM, M0=0LM.
- genum3/g3b (clean-restart multi-k, ns=2): partial, superseded (k-sets too strict).

## L12 scaling check (lead request, 2026-10-09 ~16:30)
verify_restart.py L12 --ks 17-17 --policy big --maxs 5e9: CLEAN restart at stage 10, m = 10159 = 4*2539+3, depth 13613
(std: m = 79 = 4*19+3, depth 173).  --policy shrink: identical (m = 10159, depth 13613).  The reload is
accumulator-sized (4R+3) and the depth jump scales with R; not a representative artefact.

## cs14 on M13a (14-state clone-splits, 52 variants, start far_17 + [0 1^41|1|19], 300 stages)
All base-transition splits halt at once (the clone's undefined symbol is read in normal operation).  7 variants (F0 u0,
G1 u1, H0 u0, L0 u1, L1 u1, M0 u1, M1 u1) never read the undefined symbol within 300 stages (MAX, same run as M13a).
0 variants halt after a restarted round.  Negative within this horizon.
