# Route 3 (tier1): residue route on L12-type restarters. REPORT (Opus investigator, 2026-10-09)

## Verdict
- **12-13 states: OPEN, leaning negative.** About 372k scan leaves gave no 12- or 13-state machine that halts after a
  full restarted round. Coverage is partial (see "Scans").
- **14 states: one Tier-1 SCREENING candidate, H14.** In the b0 = 6 follower world it halts after 2 full
  f_(omega+1) rounds. Round 2 is reloaded from the accumulator (counter 4R+4). This is screening evidence only. The
  final halt is a Collatz-type gamble on the real depth: every large-depth case tested halts (see "H14 robustness").
- **The n1-notes route as stated (R2 = 5 or 12 mod 21) is closed.** R2 cannot be steered. Only the counter offset
  delta can, and delta acts through the left-over digit prefix or stray bits that the eater leaves behind.
- **Correction to the n1 notes.** Std-policy eater tests are faithful only for small k (k up to about 45 with
  R-rep 19). Two false Tier-1 positives came from this (T13 and a 14-state m66 clone). L12 survives the check: with
  the big policy it restarts cleanly at k = 17, 49, 77, 137.

## Residue rule (task 1)
1. Every huge accumulator produced by n1's champion jump is r = 19 mod 2520.
   - rescheck.py: 60 of 60 jump outputs, residue known modulo a multiple of 2520.
   - All 606 J lines in the n1 logs show r = 19 or 2539.
   - This is a tower-residue fixed point of the base machine, independent of the eater.
2. A round restart has counter **c2 = 4R + 3 + delta**.
   - R is the accumulator at the left event, which is the output of the last jump, so R = 19 mod 2520 always.
   - delta is a small constant fixed by what the eater leaves at the left end when the far region is gone. That can
     be a digit prefix P (prefix_table.py) or stray far-left bits (remnant.py).
   - Hence c2 = 79 + delta (mod 10080). Checked R-sized with the big policy: c = 10159 + delta.
3. The achievable delta values:

   | source | cases | delta values found |
   |---|---|---|
   | digit prefixes of up to 3 digits | 819 | {0, 1, 2, 3, 5, 7, 8, 16} |
   | stray bit patterns (up to 6 bits, gaps 1-6) left of '7 1^N' | 378 | 0-7, 16; 189 cases re-enter J0 |

   - delta depends on the digits mod 3. Gap dependence is mod 4.
   - A single stray '1' at gap 2 gives delta 2.
   - delta = 14 or 28 mod 42 was never seen. That is the class-9 "k2 != k1 mod 3" route from the n1 notes.
4. The round end depends on c2 mod 14 (base_table.py, c = 3..180):

   | c2 mod 14 | round end |
   |---|---|
   | 9 | standard J0, k = 4(c-9)/14 - 3 |
   | 5, 8, 11 | J0 on a different tail |
   | 1, 4, 6 | J0 with no far region |
   | 10 | J0 with an irregular k |
   | 2, 7 | small self-restart |
   | 12 | self-restart with 79 (round 1 again) |
   | 0, 3, 13 | junk |

   So any delta in {1, 2, 6, 9, 10, 11, 13, 14, 16, 28, ...} presents a round-2 J0 tape different from round 1's, and
   a spare slot can halt there. L12 leaves '26 33' then '7', so its delta = 0 (c2 = 79 = 37 mod 42, k2 = 17 = k1),
   which is why its rounds are identical. The 11-state sibling's delta = 12 (c2 = 91) is a k = 17 accident.
5. k-faithfulness:
   - The real k1 = 17 mod 8640 is huge but far smaller than R. The std world has R-rep 19, so eater tests are only
     faithful for small k.
   - Screens must check several k values: k = 29, 41 in std, or k = 77, 137 with the big policy.

## Scans (task 2)
t1enum.py does a lazy TNF enumeration. The start is far_17 + [0 1^41|1|19]. A restart is detected by its counter and
delta, then checked at k = 29 and 41 (branching on any undefined slots read there). Rounds 2-4 are followed with
further branching. HALT2 means a halt after a full restarted round.

