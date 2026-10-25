# tier1 (route 3): residue route on L12-type clean-round restarters (Opus investigator, 2026-10-09)

## Tools (this dir; n1/ tools imported read-only via t1lib.py)
- t1lib.py: imports n1/fstep.stage, sim.far_of/word_of; rsig() round-start signature 'P 2 5 1^c 0^3 9 1^z'; run().
- base_table.py C0 C1 [z]: n1 itself (J0 undefined) from a round start [2 5 1^c 0^3 3 1^z|1|19]: where does the round end
  (J0 read, far form, k) per counter c.  Output base_table_z32.txt (c = 3..180).
- prefix_table.py L D [N]: n1 from a no-far list [P 1^N|1|19] (P = digit prefix left by an eater): restart counter c,
  delta = c - 79.  Output prefix_table.tsv (all P with <= 3 digits 0..8).
- ptest.py POLICY N 'P'..: same for chosen prefixes, std or big policy (checks c = 4R+3+delta is R-sized).
- j0view.py MACHINE c: literal tape around the head at the J0 read that ends a round with counter c.
- rescheck.py: residues of every huge jump output (all 19 mod 2520, full modulus knowledge).
- t1enum.py: residue-targeted lazy TNF enumeration (J0 + new states), restart detection with c2/delta/class,
  follows every restart into round 2, 3 (HALT2+ = Tier-1 candidate).

## Task 1: residue map (established)
1. Every huge accumulator output of n1's champion jump is 19 mod 2520 (rescheck.py: 60/60 jump outputs, residues known
   mod a multiple of 2520; 606 J lines in n1 logs: r = 19 or 2539 only).  A tower-residue fixed point of the base.
2. A restart's counter is c2 = 4R + 3 + delta(P), R = accumulator at the left event = output of the last jump, so
   R = 19 mod 2520 always; delta(P) is a small constant fixed by the digit prefix P the eater leaves in the list at the
   first no-far K-moment.  Checked R-sized: big policy (R = 2539) gives c = 10159 + delta for P = 7, '0 2', '0 1 2',
   '2 0 2', '5 0 2', '3 1 2' (delta 0,1,2,3,5,16).
3. prefix_table (819 prefixes <= 3 digits): delta in {0 (225), 1 (21), 2 (3), 3 (9), 5 (3), 7 (3), 8 (3), 16 (6)};
   c = 0 (9) = degenerate.  delta depends on the digits mod 3 (f_omega digits are eaten 3 at a time).
   L12 leaves P = '26 33' -> '7' -> delta 0 (c2 = 79 = 37 mod 42, k2 = 17 = k1: identical rounds, no halt).
   The 11-state sibling (K = 0LC1LJ) leaves P = '1 2 6 0^3' -> delta 12 (c2 = 91, class 7 mod 14).
4. So R2 itself can NOT be steered (pinned by the base); only delta can.  c2 mod 14 = (9 + delta) mod 14.
5. Round-end type per counter class (base_table, c >= 100, n1 with J0 undefined):
   - 9: J0, standard far D2^k + n1 tail, k = 4(c-9)/14 - 3 (k mod 3 from c mod 42: 9 -> 0, 23 -> 1, 37 -> 2).
   - 5, 8, 11: J0 with D2^k + a DIFFERENT tail (class 11: D2^k 1111001000001000[J]0011110101..).
   - 1, 4, 6: J0 with NO far region (k = 0).
   - 10: J0 with irregular k.
   - 2, 7: base self-restart with a small counter (messy); 12: base self-restart with c = 79 (= round 1 again).
   - 0, 3, 13: junk (no J0 within 120+ stages).
   So any eater whose round-1 restart has delta in {1, 2, 6, 9, 10, 11, 13, 14 (k2=0), 16, 28 (k2=1), ...} reaches a
   J0 entry whose literal tape differs from the round-1 one: the eater can halt there with a spare slot.  The n1-notes
   condition (R = 12 or 5 mod 21) is the special case 'class 9 with k2 != 2 mod 3'; the class-5/8/10/11/1/4/6 ends widen it.

