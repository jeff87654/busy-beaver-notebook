# Route 2: prefix digit as outer counter d with a class-invariant borrow (inv-w2-borrow, Opus, 2026-10-10)

Tools copied from inplace/ (ilib.py, igstage.exe, rscan.py, ...). New: rtab.py (round-end class table from a crafted
round start far + [P 2 5 1^c 0^3 9 1^z|1|1]).

## Task 1: P11 dissection
P11 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1RC---
- Std run (ilib follow, far_17 + [0 1^41|1|19]): stage 7 RSIG P=[19] c=35 z=37; round 2 ends stage 21
  '19 2^9 5 1^5 0^2 41 1^146'; stage 22 '16 8 2 5 1^3 0^3 1 4 1^2 0^3 1 35 2 5 0^3 9 1^144' (borrow 19->16);
  stage 24 folds everything into the far region (448 bits, ends in a (100000)^~19 junk block); stage 25 copy loop
  restarts with P=[16 8 2 5 1^3 0^3 1^2 5 1 0 2 1^20 0 18] c=41 (class 13) z=142.
- rtab (std, far = P11's stage-7 far, P=[19], z=37), c = 35..48:
  7 -> borrow (19->16), next c=41 (13);  8 -> NO borrow, P=[19] kept, next c=35 (7!), z=143;  9 -> P=[19] c=35 z=0;
  10 -> P=[4 45] c=7; 11 -> long junk prefix c=9; 12 -> c=26; 13, 0, 3 -> no restart in 120 stages;
  1, 4, 5 -> P=[4 45] c=7 z=7; 2 -> P=[16 24 33] c=6; 6 -> junk prefix c=36.
- Borrow vs prefix value (std, rtab --Ps): class 7 (c=35): d -> d-3 for every d >= 2 (d = 2 leaves '8 2 5 ...'), the
  rest of the new prefix is fixed junk '8 2 5 1^3 0^3 1^2 5 1 0 2 1^((4U-16)/3) 0 (U-1)', counter 2U+3 (class 13).
  d = 0, 1: no borrow ('4 45' junk round).  Class 8 (c=36): the old prefix is folded into the far region (far grows
  2d bits) and the new prefix is [U] (fresh accumulator), counter 2U-3 (class 7): a round-1-like restart.
- Big policy (U = 2539, c = 35/36 so k = 9): same: class 7 -> P=[16 8 2 5 1^3 0^3 1^2 5 1 0 2 1^3380 0 2538] c=5081;
  class 8 -> P=[2539] c=5075.  Class 12 -> c = 3386 = (4U+82)/3 junk prefix.
- The borrow is BASE behaviour: n1 itself (J0 = halt) does the class-7 borrow at stage 14->15 and only then reaches J0
  (stage 18, with the borrowed prefix, the new '35 2 5 0^3 9' c=0 mini-start, all parsed into the far).  J0 is read only
  at round ends (never inside a round) in P11.
- The class-7 end depends on more than c mod 14 (std, n1, P=[19]): c = 21 (k=5) borrow + other junk; 35 (k=9) borrow;
  49 (k=13) no borrow, J0 at once; 63 (k=17) borrow (other shape); 77, 91, ... (k = 21, 25, ..) no borrow in std.
  Real post-restart counters are 2U-3 = 35 mod 5040 -> k = 9 mod 1440, so k = 9 is the representative only if the end
  depends on k mod a divisor of 1440 (P11 big run k = 1449 did borrow: consistent).
- With the junk prefix in front (P = [16 junk 18], std), a class-7 end borrows the NEAREST digit (18 -> 15), not d:
  the borrow always takes the digit adjacent to the round.  So the post-borrow restart must leave d-3 as the nearest
  prefix digit (no fresh U digit in front of it) AND give a class-7 counter.  P11's gadget does neither (it lays out
  U-1 in front and 2U+3).