| run | space | leaves | k-robust restarts | HALT2 |
|---|---|---|---|---|
| e2_a | ns=2, J0 = 0LK, K0 up to 0RH (about 40%) | 89,886 | 18 (L12 family, delta 0) | 0 |
| e2_b | ns=2, J0 = 1LK (partial) | 41,789 | 12 (delta 0) | 0 |
| hm (L12 + half-state M) | 20 runs | 1,060 | 18 (delta 0) | 0 |
| b3 B1 | ns=3, J0=0LK, K0=0LC, K1=1LL, complete | 74,933 | 303 delta 0, **6 delta 1** | 0 |
| b3 B2 | L12's L fixed | 49 | 1 | 0 |
| d1c | delta-1 core fixed, K/L free; J0 free | 18,825 + 18,981 + 365 | delta 1 x 19 | 0 |
| d1c2 | delta-1 core, M1=1RM, M0 free (stopped, partial; M1-free subtree not run) | 125,292 | delta 1 x 3, rest delta 0 | 0 |

KFAIL (k=17-only) families include delta 9 (c=88), delta 12 (c=91), delta 18 (97), delta 34 (113) and delta 38 (117).
The other session's genum5 runs (g5s3_0LA at 80k leaves, g5s3_0LC at 42k leaves, g5_0LK, g5_1LK; all stopped)
have 0 halts at stage 40 or later. Their delta = 1 restarters (m66 chains) are k = 17 accidents.

## Candidates
- **D1** (13 states, non-halting) is the first k-robust delta-steering eater:
  `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK1LM_1RJ1RM`
  - It is L12 with L1 = 1LM and a new M = 1RJ1RM. M runs right over 1s and plants a 1 at the first 0.
  - For k = 2 mod 3 it restarts with c2 = 4R+4 (delta 1). Checked in std at k = 17, 29, 41 and with the big policy at
    k = 17, 77, 137 (c = 10160).
  - It reads all 7 new slots in round 1, so it has no free slot for a 13-state halt.
  - Six variants: L0 in {0LK, 1LB, 1LH}, L1 in {1LM, 1RM}, and K0 = 1RI also works.
- **H14** (14 states, Tier-1 screening candidate):
  `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LN1LL_0LK1LM_1RJ1RM_1RD---`
  - It is D1 with K0 sending to N, a copy of C whose 1-slot is the halt.
  - Real start b0 = 6: round 1 runs stages 0-36, then the eater, then a clean restart at stage 50 with c2 = 80.
  - Round 2 is full and clean (stages 50-86), followed by a messy post-round phase and HALT N1 at stage 141
    (H14_b6_std.log).
  - Robustness:
    - The eater does not halt in round 1 for k = 77 or 137 (big policy).
    - The round-2-end halt holds for crafted round-2 starts with c in {80, 122, 164, 248} and depth z in
      {415, 575, 1255, 2935} (val2.py).
    - A big-policy check of the round-2 end is infeasible (a literal stage needs more than 2e9 steps).
    - A b0 = 846 replay (same real class mod 840) is INCONCLUSIVE, not a counterexample (H14_b846_std.log, then
      H14_b846_resume.log). Round 1 ran cleanly for about 4360 stages. At its end k1 = 2897, which is far above
      R-rep 19, so the std eater test is unfaithful there. The eater left '2^2885 1 5 35' and the next literal stage
      timed out at 4e8 steps. A faithful test needs R-rep much larger than k: the big policy with bigk of about 3.
  - Main caveat: the halt comes after a messy phase whose literal path uses depth-derived digits. The std world has
    depth > R-rep, while in the real run depth is much smaller than the current accumulator.
  - Grade: 2 full rounds, the second reloaded from the accumulator. sigma ~ f_(omega+1)(f_(omega+1)(~2^^363)) is
    Tier 1, but at 14 states. That would still beat the f_(omega+1) BB(14) champion if verified.

## H14 robustness (lead's four questions, added ~20:00)
1. **Why round 2 ends differently from round 1.**
   - Round 1 ends in counter class 9 (c1 = 79 mod 10080). That is the standard J0 entry: the D2 run plus the 44-bit
     tail.
   - The eater's delta = 1 puts round 2 in class 10 (c2 = 4R+4 = 80 mod 10080). Its J0 entry has a different,
     irregular tail.
   - After that entry the eater starts a CHAIN of short mini-rounds. Each turns the current depth z into the next
     counter z' ~ (3z - r)/5, with r set by z mod 5 (std: 1036 -> 620 -> 372 -> 222 -> 132 -> 78), and leaves a prefix
     behind.
   - When z is small the chain collapses. It either ends at a J0 entry with '1 0' left of the J0 cell, where
     K0 = 0LN sends N onto a 1 (HALT), or it falls into an n1-type junk cycle that never halts.