## k-faithfulness (important screening caveat, found ~17:30)
- The real round-1 end has k1 = 4(c1-9)/14 - 3 with c1 = 12B+7, B = 6 mod 2520 huge: k1 = 17 mod 8640, astronomically
  large, but still << R (the accumulator).  In the std follower R-rep = 19, so std eater tests are faithful only for
  k below ~2R-rep (L12: clean for k <= 47, junk for k >= 49 in std; with big policy R-rep 2539 L12 restarts cleanly at
  k = 17, 49, 77, 137 -> L12's eater is genuinely k-periodic (mod 3)).
- FALSE POSITIVE T13 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LM0LC_0LK0LL_0LK1RA_0LK---
  (clone-split of the delta=9 restarter ..._0LK0LL_0LK1RA): b0=6 follower: round 1, eater, clean restart c2 = 88
  (delta 9), full clean round 2, HALT M1 at stage 93 (T13_b6_std.log).  BUT its eater restarts ONLY for k = 17
  (kscan: k = 29, 41, 77, 137 halt M1 at eater stage 2, big policy too).  Not a candidate.
- Also a 14-state clone-split of the delta=1 restarter (..._0LC0LL_0LM0RA_1LE0LL + N) "halted" at stage 103 after
  round 2 in a messy phase; its base restarter is k=17-only too (kcheck) -> discarded.
- Fix: t1enum.py now runs kcheck (same eater, k = 29, 41 = 17 mod 12, std) at every phase-1 restart and branches on
  undefined slots read there; leaf KFAIL otherwise.  Final validation should use big policy k in {77, 137}.

## Remnant map (remnant.py -> remnant.tsv, ~17:00)
- n1 from PATTERN + 0^g + [7 1^329|1|19] (stray far-left bits at the left event), patterns <= 6 bits, g = 1..6:
  58 restart with c = 79, 69 with delta in {1..7, 16}, 189 re-enter J0 (eater would run again), 62 junk.
  E.g. a single stray '1' at gap 2 or 6 -> c = 81 (delta 2, class 11); '11' at gap 1/5 -> delta 1; '101' g2 -> delta 4.
  So the left event DOES merge leftover bits into the counter offset: an eater that robustly leaves such a remnant
  steers c2.  Gap dependence is mod 4 (bit parity of D-words).

## Scans (t1enum, start far_17 + [0 1^41|1|19], kcheck k = 29, 41)
- e2_a: ns=2, J0 = 0LK then 0RK (running).  e2_b: ns=2 J0 = 1LK: stopped at 41.6k nodes (K0 up to 0LL done
  partially; options order 0LA..0LL, 0RA.., 1LA..), 0 HALT2.  First (pre-kcheck) runs in old/.
- hm.sh: L12 + half-state M (one eater slot X of L12 redirected to M, all write/move; M one defined slot, other =
  halt): 20 sub-runs, 1060 nodes; restarts: only delta = 0 loops (10, some with the M halt slot never read) and
  KFAIL (c = 91, 97: k=17 accidents).  No HALT2.  -> L12 + half a state cannot steer delta.
- b3.sh: ns=3 around the L12 core (J0=0LK, K0=0LC; B1 K1=1LL fixed, B2 L = 0LK0RC fixed) (running).
- k=17-only restart families seen so far: delta 9 (c=88, ..._0LK0LL_0L?1R?), delta 12 (c=91, sibling family), 97.
  Every k-robust restarter found so far is in the L12 family with delta = 0.

## FIRST k-ROBUST delta-STEERING EATER (b3 scan, ~17:10): D1 family, 13 states, delta = 1
D1 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK1LM_1RJ1RM
  (L12 with L1 = 0RC -> 1LM, new M = 1RJ1RM: "skip right over 1s, write a 1 at the first 0, go to J"; it plants a
  stray bit, cf. the remnant map).  Variants: L0 in {0LK, 1LB, 1LH} x L1 in {1LM, 1RM}, M = 1RJ1RM (6 machines).
- Eater outcome: k = 2 mod 3 -> clean restart c2 = 4R+4 (delta 1, class 10 mod 14); k = 1 mod 3 -> delta 0; k = 0 -> junk.
  k-robust: std k = 17, 29, 41 (all k = 2 mod 3 in 5..46 except 3) and BIG policy k = 17, 77, 137: c = 10160 = 4*2539+4.
- Round 2 (class 10) ends at J0 with the irregular-k far; then a messy phase; no restart, no halt (MAX2); all 7 new
  slots are read in round 1 (droptest), so no 13-state halt from D1 itself.

## 14-STATE TIER-1 SCREENING CANDIDATE H14 (clone13 on D1)
H14 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LN1LL_0LK1LM_1RJ1RM_1RD---
  (D1 with K0 = 0LC -> 0LN, N = copy of C = 1RD0LB with N1 undefined = halt.)
- Real start, b0 = 6, std follower (H14_b6_std.log): round 1 = n1's round (stages 0-36), eater, clean restart at
  stage 50 with c2 = 80 = 4R+4 (depth kept, 415), FULL clean round 2 (stages 50-86, counter 80 -> 0), round-2 end J0
  (class-10 far) at 86, messy phase (depth-sized digits 426/252/150/91.. consumed), left event at 139, HALT N1 at 141.
- Eater k-robust (big policy k = 17, 77, 137: restart c = 10160, no halt in round 1).
- Round-2-end halt over representatives (val2.py, std): crafted round start [2 5 1^c 0^3 3 1^z|1|19] with
  (c, z) = (80,415), (80,2935), (80,1255), (80,575), (122,415), (164,415), (248,415): ALL halt at N1, always after the
  round end (stage 49-185).
- Big-policy check of the round-2 end: infeasible (literal stage > 2e9 steps at the eater after a 10^4-token round).
- Caveat: the halt comes after a messy post-round phase whose literal path involves depth-derived digits; the std
  world has depth > R-rep while in reality depth << current accumulator. Screening evidence only.
- Grade: 2 full rounds, the second reloaded from the accumulator (c2 = 4R+4): sigma ~ f_(omega+1)(f_(omega+1)(~2^^363))
  = Tier 1, but with 14 states (the BB(14) champion is only f_(omega+1)), not 12-13.

## Wrap-up (19:05)
- d1c2_M0free (L1=1LM, M1=1RM, M0/K/L free): stopped at 125,292 leaves, 0 HALT2 (5 MAX2 delta-1, 48 delta-0 loops).
  d1c2_M1free not run.
- H14 b0=846 replay: round 1 clean for ~4360 stages; at its end k1 = 2897 >> R-rep 19, so the std eater test is
  unfaithful (eater output '2^2885 1 5 35', then a literal timeout at 4e8 steps).  Inconclusive, not a refutation;
  a faithful large-k check needs big policy with bigk >= 3.
- REPORT.md written.

## H14 robustness answers (lead's 4 questions, 2026-10-09 ~19:40)
1. **Why round 2's end differs from round 1's.**
   - Round 1 ends in counter class 9 (c1 = 12B+7 = 79 mod 10080). That gives the standard J0 entry: D2^k1 + the
     44-bit tail, with k1 = 2 mod 3.
   - D1's eater leaves delta = 1, so round 2 runs with c2 = 4R+4 = 80 mod 10080 (class 10 mod 14). Its end is a
     class-10 J0 entry: a D2 run followed by a different, irregular tail ('..110101010100000100000100000..' for c = 80).
   - The eater turns this into a messy phase. It holds a chain of short "mini-round" starts with depth-derived counters
     (std: '1 2 5 1^419', then 249, 147, ...) behind surviving prefixes ('2^18 1 55 0 426 1 2^6 1 44 252 1 ...').
   - The phase ends at a J0 entry whose tape has '1 0' immediately left of the J0 cell. There J0 -> K (reads 0) ->
     K0 = 0LN -> N reads 1 = HALT (ntrace.py: J0@3141, then N1@3139).
2. **Why N1 is never reached in round 1, for the real k1.**
   - ntrace.py, round-1 eater at k = 29: state N is entered only 3 times. Twice it is inside the fixed 44-bit tail
     (contexts '..0100[0]0000111..', N reads 0). Once it is at the blank left end after the far region is eaten
     (all zeros).
   - K0 is never executed inside the D2 run, so the number of N entries and what N reads do not depend on k.
   - Measured: k = 2 mod 3 restarts with delta 1 and no halt for every k = 14..44 (std) and k = 17, 77, 137, 257,
     521, 1001 (big). k = 5 and 8 halt: a small-k boundary effect, since the real k1 is huge.
3. **Score.**
   - H14's round 1 is n1's run up to n1's halting J0 read, so the tape at that point already holds n1's output.
     That output is sigma(n1) ~ f_(omega+1)(~2^^363), and the accumulator R at the left event is at least of that size.
   - Round 2 has counter c2 = 4R+4. A round with counter c gives about c/14 growth periods, each raising the
     omega-level, i.e. f_(omega+1)(~c).
   - So sigma(H14) >~ f_(omega+1)(f_(omega+1)(~2^^363)). The messy phase only adds. This is a Tier-1 lower-bound
     shape, not computed exactly.
4. **Residue argument for the round-2 end (big policy literal infeasible).** The messy phase is driven by the
   counter class and the depth. Both were swept (val2.py, std; h14_val_cz.txt, h14_val_smallz.txt):

   | swept | values | result |
   |---|---|---|
   | counter c, depth z = 415 | c = 80, 94, ..., 360: every class-10 counter, all residues mod 42 and 168 up to 360 | 21/21 halt at N1, always after the round end |
   | depth z, c = 80 | z = 400..427: every residue mod 2, 3, 4, 7, 14, 28 | 28/28 halt at N1 |
   | small depth | z = 3..35 against c = 80 and 164 | 16/18 halt; 2 do not halt within 600 stages (c = 80 with z = 3 and z = 30) |

   - So inside the std world the halt depends only on c = 10 mod 14 once z is large. The real c2 = 80 mod 10080 is in
     that class.
   - z = 30 = 422 mod 28 halts at z = 422, so the two small-z failures are size effects, not residue effects.
   - OPEN RISK: in reality the depth is much smaller than the current accumulator. The std world has the opposite
     order (z ~ 400 > R-rep 19). The small-z exceptions show that the relative size of depth can matter.
   - BIG POLICY (R-rep 2539 > depth 415, the realistic order) with a 4e10-step cap: c = 80, z = 415 -> HALT N1 at stage
     89 (h14_val_big.txt).  More big cases (z = 100, 1001; c = 94, 164) in h14_val_big2.txt.

## in-place restarts
- H14 / D1, post-round-2 messy phase (std, H14_b6_std.log stages 87-139): repeated round starts '.. 1 2 5 1^m 0^3 43 1'
  with DEPTH-derived counters (m = 419, 249, 147, 84, 48, ..) behind a SURVIVING, growing prefix
  ('2^18 1 55 0 426 1 2^6 1 44 252 1 2^6 1 44 150 ..'). Nothing is written left of the far tail. They are short (they
  collapse into '2^9 47 1^z' within ~6 stages), not full rounds.
  Machine: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK1LM_1RJ1RM (D1).

## H14 post-round-2 mechanism and halting gamble (~19:50)
- After round 2 ends (class-10 J0), the eater starts a CHAIN of short mini-rounds (h14_c164_std.log stages 72-111).
  Each mini-round turns the current depth z into the next counter: z' ~ (3z - r)/5, where r depends on z mod 5
  (1036 -> 620 -> 372 -> 222 -> 132 -> 78).  Each mini-round leaves a prefix '1 2^7 1 41 0 z'' behind.
  When z gets small the chain collapses.  The collapse either ends at a J0 entry with '1 0' left of the J0 cell, giving
  K -> N reads 1 = HALT, or falls into an n1-type junk cycle that never halts (c = 80, z = 30: 40-stage cycle, zeros
  +30 per cycle, h14_c80z30_std.log).
- So the halt is decided by where an iterated (3z-r)/5 map from the real (huge) depth bottoms out.  That depends on
  ALL digits of the depth, not on a residue mod 2520.  Residue arguments cannot decide it.  It is a Collatz-type gamble.
- Empirical odds (std, c = 80): z = 1000..1199 halt 200/200; z = 400..427 halt 28/28; z = 2523, 2550, 5043, 5070,
  7590 halt; z = 3..35 halt 16/18 (z = 3 and 30 go to junk).  Every large start tested halts.
- Big policy (R-rep 2539): halts for (c, z) = (80, 415), (80, 100), (94, 415).
  (164, 415) did NOT halt within 400 stages; a logged rerun is in h14_c164_big.log.
- Status: H14's halt holds in screening for every large-depth case tested in std.  It is NOT provable by residues: a
  proof needs either an argument that every large chain bottoms out into the halting branch, or the exact depth.

## Realistic size order for the post-round phase (~20:25)
- In the real run the depth (~(4/3) of the previous accumulator) is far SMALLER than the current accumulator R''.
  Neither follower policy reproduces this: all accumulators share one representative, so depth ~ periods x R-rep >
  R-rep.  The chain's literal path changes with this order: R-tokens 2R+23 get inserted ('61' in std at small z,
  '5101' in big).
