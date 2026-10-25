# n1right: route 2 (outer counter d right of n1's accumulator) -- notes (Opus investigator, 2026-10-09)

## Tools (this dir)
- rtwin.cpp/.exe: lockstep twin simulator (server). Base tape = word (far + tokens + 1010, head right in G); patterned
  tape = same + PATTERN at word_end + GAP. Reports base K-moment (strict gstage rule: nothing right), bmax = rightmost
  head cell - word_end, first read of the pattern region, first (state,sym) divergence, patterned outcome (K with a
  12-cell blank margin, remnant bits right of the K head). RCAP < 0 disables K cuts (rtwin2.exe build, env RTWIN).
- rlib.py (driver, word(), twin()), logcfg.py (nfol log -> J configs), reach.py (bmax per stage x R),
  surv.py (pattern classification), jumpreach.py / jumpreach2.py (literal champion-process frontier).
- copied: sim.py nfol.py fstep.py gstage.* gtrace.* kgram.* kg.py kgcmp.py (from ../n1, ../g6; unmodified).
- compiler: C:/msys64/ucrt64/bin/g++ (not on the Git-Bash PATH).

## Facts
1. Every literal stage ends exactly at its rightmost cell: bmax = koff (K-moment offset) for all 51 stages of an L12
   round (logs/reach_L12.txt, stages 0-50 of L12_b6.log, incl. exhaustion 34-43, eater 43-45, restart 45-46, round 2
   start 47-50). bmax = 2R+4 (R1/R3-type stages), 2R+6 (stages ending with r=2), 2R+10 (eater stage 45, K = 7 1^474),
   2R+14 (restart stage 46, K = 2 5 1^79 0^3 9 1^472); identical offsets for R = 19, 79, 139, 259, 2539.
   So the right end of the word moves right by 2R+c in EVERY stage and the head never goes past the new word end.
2. Jumps (follower K->J, the champion process) extend the right end monotonically (PASS +2 cells, PRO +5 cells,
   per the B-form rules): literal run from K = [2 5 1^79 0^4 43 1^2|1|1] with K-cuts off: head reach 637 / 2015 / 5709 /
   19341 cells after 1e5 / 1e6 / 1e7 / 1e8 steps (~sqrt(steps)); a single bit at gap 10 / 100 / 1000 / 10000 is first read
   at step 374 (A1) / 4552 (G1) / 242598 (G1) / 27362220 (G1).  In the real machine each jump's accumulator is f_omega-
   sized, so the frontier passes ANY fixed gap within the first jump after a pattern is placed.
3. Consequently the tape right of the word is blank at every K- and J-moment (also forced by the follower's K rule,
   which held for every stage of every log): the real start puts nothing there, and nothing put there survives a jump.
4. Pattern classification (surv.py; all bit patterns starting with 1 of length <= 8 plus unary-token patterns
   1^d(01^d)^(c-1), d<=6, c<=3; gaps 1..8 and bmax+1; logs/surv_L12.txt, logs/surv_n1_restart.txt):
   - gaps 1..8: EVERY pattern is read inside the stage. Classes: Md (merged into list/accumulator tokens, nothing left
     right of the word) ~95%, T (junk, no K within 20x the base stage length) ~2-5%, H (n1 restart only: junk J0 halts
     inside the restart stage). Erased-clean E = 0, preserved/shifted S = 0, X (tokens changed and bits left) = 0.
   - gap bmax+1: untouched by the stage (U) but then sits right next to the new word end (K head + 1), i.e. it is read
     at the first step of the following jump.
   - first readers (first divergence): only H1 (pattern at odd gap: G0 = 1RH writes the frontier, H reads it) and G1
     (even gap); in the jump also A1. These are base engine transitions read in every stage (U masks feff/bffff/...
     all contain G1 = slot 13 and H1 = slot 15) => no round-boundary-only hook exists on the right.
5. MERGE LEVER at the no-far restart (lever.py, lever2.py; logs/lever_n1_restart.txt): J = [1^141 | 1 | R] (n1's and
   L12's restart stage) with a block (10)^j right of the word at any ODD gap g, g + 2j <= 2R+3:
   clean round start [2 5 1^(4R+3+2j) 0^3 9 1^n] (depth unchanged), checked for R = 19, 79, 259 and j = 1..10 exactly.
   The block is absorbed as j extra accumulator units during the restart's doubling.  Even gaps / other patterns give
   either other clean counters (e.g. R=79: 1@150 -> 1227, 1@156 -> 629; R=19: 1@18 -> 735, 1@36 -> 149: a bit met later
   in the doubling) or junk.  Counter class mod 14 shifts by 2j: j = 7 keeps n1's halting class 9 mod 14 and shifts
   k2 = 4(c2-9)/14 - 3 by +4 (k2 mod 3 by +1).
6. L12 classification complete (stages 0,2,4,5 period; 34,35 exhaustion; 43,44,45 eater; 46 restart): near gaps only
   Md / T, far gap only U-then-adjacent; first divergence always H1 or G1.  L12 stage 46 reproduces the lever
   (1@1 -> counter 81 = 4R+5, 101@1 -> 83).
7. Practical reach of the lever: the frontier cell right of the word is read at step 1 of every stage (G0 = 1RH writes
   the word-end cell, H reads the next: '1 H1 rel=1'), so a block must already exist at the J moment, i.e. be written by
   the preceding jump (base transitions only).  A gadget can only influence it by ending a LITERAL stage with bits
   right of the K head (e.g. a modified eater stage 45), which the next jump absorbs into its first a-token/doubling:
   the effect is an accumulator-class shift of the next round, nothing more.  No storage across a jump.
VERDICT: route 2 closed negative (see REPORT.md).
8. Big-R check (lead request; one Idle process; logs/reach_L12_R5059.txt): stages 0, 5, 34, 45, 46 at R = 5059 give
   bmax = koff = 10122 / 10124 / 10122 / 10128 / 10132 = 2R+4 / 2R+6 / 2R+4 / 2R+10 / 2R+14, the same offsets as at
   R = 19..2539.  The tokens scale too (restart counter 20239 = 4R+3; eater K = 7 1^20634).  So the reach is exactly
   affine in R: per period the word end moves right by six stage terms 2R_i+c_i plus the six jumps (2R'+O(1) each,
   R' f_omega-sized); per restart by 2R+14.  The rightmost reach is always the new word end.