2. **Why N1 is never read in round 1, for the real k1.**
   - ntrace.py, round-1 eater at k = 29: N is entered only 3 times. Twice it is inside the fixed 44-bit tail; once it
     is at the blank left end. It always reads 0.
   - K0 never runs inside the D2 run, so these reads do not depend on k.
   - Measured, k = 2 mod 3: restart with delta 1 and no halt for k = 14..44 (std) and for k = 17, 77, 137, 257, 521,
     1001 (big policy). k = 5 and 8 halt, a small-k boundary effect.
3. **Score.**
   - Round 1 is n1's run up to n1's halting J0 read, so the accumulator R at least matches n1's output,
     about f_(omega+1)(2^^363).
   - Round 2 has counter 4R+4 and gives about f_(omega+1)(R).
   - So sigma(H14) >~ f_(omega+1)(f_(omega+1)(~2^^363)), if it halts. This is a lower-bound shape, not computed.
4. **Residue argument.** NOT POSSIBLE for the halt itself: the bottom of the (3z-r)/5 chain depends on all digits of
   the real depth, not on a residue. The halt is a Collatz-type gamble. Empirical odds:

   | policy | swept | result |
   |---|---|---|
   | std | every class-10 counter c = 80..360 (z = 415) | 21/21 halt |
   | std | z = 400..427, 1000..1199, 2523/2550/5043/5070/7590 (c = 80) | 233/233 halt |
   | std | small z = 3..35 | 16/18 halt; z = 3 and 30 go to junk |
   | big (R-rep 2539 > z, the realistic order) | (c, z) = (80, 415), (80, 100), (94, 415) | halt |
   | big | (164, 415) | no halt within 400 stages: a slow countdown, outcome unknown |
   | REALISTIC ORDER (accumulator tokens >> depth) | realistic.sh: the real stage-84 state with R = 19+2520j, bigk = j, j = 1, 2, 4 | 3/3 halt, same terminal collapse |

   The real run has depth << accumulator. Neither follower policy reproduces that, because every accumulator shares one
   representative. realistic.sh crafts that order directly and all three cases halt. The (164, 415) big case has the
   wrong order (depth 78k > 2R).

   Verdict: a strong screening candidate (every large-depth std case halts), but not certain. A proof would have to
   show that every large chain bottoms out into the halting branch.

## Depth class (lead's caveat)
- The real round-1-end depth is n = 35 mod 42 (std 329), but every t1enum scan used n = 41.
- All 9 delta-1 restarters, including H14's round-1 eater, re-tested at n = 329, 371 and 2849 with k = 17 and 29
  (std): 54/54 restart with c = 80 (depthcheck.txt).
- The earlier n = 41 negatives could still miss a depth-sensitive halter.
- k0sweep.sh now runs at n = 329.

## 13-state follow-up (k0sweep.sh, t1enum ns=3, J0 = 0LK, one K0 seed at a time; .done markers)
- The seed order puts 1RI first; 0LA and 0LC are skipped, since they are the g5s3 trees and b3.
- K0 = 1RI at n = 41: 170k leaves before it was stopped for the depth fix (437 delta-0 loops, 17 delta-1, a few prefix
  restarts). At n = 329: 152,752 leaves, 0 HALT2, then PAUSED at the lead's request (no seed finished). It found new delta-1 families, k-robust at k = 29 and 41,
  for example K = 1RI0LL with L = 0LM0LC and M = 1LL0LJ. Every one uses all 7 new slots (droptest), so none is a
  13-state halter. 0 HALT2.

## Tools (tier1/)
- Library: t1lib.py.
- Residue and class tables: base_table.py, prefix_table.py, ptest.py, remnant.py, j0view.py, rescheck.py.
- Scanning: t1enum.py (with kcheck and maxdef), hm.sh, b3.sh, d1core.sh, d1core2.sh.
- Robustness checks: kscan.py (POL=big env), kcheck.py, droptest.py, clone13.py, classrun.py, val2.py, resume.py.

## Recommended next steps
1. H14 hinges on the post-round chain.
   - Model the mini-round map exactly, i.e. z -> z' and the terminal behaviour by z, using literal and event runs.
   - Then decide whether every large start reaches the halting collapse. If junk is possible, the halt is an
     unprovable gamble.
   - realistic.sh is the template for testing in the realistic order.
2. The 13-state seed sweep (k0sweep.sh) is paused; no seed finished, so a resume restarts K0 = 1RI. Every delta-1 eater
   found so far uses all 7 new slots.
   - Most promising: route 2's lever. A (10)^j block right of the head at the no-far restart shifts the counter by 2j.
   - So a 3-state eater that plants a right-side block with one slot to spare would also give a class-10 or class-9
     (j = 7) round 2.
3. Keep every eater screen k-robust: k = 29 and 41 in std, k = 77 and 137 with the big policy.