- realistic.sh crafts the post-round state directly from H14_b6_std.log's stage-84 J output
  '2^23 5 1^2 0^3 1 (2R+2) 0 1^685 | 1 R', with R = 19 + 2520 j and big policy bigk = j, so the R-tokens are much
  larger than depth 685:

  | run | result |
  |---|---|
  | j = 0 (std reference) | HALT N1 at +56 (as in the full run) |
  | j = 1 | HALT N1 at +151; the mini-round counters climb to ~2R |
  | j = 2 | HALT N1 at +15 |
  | j = 4 | HALT N1 at +23 |

  All end with the same terminal collapse '.. 2 3 2 1 5 1^m 0 3 0^3 1 0^3 X 0' -> '7' + far -> left event -> HALT N1.
- The c = 164 big run (unrealistic order: depth 78k > 5101) was stopped at stage 300 inside a slow a-block countdown
  ('1 4515 3 2', -3 per stage).  Its outcome is unknown.
- Updated H14 status: every case in the realistic order halts (3/3), as does every large-depth std case (233/233).
  The halt still depends on the exact chain, so it remains screening evidence.

## Depth-class caveat (lead, ~20:35): the real round-1-end depth is n = 35 mod 42 (std 329); n = 41 is the wrong class
- All t1enum scans so far used n = 41.  Re-test (depthcheck.txt, std, k = 17 and 29, n = 329, 371, 2849): every delta-1
  restarter restarts with c = 80 at all 6 points (54/54).  That covers D1 and its L0/L1 variants, the K0 = 1RI families,
  and H14's round-1 eater.  So the delta-1 eaters do not eat depth.