## Base round-end table (endtab.py, n1 with J0 = halt, std, P=[31], far7; endtab_std.txt)
Entry = first K-moment 'P 2^k 5 1^m 0^2 X 1^w' with m < 14; k replaced by k0 + 4j.  Pre-J0 word in loose form.
- r = c mod 14.  No borrow, J0 with d intact: r = 1, 4, 5, 6, 8, 9, 11 (k-independent shapes; r = 8: 'd 2^(k-1) 1 7 6
  0^3 [debris] (B)^3 5 _4 (B)^X 0 _4 1^w', B = '100000', X ~ 2U/3: the accumulator laid out as blocks).
  r = 10: J0 after a long irregular phase (d intact).  r = 0, 3, 13: junk cycle (no J0 in 60 stages).
- BORROW classes (d = 31 -> 28): r = 7 (k = 9, 17), r = 2 (k = 13, 25), r = 12 (k = 17..33).  k-dependent in std,
  probably because std U = 19 < k for k >= 21 (std is faithful only for k < U).
  r = 12 at k = 21 and 33: pre-J0 = '28 0 1^w | U' = EXACTLY the n1 round-end J0 shape ([0 1^w | f]) with the
  borrowed digit as the only prefix.  k = 25: '28 65 0 1^w'; k = 17/29: '28 46/70 41 0 1^w'.
- r = 7 at k = 9: pre-J0 '[d-3] 8 2 5 1^3 0^3 1 4 1^2 0^6 _2 (B)^X1 1 _4 (B)^X2 0 _4 1^w' (big: X1 = 1690, X2 = 1695).
  P11's gadget turns (B)^X1 into 1^(2 X1) (a pure move) and (B)^X2 into '0 (U-1) 2 5 1^(2U+3)' (copy: digit + counter).
- The class-7 borrow takes the NEAREST token: x >= 3 -> x-3 (+ fixed junk); x = 1 (cleared zeros) -> borrow passes and
  hits the next digit but creates new digits; x = 0 or 2 -> no borrow, J0 at once.

## Gadget side (J0 copy loop)
- J0 is read at the LEFT end of the round's debris (where the end-event borrow ran out), not at the tail.
- P11 class 7 (big): pre-J0 '[d-3] 8 2 5 1^3 0^3 1 4 1^2 0^6 _2 (B)^1690 1 _4 (B)^1695 0 _4 1^w | U'; restart
  '[d-3] 8 2 5 1^3 0^3 1^2 5 1 0 2 1^3380 0 (U-1) 2 5 1^(2U+3)': the first block run becomes 2 ones per block (a
  MOVE into cleared zeros), the second becomes digit U-1 + counter 2U+3 (a COPY, ~1.5 + 3 units per block).
- P11 class 8: '(B)^1692' -> digit U + counter 2U-3 (copy); the old prefix d and the 2-run stay untouched to the left.
- Every in-place restart seen leaves an accumulator-derived digit NEAREST the new round: P11 [R] / [.. U-1],
  T12a [3, 2R+4] (c = (4R-19)/3), H13c [.. 2R+3], Q12a [3 1 0 R].  The next borrow then takes that fresh digit.
- benum.py (gadget-only lazy TNF from a saved pre-J0 word, mkstart.py) + bfilter.py (does the next RSIG keep d-3 as the
  nearest digit, with only 1s / only tokens < 3 after it?).
  - st_c7_k9 (class-7 borrow, P11's tape), ns = 1: 2817 nodes, 44 RS leaves, 0 keep d-3 nearest.
- st_c7_k9 ns = 2 (running): bfilter 'strict' hits (P = [2 28], c = 21) are FALSE: bverify with d = 37/43 gives the
  same [2 28] (28 is gadget-made, not d-3).  Always bverify with two other d values.
  (Side fact from that family, 0LK0LC_0RK0RL_0LD0L*: class 7 at k = 5 also borrows.)
- J0 read site (j0at.py, literal): round-1 end: inside the far tail (idx 22 of the 44-bit tail, matches farcount);
  class-12 borrow end: at the RIGHT END OF THE OLD FAR REGION, i.e. LEFT of D(d-3) (pos 180 of 182-bit far7, same for
  d = 31/37): the class-12 end walks left over its own D2 run AND over the borrowed digit (rewriting it as
  '1111 0 11111 0 ...' marks) before reading J0.  Class 7: J0 read right of the (B)-blocks, far right of d-3.
- Class-12 pre-J0 tokens '[d-3] 0 43 1^w' = the n1 halting shape FarE + [0 1^w | f] with D(d-3) in place of FarE's tail.
- Literal J0 tapes (n1, j0at-style):
  - class 12 (k=21 std): right of the J0 site '0011110 (111110)^((d-4)/3) (10)^41 0 1^w': the borrowed digit d-3 is
    UNROLLED into marks (one '111110' per 3 units, d-4 = 27/33/39 for d-3 = 28/34/40) by the left walk that precedes
    J0; it is no longer a D-token.  (Round 1: '0011110 0100100100 1 ...' = far tail rest.)  A class-12 cycle needs
    the gadget to re-roll the marks into a digit token.
  - class 2 (k=13): '[d-3] 24 30 0 7 1 0^4 ..' | J0: accumulator-derived digits 24, 30 between d-3 and the site.
  - class 7 (k=9): '[d-3] 8 2 5 1^3 0^3 1 4 1^2 0^6 _2 (B)^X1 1 _4 (B)^X2 0 _2' | J0: fixed junk + two block runs.
  So in no borrowing class is d-3 adjacent to the J0 site: the gadget must clean fixed junk (class 7), remove two
  accumulator-derived digits (class 2) or re-roll marks (class 12), on top of building the counter WITHOUT a copy digit.
- **st_c12_k21 (class-12 borrow tape), ns = 2 COMPLETE** (all J0, K, L; S = 6 stages): 366,285 nodes: 2989 RS,
  332,371 MAX, 15,525 W, 7769 T.  bfilter (P ends in d-3 = 28 + small tokens): 57 hits, ALL fail bverify (d = 37/43
  give the same 28: gadget constant).  bverify2 (nearest digit x of the first RSIG must move with d): 2804 RS machines,
  70 'MOVES', none keeps d: 56 have x DEcreasing with d and the COUNTER = d-3 (the gadget re-rolls the marks into the
  counter: 0RL1RF_0RK0LJ family P=[x], c = d-3, x = 38-(d-3)/2), the rest change structure between d values.
  => no 12-state (ns = 2) gadget restarts a class-12 borrow tape keeping d as a digit.
- **st_c7_k9 (class-7 borrow tape, P11's), ns = 2 COMPLETE**: J0 -> base states (ns0), J0 = 0LK (S = 14 for K0 =
  0L*..1LL, S = 6 for K0 = 1R*), J0 = 0RK, 1LK, 1RK (S = 6).  bverify2 over all 7048 RS machines (d = 37 vs 43):
  0 'MOVES' (433 read an undefined slot on the other starts).  => no 12-state (ns = 2) gadget keeps the borrowed
  digit nearest after a class-7 borrow; the first RSIG always has a gadget- or accumulator-made nearest digit.
- **st_c2_k13 (class-2 borrow tape), ns = 2 COMPLETE**: 349,197 nodes (3518 RS, 315,891 MAX, 14,554 W, 7959 T);
  bverify2 over 3246 RS machines: 0 'MOVES'.
- Running next: ns = 3 (13 states) J0 = 1RK on the class-7 tape, node cap 300k; big-policy class tables r = 12/2/7;
  mining (mine2 = 1172 multi-restart leaves with a prefix from t12scan/d13/tier1; mine1b = 983 from inplace ienum).
- ns = 3 slice (13 states): J0 = 1RK, class-7 tape, DFS capped at 300,189 nodes (covers K0 = 0LA..0LK, i.e. about
  1/4 of K0 values; 6751 RS, 256,637 MAX, 24,113 W, 6726 T); bverify2 over 6483 RS machines: 0 'MOVES'.
- Big-policy class-12 table (endtab_big12.txt, U = 2539, P = [31]): matches std for k <= 45 and extends to real k:
  k = 9 mod 12 (21, 33, 45, 1449): CLEAN borrow, pre-J0 '28 0 1^w | U';  k = 5 mod 12 (17, 29, 41, 1445): '28 (2k+12)
  (2U+3) 0 1^w';  k = 1 mod 12 (13, 37, 1453): junk cycle (25: '28 65 0').  So a class-12 counter whose k-subclass is
  9 mod 12 gives the clean borrow at true sizes.

## !!! CORRECTION: the class-7 borrow is a small-k artefact (big policy, true k)
- endtab big, class 7 (entry c = 49, m = 7 phase, k = 13 + 4j, U = 2539): k = 17 borrow; k = 25, 33 J0 at once (no
  borrow, d intact); k = 41, 49, 57, 65, ... and k = 1449 (the real P11 round-2 value, c = 2R-3 = 35 mod 5040 ->
  k = 9 mod 1440): n1's growing-far JUNK CYCLE, no borrow.  Same for d = 31, 1399, 1501, 3001 (so not 'k < d').
  Std agrees (k = 29, 37, 41 junk).  The class-7 borrow happens only for k in {9, 17}.
- The inplace note 'P11 round 2 borrows, big 2539 -> 2536' came from a TRIMMED big run (realbig/ctrim keeps c mod 42,
  so k = 9).  At true size P11's round 2 most likely ends in the junk cycle (bigrun.py untrimmed run queued).
- Class 2 at true k (1445, 1449, 1453): borrow 31 -> 28 but then '28 (2k-2) (U-ish) 2^37 5 ...' and no J0 within 60
  stages (junk).  Class 12 at k = 9 mod 12 (1449 checked): clean borrow, J0 at the old far, d-3 unrolled into marks.
  => at true sizes the ONLY borrowing end that reaches J0 is class 12 with k = 9 mod 12.
- Depth-independence: class 7 at k = 1449 (big, d = 31) is the junk cycle for z = 38, 39, 40, 41, 50, 1037 (crafted
  start depths; end depths ~20k).  An untrimmed P11 big run (bigrun.py) was stopped at stage ~150: the stage cost
  grows with the depth list (quadratic total, ~40 h estimated); RSIG at stage 7 'P=[2539] c=5075' reproduced.
- Mining done: mine1 (1562 machines) + mine2 (1172): 0 machines with 2 consecutive borrows of an accumulator-sized
  digit; the 89 single events are the P11 family (std, small k) and small-c cyclers.
- class-12 tape, ns = 3, J0 = 1RK, capped 250,113 nodes (K0 = 0LA..0LK): 1865 RS, bverify2 1762 machines: 46 MOVES,
  all with x DEcreasing in d (counter = d-3 re-roll family) or irregular; none keeps d.
- class-12 tape, ns = 3, J0 = 0LK, capped 250,161 nodes (K0 = 0LA..0LC.. partial): 3263 RS, bverify2 3219 machines:
  14 MOVES, 12 decreasing in d, 2 irregular (prefix structure changes between d values); none keeps d.
- All queued work finished 2026-10-11; queue.sh stopped (queue.stop).

## farcount handoff: class-12 looper L12f = ..._0LJ0LI_1LK0LC_0LL0RA_1LL0LI (2026-10-11)
- Real round structure (std): RSIG st 112 P=[2^2 0^2 25 2 0 7] c=26; big (crafted from the std st-112 far):
  P=[2^2 0^2 (2U-13) 2 0 7] c = 3386 = (4U+82)/3 (class 12, accumulator-sized), z 111 -> 10273.
- The 'refill' is a FULL REBUILD, not +3: rtab with the last digit X = 7, 13, 22, 31 (std) and X = 7, 31 plus
  the 25 replaced by 2539 (big) always restarts with the SAME prefix '2^2 0^2 (2U-13) 2 0 7'.  The far region grows
  by 2(X-7) bits (2539 case +4980): the whole old prefix, including the borrowed X-3 and the old U-digit, is pushed
  into the far debris and never read again.  X = 4, 6, 8, 10: junk (no restart).
- So the 7 is a gadget constant: 'refill less than it borrows' does not exist as a knob, and the decrement cannot be
  carried to the accumulator-sized digit (2U-13), because that digit is rebuilt fresh from the new U every round and
  the old one is dumped.  L12f is a clean in-place class-12 accumulator reloader (a Q12a / L12-type looper).
- Priority bug: ilib.py's SetPriorityClass call passes the 64-bit pseudo-handle without argtypes, so it silently
  fails (python stays Normal; only igstage children were Idle via creationflags).  Fixed here: idle.py (proper
  HANDLE argtypes), imported by every borrow/ script (verified Idle with Get-Process).  Other dirs' ilib copies
  (inplace, t12scan, farcount, ...) have the same bug.
