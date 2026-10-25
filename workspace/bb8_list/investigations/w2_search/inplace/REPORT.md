# In-place reload route on n1: REPORT (inv-w2-inplace, Opus, 2026-10-09/10)

## Result in short
**Two Tier-1 candidates (follower screening only, no proof).**
- Both halt after a full second round whose counter is reloaded from the accumulator.
- The reload is in place: nothing left of the far region is ever changed.

The two machines:
- **T12a (12 states, one spare slot K1)**
  `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---`
  - Gadget: J0 = 1RK, K = 0RL---, L = 0RF---.
  - It halts on L1. K1 is never read.
- **H13c (13 states)**
  `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1LK0LL_0LM0LA_0LJ---`
  - M is a clone of I with M1 = halt.
  - So the machine halts exactly when L reads 0 and I then reads 1.
  - Its base is the in-place restarter F12 = ..._1RK0LC_1LK0LL_0LI0LA.

Mechanism (the same for both):
1. At n1's round-1 end (J0 at the far tail) the gadget restarts in place. The new round start is
   'P 2 5 1^c2 0^3 9 1^z'.
2. The round-2 counter c2 is accumulator-sized:
   - T12a: c2 = (4R-19)/3, class 5 mod 14.
   - H13c: c2 = (4R-10)/3, class 8 mod 14.
   - Every jump output R is 19 mod 2520, so the class is fixed.