- H14's own evidence already used the real class: the b0 = 6 real-start follow and the big kscan are at n = 329, and
  the round-2 halt was swept over 233 large depths covering all residues mod 28.
- k0sweep.sh restarted at n = 329 (the n = 41 partial K0 = 1RI tree moved to old/n41/).  J0 = 0LK only, so it does not
  overlap inv-w2-inplace's J0 = 1RK family (T12a, H13c).
- Caveat for the earlier n = 41 negatives (e2_a/b, hm, b3, d1c, d1c2): a depth-sensitive halter could have been missed.
  The restart leaves they found are depth-robust where checked.

## k0sweep PAUSED (lead request, ~21:00; CPU cap)
- Stopped cleanly; no seed finished at n = 329 (no .done markers), so a resume restarts K0 = 1RI from scratch.
- K0 = 1RI at n = 329 (partial, DFS reached K = 1RI1LL, L = 1LB1LM): 152,752 leaves.

  | outcome | leaves |
  |---|---|
  | NORESTART | 138,385 |
  | W | 7,911 |
  | HALT1 | 2,939 |
  | T | 2,896 |
  | RESTART4 (delta-0 loops) | 306 |
  | KFAIL | 294 |
  | MAX2 | 21 |
  | HALT2 | **0** |

  The MAX2 leaves are 13 delta-1 restarts (c = 80) and 8 prefix restarts (c = 53 or 41).  No new eater class.
- Partial n = 41 tree for the same seed: old/n41/ (170k leaves, 0 HALT2).
- inv-w2-d13's complete s1 scan (194k leaves, D1-style K0-into-new-state space) found no halts either, so this seed
  space is low-yield.
