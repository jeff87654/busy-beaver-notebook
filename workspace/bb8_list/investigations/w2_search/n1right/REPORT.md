# Route 2 (outer counter d right of n1's accumulator): REPORT (Opus investigator, 2026-10-09)

## Verdict: NEGATIVE. Nothing can be stored right of the accumulator. The right end is n1's growth frontier.
Evidence level: literal twin-simulation measurements on n1 and L12. This is screening evidence, not a proof. Task 3
(gadget enumeration) was not run because no round-boundary-only hook exists on the right.

## The measured rule
1. **Every literal stage rewrites the right end.** For all 51 literal stages of an L12 round (stages 0-50 of
   L12_b6.log), the head's rightmost cell equals the stage's K-moment position. The head moves the word end right by
   2R+c and never goes past it.
   - c = 4 or 6 in period and exhaustion stages.
   - c = 10 in the eater stage (K = 7 1^474).
   - c = 14 in the restart stage (K = 2 5 1^79 0^3 9 1^472).
   - The offsets are identical for R = 19, 79, 139, 259 and 2539 (logs/reach_L12.txt, all 51 stages) and for
     R = 5059 (stages 0, 5, 34, 45 and 46: 10122, 10124, 10122, 10128 and 10132; logs/reach_L12_R5059.txt).
   - Per period, the word end moves right by six stage terms 2R_i+c_i plus six jumps of 2R'+O(1) each, where R' is
     f_omega-sized. Per restart it moves 2R+14. The rightmost reach is always the new word end, at every R tested.
2. **Jumps extend the right end without bound.** In the B-form rules, a PASS adds 2 cells and a PRO adds 5 cells.
   - A literal champion-process run from K = [2 5 1^79 0^4 43 1^2 | 1 | 1] reached 637, 2015, 5709 and 19341 cells
     right of the word after 1e5 to 1e8 steps (about sqrt(steps)).
   - A single bit at gap 10, 100, 1000 and 10000 was first read at steps 374, 4552, 242598 and 27362220, by A1 or G1.
   - In the real machine each jump's accumulator R' is f_omega-sized. Any structure right of the word is therefore
     overrun in the first jump after it appears.
3. **Nothing survives, and no hook exists.** Patterns tested: all bit patterns up to length 8 plus unary-token
   patterns 1^d(01^d)^(c-1) for d <= 6, at gaps 1-8 and at gap 2R+c+1.
   - Stages: L12 period, exhaustion, eater and restart stages, plus n1's no-far restart.
   - At gaps 1-8 every pattern is read inside the stage. It is either merged into the tokens (about 95%) or turns
     into junk (time-outs, and J0 halts inside n1's restart stage).
   - Not one case was erased cleanly, kept, or shifted.
   - At gap 2R+c+1 the stage does not touch the pattern, but it then sits next to the new word end and is read at
     step 1 of the next jump.
   - The first divergence is always H1 (odd gap) or G1 (even gap). Both are core engine transitions read in every
     stage's U mask. So no transition reads the right side only at a round boundary, and the k-gram test is moot.
4. **The real start puts nothing there.** At every K-moment and J-moment of every follower log the tape right of the
   word is blank (the K rule requires it, and fact 1 shows each stage ends at its own rightmost cell). A d on the
   right would have to be rewritten into every stage's frontier. That is impossible without changing G and H, which
   are the engine itself.

Compared with G6 and the left end: the left end is overwritten about 6R-8R cells at each restart (unpack). The right
end is overwritten in every stage (+2R+c) and every jump (+2R'). n1 has no side where an outer counter can sit
outside the list. The only durable non-list storage is the far region (the D2 run plus the tail), which L12's eater
destroys.

## Side result: a counter-class lever (for the route-3 investigator)
At the no-far restart stage J = [1^(n+1) | 1 | R] (n1's restart, also L12 stage 46), place a block (10)^j right of
the word at any odd gap g with g + 2j <= 2R+3. The result is a clean round start [2 5 1^(4R+3+2j) 0^3 9 1^n]: the
counter is 4R+3+2j and the depth is unchanged.
- Checked exactly for R = 19, 79 and 259 with j = 1..10 (lever2.py), and for single bits over all gaps
  (logs/lever_n1_restart.txt).
- Even gaps give other clean counters (for example R=79: 1@150 gives 1227 and 1@156 gives 629) or junk.
- The counter class mod 14 shifts by 2j. j = 7 keeps n1's halting class (9 mod 14) and shifts k2 = 4(c2-9)/14 - 3
  by +4, so k2 mod 3 shifts by 1.
- **Caveat.** The frontier cell is read at step 1 of every stage, so the block must already exist at the J moment,
  and only the preceding jump writes there. A gadget can reach the lever only by ending a literal stage (for example
  L12's eater stage 45) with bits right of the K head. The next jump then absorbs them into its first a-token and
  doubling. The net effect is an accumulator-class shift of the next round, not storage.

## Candidate machines
None.

## Tools (this directory)
- rtwin.cpp/.exe: lockstep twin simulator. It compares a base tape and a tape with a right-side pattern, and reports
  the base K, the head's rightmost cell, the first pattern read, the first divergence, and the outcome with the
  remnant bits.
- rtwin2.exe: the same simulator with RCAP < 0 allowed (K cuts disabled).
- rlib.py: the driver.
- logcfg.py: turns an nfol log into J configs.
- reach.py: reach per stage and per R.
- surv.py: classification of right-side patterns.
- jumpreach*.py: the literal jump frontier.
- lever.py, lever2.py: the restart lever.
- Copied unchanged: sim/nfol/fstep/gstage/gtrace/kgram.
- g++ is at C:/msys64/ucrt64/bin.

## Recommended next step
Drop route 2. An outer counter in n1 needs a place outside the list, and only the far region qualifies. A d there
must survive the eater, so route 3 (or an eater that leaves part of the D2 run as d) is the remaining n1 option.
The (10)^j lever above is a cheap way to steer the round-2 counter class, if a literal-stage gadget can leave bits at
the K head.