3. Round 2 runs fully.
4. It then ends in a "J0 on another tail" class (tier1's table) instead of n1's class 9.
5. There the gadget reads something different from what it read at the round-1 end, and it hits the undefined slot.

Size: round 1 is n1's round, about f_(omega+1)(0.86 B). Round 2 has a counter of about 4R/3, with R that huge.
So sigma is about f_(omega+1)(f_(omega+1)(~B)). That is Tier 1 (f_(omega+1)^2), far beyond n1. The exact score
was not computed.

**Tier 2: not found.** Structural negative below: an in-place restarter never reads the far left, so it never sees a
parked d.

## Evidence
The follower is ilib.py: igstage literal stages plus follow2 jumps, under the std and big policies.

| test | T12a | H13c |
|---|---|---|
| far_k + [0 1^n\|1\|19], std, k = 17/29/41, n = 329/371/2849 (also 41) | restart at stage 14, c2 = 19; HALT L1 at stage 26 | restart at stage 4, c2 = 22; HALT M1 at stage 16 (also n = 35/77/413) |
| real start b0 = 6, std | n1's J0 at stage 37; restart at 51 (c2 = 19); HALT L1 at stage 63 | restart at 41 (c2 = 22); HALT M1 at stage 53 |
| big, constructed n = 329, restart counter trimmed to its class mod 42 | k = 17, 77, 137: restart c2 = 3379 (z = 3714); HALT L1 at stage 26 | k = 17, 77, 137: restart c2 = 3382; HALT M1 at stage 16 |
| real start, big (realbig.py: round 1 untrimmed, restart counter trimmed to its class) | restart at 51, c2 = 3379 (z = 40674); HALT L1 at stage 63 (the round-2-end stage needs about 1e11 steps; run with max 5e11, t12a_realbig2.log) | restart at 41, c2 = 3382 (z = 37298); HALT M1 at stage 53 |
| restart counter vs R (big, bigk = 1, 2, 3: R = 2539, 5059, 7579) | c2 = 3379, 6739, 10099 = (4R-19)/3 exactly | c2 = 3382, 6742, 10102 = (4R-10)/3 exactly |
| round-2 counter sweep c2 + 42j (rscan from the restart word, prefix kept), std | j = 0..6 and 7, 9: HALT L1 at the round end (stage 12 + ~18j) | j = 0..9: HALT M1 at the round end; big j = 0, 2: HALT; j = 4: T |
| leftmost changed cell, relative to the far region's left end | 33 or more | 28 |
| markers 1, 11, 101, 1101, 10101, 111 at gaps 1-4 left of the far region | not run | outcome unchanged, marker untouched |

**Evidence label.** Every row above except the size-order test is follower-with-fixed-U: all accumulators share one
representative (19 or 2539 + 2520 (bigk - 1)). That puts depth > accumulator at the round-2 end, while in the real
run the accumulator is far larger than the depth.

**How each machine halts (asked by the lead after H14's fixed-U artefact).** Neither halt goes through mini-rounds
or a z -> z' chain. No round-start signature appears between counter exhaustion and the halt.
- H13c halts DIRECTLY at counter exhaustion.
  - Round 2's counter is empty at stage 13.
  - Stages 14-15 are the end event ('... 0^3 1 40 0 43' -> '7 1^z').
  - The next stage reads J0 -> K -> L0 -> M1 = HALT.
- T12a halts after ONE absorption pass, three stages after exhaustion.
  - Stage 22: the counter is at 1^3 and runs out.
  - Stage 23: the depth list is expanded into an 'X (2 0 3)^m' block.
  - Stage 24: '... 10 1^2'.
  - Stage 25: '7 1^2'. The depth list now sits in the far region.
  - Stage 26: J0 -> K0 -> L reads 1 = HALT.

**Size-order test (order.py).** Big policy, with the jump stand-in raised to U = 19 + 2520*20 = 50419 from the last
period of round 2 on. The accumulator entering the round-2 end is then ~100840, far above the depth 7113 / 10489.
- H13c: same path, HALT M1 at stage 16.
- T12a: same path, X = 100833, HALT L1 at stage 26 (t12a_order22.log).

So both halts survive the realistic order k1 << depth << accumulator. This is still follower screening; exact tower
residues are inv-t12a-verify's job.

Caveats on the evidence:
- Trimmed counters keep the class mod 42. The round-end type depends on c mod 14, and on k mod 3 through c mod 42.
- Untrimmed big rounds are too long for the follower.
- There is no literal replay of a full-size round 2.
- Not checked: whether the R used by the restart is the final round-1 accumulator or a later jump output. Both are
  huge and 19 mod 2520.
- T12a's round-2 end first eats the depth list into the far region (stages 23-25), then reads L1. That stage costs
  about R x depth steps under big.
- The 13 HALT-after-restart leaves of the 1RK tree are T12a and its siblings:
  - ..._0RL1LD_0RK---, ..._0RL---_1RA---, ..._0RL0LA_1RK--- and others give the same result (std).
  - ..._0RL0RC_1RK--- is the exception: it halts with no restart at n = 329.

## Task 1: M13a
Machine: M13a = ..._0LK0LC_0LC0LL_0LA1RM_0RM0LE. Start: far_17 + [0 1^41|1|19].
- **Round-2 restart (stage 20): not in place.**
  - It writes 230 cells (std) / 20394 cells (big, about 3 x depth) left of the far region's left end.
  - Its counter 2*depth - 52 IS accumulator-sized, because the depth before it is R-sized (big 6817).
- **Round-3 restart (at the round-2 end): in place.**
  - It reaches at most 1 cell left of round 2's start.
  - Its counter comes from round 2's own D2 run: c3 = 21 + 4(c2-100)/14, about 2 c2 / 7. So it is not
    accumulator-sized.
  - rscan, c2 = 100..156 in class 2 mod 14: P = [54,18] [62,14] [70,10] [78,6] [86,2], c3 = 21..37.
  - c2 = 170 gives junk. Under big, the round-2 end is JF.
- **Round 3 is not a real round.** With c3 = 33 (class 5) it degenerates after 2 periods into n1's growing-far junk
  cycle (8 stages per cycle, far +202 bits per cycle).

## Task 2: in-place screen
### Enumeration (ienum.py)
How it works:
- Lazy TNF enumeration over J0 plus NS new states.
- Each node is followed with the follower from far_17 + [0 1^41|1|19].
- LEFT pruning: a stage that changes a cell left of abs -8, or visits left of abs -12, ends the branch.
- It records every round-start signature (RSIG) and keeps following through round 2.

Trees:

| tree | size | leaves |
|---|---|---|
| J0=1RK, ns=1 | 309 leaves, complete | 3 in-place leaves with repeated restarts, among them P11 |
| J0=1RK, ns=2 (DFS stopped inside K0 = 1LL..; K0 = 1R* not reached) | 37,070 leaves | 2957 LEFT, 27795 NORS, 2797 NOEND, 484 RS4, 774 HALT before any restart, **13 HALT after a restart (the T12a family)** |
| J0=0RK, ns=2 (stopped at K0 = 0RL0RK_1LJ1RK) | 22,881 leaves | 2535 LEFT, 197 RS4, 0 HALT after a restart |

The start depth n = 41 is the wrong class (see the caveats). Every hit was re-tested at n = 329/371/2849.

### In-place, accumulator-sized restarters
In all of these the head never goes left of the far region's left end.
- **P11 = ..._0LJ0LI_1RK0LC_1RC--- (11 states, K1 spare)**
  - Restart counter 2R-3 (std 35, big 5075). The old accumulator stays as a prefix digit.
  - Round 2 is class 7. It ends by the base borrowing that prefix digit (19 -> 16; big 2539 -> 2536).
  - A copy loop then restarts round 3 with counter 2R+3 (big 5081).
  - Round 3 is class 13 and ends in n1's junk cycle.
  - Robust for k = 17..137 and for n = 41 and 329.
- **Q12a = ..._1RK0LC_0RL0LB_1LE1LJ (12 states, all slots used)**
  - Class-9 counter 2R-1 (37 / 5077), restarted every round with the same prefix '3 1 0 R'.
  - The far region gains one deposit per round. It never halts.
- **F12 = ..._1RK0LC_1LK0LL_0LI0LA**: the base of H13c.
- **..._0RK0LC_0LL1RC_0LK0LC** (c = 23 / 3383, class 9): k-fragile at n = 329.

### Hook scan
kgc.py / kscan.py / kscan2.py compare the k-grams of consecutive slot reads in the round-2-end window against all
earlier stages, including the whole real-start round 1.
- P11 and Q12a: 0 special-only grams (k up to 4 and 5). Their round ends are locally identical to earlier stages.
- kscan2 at n = 329, over 83 restarters with real rounds: 59 ran and 25 had special-only grams.
- robust.py kept 8 of these: those whose RSIG c sequences agree for (k,n) = (17,329), (17,371), (17,2849), (29,329)
  and (41,371).

Their hooks were then tested with hooktest.py:
- H13c passes.
- G12a = ..._1RK0LC_1LK1LL_1RI1LG: its hooks fire inside the restart-1 stage. This is an artefact of the scan window.
- ..._0RK0LC_0LK0LL_1LL1LF with hooks K1,L1 and L1,F1: halts in std, but under big it restarts again instead of
  halting. Under big its prefix is R-sized (P3393), so the std result is an artefact.
- H13a = ..._0LL0RC_0LK0LM_0LL--- and H13b = ..._0LL1LG_1LM0LL_1RK---: depth-fragile.
  - H13b halts after an R-sized round at n = 329 and from the real start in std.
  - But at n = 77..497 and at n = 2849 it halts with no restart.

## D1 (forwarded lead; measured only, its subtrees not enumerated)
D1 = ..._0LK0LC_0LC1LL_0LK1LM_1RJ1RM. Start: far_k + [0 1^n|1|19].
- **First restart (stage 13) is NOT in place.**
  - Counter 4R+4 (std 80, big 10160 at k = 17 and 29).
  - The far region is erased (far = 0 bits).
  - It writes 184 cells (std) / 20344 cells (big, about 8R) left of the far region's left end: a leftward unpack
    like n1's H.
- **After that nothing is written further left.** In std, n = 41, the leftmost changed cell stays at -184 through
  stage 160.
  - The post-round-2 phase is in place relative to the new left end.
  - Its prefix '0 1 2 0 3 1^2 2 0^2 2 0^2 1 2 35 61 0 14 18 0 39' survives: an RSIG at stage 120 with c = 24, z = 57.
- **Same phenomenon as M13a's '78 6' and the round-3 restart.** The counters come from structure the round built (the
  depth list for D1, the D2 run for M13a), not from the accumulator, and they shrink geometrically.
  - D1 / H14: z' ~ (3z - r)/5 (tier1 notes).
  - M13a: c3 ~ 2 c2 / 7.
- **Can D1's short rounds be made full-size?** Not by the same mechanism.
  - A full-size round needs the counter to be read off the accumulator. These in-place restarts only re-split the
    depth list or the D2 run.
  - The accumulator-sized in-place reloads found here (T12a, H13c, P11, Q12a, F12) all come from J0 = 1RK gadgets
    that act at the round-end tail. They do not come from depth eaters.

## Task 3: markers and the outer counter d (negative)
- **Markers.** Shapes 1, 11, 101, 1101, 10101 and 111 at gaps 1-4 left of the far region.
  - The outcome is unchanged for H13c, P11 and Q12a (3 restarts).
  - Nothing left of far + 18 is ever changed, so the markers survive.
- **Why a parked d is useless (structural).**
  - An in-place restarter (minlo = 0) never reads the far left.
  - At every round end the J0 event sits at that round's own tail.
  - Between that tail and anything older lie the round's own D2 run (R-sized) and every older round's deposit, which
    contains '00'.
  - So reaching a parked d needs a walker across R-sized junk, a decision state and a return path.
  - That is at least 3 states on top of the 1-2 restart states, so 14 or more states in total.
- **The only automatic d** is a prefix digit that the base borrows (in P11, the digit R is decremented by 3 at a
  class-7 round end).
  - This would give f_(omega+2) if every reload landed in the borrowing class again.
  - In P11 the reload after the borrow is class 13, which is junk.
  - No machine in the trees repeats the borrow class.
  - The class-7 and class-12 loopers that repeat with a constant depth z are cyclers, not rounds.

## Screening caveats (new)
- **Depth class.**
  - The real round-1 end depth is 35 mod 42: the std real start gives 329, and the big real start (trimmed) gives
    37289.
  - genum5 ns=3 and ienum used n = 41, which is the wrong class.
  - Gadgets that eat the depth list are fragile: their mini-rounds shrink n to about 0.58 n, so the residue
    information is lost.
  - Re-test every hit at n in {329, 371, 2849}, at the tier1 k values, and from the real start.
- **Big real-start runs.**
  - Do not trim round 1's counter: 79 is a start value.
  - A small ctrim turns 79 into 37 and k1 into 5.
  - realbig.py trims only R-sized counters (> 1000).
- **Python limits.**
  - Big runs need threading.stack_size(250 MB) and setrecursionlimit(300000).
  - Otherwise follow2 fails with JF "maximum recursion depth". This is the old "JF at stage 29".

## Tools (this dir)
Stage runner:
- igstage.cpp/.exe: gstage plus the leftmost visited and changed cells, and a left-limit stop.
  Build: g++ from C:/msys64/ucrt64/bin with -static, and that directory on PATH.
- ilib.py: the follower with absolute left tracking, rsig, ctrim and real_start.

Validation:
- ival.py: runs over k, n and policy.
- rscan.py: the next RSIG from a constructed round start.
- hooktest.py: builds a clone-chain hook machine and tests it under std, big and the real start.
- realbig.py: the real start under the big policy, trimming only R-sized counters.
- t1val.py: the Tier-1 validation battery.
- robust.py: (k,n) robustness of RSIG sequences.
- marker.py: survival of a marker placed left of the far region.
- longrun.py: long follow-ups.

Search:
- ienum.py: the in-place lazy enumeration.
- post.py: the big-policy post-filter.
- kgc.py / kscan.py / kscan2.py: k-gram hook scans.
- kgram.exe: copied from g6.

Inspection:
- j0win.py: literal tape windows at J0 and gadget reads.
- umask.py: slot masks per stage.
- dumpst.py: the stage word.

Logs: ie2_1RK.tsv, ie2_0RK.tsv, kscan_n41.tsv, kscan2_out.tsv, robust_*.tsv, hooks2.log, h13c_*.log, t12a_*.log,
m13a_std.log. NOTES.md holds the running notes.

## Recommended next step
1. Independently verify T12a first, then H13c. Start with the cheap checks:
   - run the follower with bigk = 2 and 3 (R = 5059, 7579) to fit the affine forms of c2 and of the round-2-end
     configuration;
   - replay the round-2 end literally with an untrimmed but moderate c2;
   - get the halting tape.
2. Then write mexp/evs-style event specs toward a Coq proof:
   - Round 1 reuses n1's chain (BB10_n1.v).
   - New events: the in-place restart, and the class-5 (T12a) or class-8 (H13c) round end that reads the halt slot.
3. T12a has a spare slot K1, so a 12-state machine might go further. Enumerate K1 together with the halting slot L1
   (2 slots), looking for a third round or a cycle of classes.
4. Tier 2 on n1 still needs a borrow-class cycle, with a prefix digit as d. The only lead is to enumerate restarts
   whose reload after a borrow is class 7 again. None was found here.

## Exact coverage (so inv-w2-d13 and others can skip it)
- **ienum trees** (start far_17 + [0 1^41|1|19], left-limit pruning; leaf rows in ie2_1RK.tsv, ie2_0RK.tsv,
  t_1RK_ns1.tsv):
  - J0=1RK ns=1: complete.
  - J0=1RK ns=2: DFS order K0 = 0L*, 0R*, 1LA..1LL done. The last leaf is K0=1LL (1LL1RK_1RD0LK). K0 = 1R* is not
    covered.
  - J0=0RK ns=2: K0 = 0LA..0RK done; 0RL partly done (last leaf 0RL0RK_1LJ1RK). The rest is not covered.
  - J0=0LK and J0=1LK: not run here (they belong to tier1 / d13).
- **kscan2**: the 83 restarters listed in kscan_in.txt, scanned at n = 329.
- **D1**: measured only.

## Erratum (2026-10-11, from w2_search/borrow/REPORT.md)
The P11 entry above ("round 2 ends by the base borrowing that prefix digit (19 -> 16; big 2539 -> 2536)", and "the only
automatic d") is a COUNTER-TRIM ARTEFACT. The big run trimmed the round-2 counter to its class mod 42, which forces
k = 9. n1's class-7 round end borrows only at k in {9, 17}. P11's real k = 9 mod 1440 (e.g. 1449) gives n1's
growing-far junk cycle with d untouched (crafted round ends, std and big). Never trim a counter when testing round ENDS.
