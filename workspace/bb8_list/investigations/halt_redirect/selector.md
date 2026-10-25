# Grow-and-count selector search (Fable, 2026-10-08)

Goal: a 10-state machine of the G/H-sibling family (base `1RB0RA_1LC1LF_1RD0LB_1RA1LE_??0LC_0RG1LD_1RH1LG_1LC0RG`,
E0 redirected to a new state I, J free) that EXTENDS its list from the latest accumulator on every cycle (as the
infinite 0RB rebuilder does) and also COUNTS cycles and HALTS when the counter runs out: f_(omega+1)-class.

Tools (halt_redirect/sel/): evtrace.cpp/ev.py (literal tracer printing every E0 read and every I/J read with a tape
window), stageu.py (one literal stage via stage35g, reports the slots read), fol.py (verbose follower = mf/ord_run.follow
with any machine / policy / constructed start, recursion-safe), gsearch.py + gs2.py (lazy TNF enumeration of the gadget
E0 in {0LI,0RI,1LI,1RI} x I0,I1,J0,J1 in 40 options, branching only on slots actually read, through literal stage tests),
gs3/gs4.py (follow lists of machines from a constructed / the real start), branch.py (follower-level TNF branching of
halting parents, family GH), ana.py / ana4.py (history analysers).  Logs in sel/logs/.

## 1. Mechanism: why 0RB grows and why 0LH counts

Every event of these machines is an E0 read; the base machine (BB(8) record minus E0) never reads E0 except at a list
exhaustion.  In the 9-state redirects E0 = 0LI, so state I reads the cell LEFT of the E0 cell: I0 (undefined) is the
halt, I1 is the gadget.  The record's exhaustion configuration is `101 (011)^(4r+8) 0 111(01)^8 00 (101)^n` with E0 read
right of the (011) run (q-1 = 1): the accumulator r is UNPACKED into 4r+8 blocks "011".  I1 decides how the blocks are
REPACKED (literal, evtrace):
* I1 = 0RB (the looper): every block becomes a one digit D4: `[1^n | 1 | r] -> [8 4^(4r+n+8) 1 37 18]` (the old zeros are
  re-set to ones as well).  The period is 2 stages: D8 -> D5 -> D2 block, then `[2 1^n | 1 | R] -> [2R+5 1^(n-1)]`, the
  huge digit is cleared, the borrow runs off the left end ("left" event), repack.  No structure survives a period, the
  list length after a period is 4R+n+8 with R the accumulator of a clearing at depth n: f_(omega+1) shape, never halts.
* I1 = 0LH / 0LA: the blocks are repacked as a D9 run with two zero digits per D9 (`[1^n | 1 | 19] -> [9^16 11 1^39 ..]`):
  the D9 run and the zero list are parked COUNTERS, nothing grows; the champion process only hits blockers (D0/D2/D3)
  and the whole run is omega-level 1 at index ~K (gh0LH_fable.md).  0LH halts at `[9 0 1^n | 1 | r]`-type stages (I reads 0
  at the far-left end of an unpack walk).
* Blocks at the far left behave differently per gadget: 0RB with a D9 run in front HALTS at `[9^k 0 1^n | 1 | r]` (k >= 2)
  and unpacks `[9 0 1^n | 1 | r] -> [2r+4 11 1^(n+11)]`.

So a grow-and-count machine needs: a repack that leaves a counter structure at the far left AND a periodic event that
unpacks an accumulator-sized token into list digits while consuming one counter unit, and a counter-exhausted event that
halts.  Such a family exists (section 2); its exhaustion event, however, is indistinguishable from its normal growth
event at the gadget level (section 3).

## 2. The D6-counter grower G6 (found by re-screening mf_GH/mg80 for "k grows, non-zero tokens shrink")

    G6 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1RJ1LA_1LI---     (E0 = 0LI, I = 1RJ1LA, J = 1LI---)
    twin  1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_1LA0RJ_---0LI     (same gadget semantics, same run)

Gadget semantics at an E0 read at cell q: write 0 at q; if q-1 = 1 go to A at q-2 (I1 = 1LA, like 0LA's repack but
writing 1); if q-1 = 0 write 1 at q-1 and at q (I0 = 1RJ, J0 = 1LI, then I1) and go to A at q-2.  J1 is unreachable (J
always reads the 0 that E just wrote).

Real-start run (mf35g single representatives r = 19, fol.py logs sel/logs/G6_std70.log; the same with r = 2539 "big",
r window 5059 "shrink", logs G6_big_b6.log / G6_shrink2_b6.log, 12 stages each; the lead's symbolic follow2 with
omega-level tracking: logs/G6_follow2.log):

    stage 0 (literal from the record's E0 configuration):  [6^u, 8, 1^m | 1 | 2],  u = (12b+8)/5
      (follow2: D6^{12/5 b + 8/5}, zeros 48/5 b + 217/5 after the first jump)
    first period (transient, 3 stages): 6^u 8 1^m -> 6^u 5 3 -> 6^u 5 0 43 -> 6^u 5 0 1^m -> 6^(u-2) 4 5 37 1^(m+8) ...
    PERIOD (3 literal stages + 3 jumps, consumes TWO D6, grows the zero list by 2R+5):
      [6^2j 4 C 1^n]            -J-> [6^2j 4 2 1^n | 1 | R']      C = 2r - R' + 7 (a counter: (C-2)/3 full cycles at depth n)
      [6^2j 4 2 1^n | 1 | R']   -lit-> [6^2j 1 (2R'+6) 1^n | 1 | 2]     (the accumulator is PARKED as a token)
      -J-> [6^2j 1 (2R'+3) 3 1^(n-1) | 1 | R'']  -lit-> [6^2j 1 (2R'+3) 0 (2R''+5) 1^(n-2) | 1 | 1]
      -J (full cycle at depth n-1)-> [6^2j 1 (2R'+3) 0 1^(n-1) | 1 | r]
      -lit (growth stage)-> [6^(2j-2) 4 (2r - R' + 7) 1^(n + 2R' + 4)]
    The growth stage is an E0/I0/J0 "walk" that unpacks the parked token D(2R'+3) into 2R'+5 zero digits four cells at a
    time (evtrace), then the base machine turns the two D6 next to it and the accumulator into the new counter token.
    Checked with r = 19 (counter 26, growth 43), r = 2539 / parked 5081 (counter 2546, growth 5083), r = 5059 / parked 41
    (counter 10106, growth 43): counter = 2r - (P-3)/2 + 7 exactly in all three, growth = P + 2.
    EXHAUSTION (no D6 left): [1 (2R'+3) 0 1^n | 1 | r] -lit-> [7 1^(n+2R'+4)] -J (7 -> 4 -> 1, left event)-> [1^N | 1 | R]
      -lit (repack, = stage 0)-> [6^u', 8, 1^(m')], u' ~ 0.8 R: a NEW ROUND with a counter of size ~0.8 R.
    In the single-representative world the run is exactly periodic with period 27 stages (8 periods + exhaustion + repack);
    follow2 reports omega-level 2 from stage 6 on (zero-list length 2R3 + 2R6 + ... : the list grows by a huge accumulator
    every period).

Score shape if it halted at the FIRST exhaustion: u/2 ~ 1.2B periods, period j does ~(2/3)C_j full cycles at depth n_j
(C_j huge) and then n_(j+1) = n_j + 2R'_j + 4 with R'_j the accumulator of those cycles, i.e. n_(j+1) >~ f_omega(n_j):
sigma ~ f_(omega+1)(1.2B).  As it stands the machine never halts: every exhaustion repacks a counter of ~0.8R D6 and starts
a new round, u_(i+1) ~ f_(omega+1)(u_i): an f_(omega+2)-SHAPED INFINITE machine (J1 is never read).  No M3 trap in the
period: the parked token is unpacked by a literal walk (cost linear in the token), the counter is consumed by jumps, and
the counter 2r - R' + 7 is positive because r (one full cycle at depth n-1 started from 2R''+5 >= 2R') >> R'.

## 3. Can the exhaustion be made to halt?  (negative, with proof-level evidence for this family)

The slots read (stage35g U mask) by every literal stage of the period and by the exhaustion stage are the same:
E0 E1 I0 I1 J0 + base (stageu.py).  evtrace shows WHY: the growth stage and the exhaustion stage are the same walk
(E0 at q, I0 at q-1, J0 at q, I1 at q-1, A at q-2, four cells left per step: `0001 0001 ...`), they differ only in what
the walk meets at its left end (the D6 run `...1011` versus the blank tape), and after the last gadget read NO I/J slot
is read any more in either stage (the base machine alone produces `6^(2j-2) 4 C 1^..` or `7 1^..`).  The last gadget read
sees q-1 = 0, q-2 = 1 in both cases; the first distinguishing cell is q-3 (1 = D6, 0 = blank), and with two free states
the walk cannot look there and still restore the walk.

Exhaustive check (gsearch.py): lazy enumeration of ALL gadgets E0 x I0 x I1 x J0 x J1 branching only on slots read,
through the growth-stage test T1 = `[6^4 1 41 0 1^19 | 1 | 19]` (160165 stage runs = leaves; 200k-step budget):
exactly 11 gadgets reproduce the growth stage (`6^2 4 26 1^62`):
  E0=0LI: 1RJ1LA_1LI---, 1RJ1LA_1LJ1LA, 0LJ1LA_1RI0RJ, 0RI1LJ_1LI0RF, 0RI1LJ_1LI1RA
  E0=1LI: 1LA0RJ_---0LI, 1LA0RJ_1LA0LJ, 1LA0LJ_0RI0RD, 1LA0LJ_0RJ0RD, 0RD1LJ_0LD0RA, 1LI1LJ_0LD0RA
Of these, 7 also reproduce stage 0 and the first-period transient (gs2.py chain EXH); ALL 7 give the identical exhaustion
output `7 1^95` (forced, see above) and hence the same infinite round structure (the 4 others have a different stage 0,
`2 1^82 0 5 1^36` / `4 1^80 0 6 1^36`, i.e. no counter at all).  No gadget halts at exhaustion, none reads J1 there.
Near variants (2885 gadgets whose T1 output still has a D6 prefix and >= 55 zeros, followed 50 stages from the real
start, gs4_near.tsv): the D6-family members (counter >= 10 at stage 0) either rebuild a counter at exhaustion
(c6 -> 0 -> 2/11/24: G6-type rounds), run off (W), stall, or halt EARLY with D6 left; the only ones that halt right after
their counter runs out are the c1 family of section 5 (constant growth) and three machines that consume the whole
counter in 7 stages with almost no growth (`1LJ0RD_---1LA`, `1LJ1LI_---1LA` with E0 = 1LI / 1RI).  A second enumeration
around c1's growth stage (T1c = `[6^3 0 1^20 | 1 | 19]`, gs_T1c.tsv, gs4_nearc.tsv) is reported in section 5.

## 4. Follower-level TNF branching of the GH tree (lead's suggestion (a))

mf_GH.tsv has 2036 rows halting at an undefined I/J slot; 69 of them show growth (k increases by >= 20 within >= 2
stages).  branch.py sets the halting slot to each of the 40 values and follows the children 30 stages (two levels).
Result: 2760 children, kinds LOOP 100 / MAXSTAGES 1544 / TIME 452 / WIDE 634, NO halting child at all (replacing the
halting slot removes the halt and nothing else halts within 30 stages), so no second level.  Nothing new here.

## 5. The halting counter-grower c1 (NEW best score shape found, omega-level 1 with index ~25B)

    c1 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---1LJ_0RJ0RF   (E0 = 1LI, I = ---1LJ, J = 0RJ0RF)
    (same run: ..._---1LJ_0RJ1RA; mf_GH.tsv had it as MAXSTAGES after 12 stages; it halts at stage 27 for b0 = 6)

Found by gs4 (real-start follow of the T1 near matches): D6 counter 27 -> 1, zeros 96 -> 196, HALT I0 at stage 27.
Run (logs sel/logs/c1_1LI_---1LJ_0RJ0RF.log std; c1_big_b6.log r = 2539; c1_shrink2_b6.log window 5059: identical event
chains, HALT I0 at stage 27 in all three; follow2 symbolic in b: logs/c1_follow2.log):

    stage 0:  [6^(4b+3) 2 3 1^(8b+48) | 1 | 2];  transient stages 1-10 (consume 4 D6);  from stage 11:
    PERIOD (2 literal stages + 2 jumps, consumes THREE D6, zeros + 13):
      [6^(3k+2) 4 (2R-7) 1^n | 1 | 1]  -J-> [6^(3k+1) 3 1^(n+2) | 1 | R']
          (2R-7 is a DIGIT: (2R-8)/3 full cycles at depth n, then 4 -> 1, then the borrow takes 6 -> 3, D3 blocks)
      -lit-> [6^(3k+1) 0 (2R'+5) 1^(n+1) | 1 | 1]   -J (one full cycle at depth n+1, D0 blocks)-> [6^(3k+1) 0 1^(n+2) | 1 | R'']
      -lit (growth stage)-> [6^(3k-1) 4 (2R''-7) 1^(n+13) | 1 | 1]
    follow2: stage 13+2j has D6^{4b-5-3j}, zeros 8b+71+13j (then "FAIL no period for b": a b-counter, as for 0LH).
    EXHAUSTION: [6 0 1^n | 1 | R] -> HALT in I reading 0 (the growth walk expects a second D6 and reads I0 on the blank);
      ones = 2R + 2n + 21.
    Literal grid (sel/c1grid.py, 58/58 exact): growth stage for m in {2,3,5,8} D6, n in {3,5,20,41}, R in {19,2539}
    -> 6^(m-2) 4 (2R-7) 1^(n+11); parking stage [6^m 3 1^n | 1 | R] -> [6^m 0 (2R+5) 1^(n-1)] for m in {1,2,5}; halt
    stage [6 0 1^n | 1 | R] -> HALT I0 for n in {3,20,41,200}, R in {19,2539} with ones = 2R + 2n + 21.  Growth stage
    also checked with R = 5059 (output 6 4 10111 1^31 from 6^3 0 1^20).
    Other start values: b0 = 6, 11, 16, 21, 26, 31, 46 all halt with the same final stage `6 0 (2R+5) 1^n -> HALT I0`.
    The D6 count at the "0 (2R+5)" stages runs 4b-6, 4b-9, ... ; for b = 0 mod 3 (b0 = 6, 21: the REAL class, B = 6 mod
    2520) it reaches 1 and the machine halts after ONE round (27 stages for b0 = 6, 67 for b0 = 21).  For b = 1, 2 mod 3
    the count reaches 2 or 0 instead: then `[6 4 (2R-7) 1^n] -> [0 (2R+5)] -> [7 1^N]` -> left event -> REPACK `[6^27 2 3 ..]`
    (a second round with a counter 4b'+3, b' = (R'-1)/3 from the left-event accumulator; R' = 19 mod 2520 gives b' = 0 mod 3)
    and the second round halts (b0 = 11: 69 stages, 16: 81, 26: 109, 31: 121, 46: 161).  So the real B gives one round.
    (b0 = 2526, the next member of the real class, was started: logs/c1_std_b2526.log, ~3400 periods.)
    The same gadget on the other three bases (mf35g families H, SIB, REC) gives the identical 27-stage run and halt
    (logs/c1H_std_b6.log, c1SIB_std_b6.log, c1REC_std_b6.log), so there is no base-family freedom in the constants.
    Siblings with the same period but a defined I0 (`0LI 0RD0RJ_1LI---`, `1LI 0RJ0RD_---0RF`, ... 12 machines,
    gs4_sib200.tsv) repack at exhaustion and run round after round (c6 27 -> 0 -> 27 -> 0 ...): f_(omega+1)-shaped, non-halting.
    A sibling for which the REAL residue led to the second round would be omega-level 2 (round 2 has ~4R'/3 periods,
    final depth ~25 R'/3): none exists in this family (the transient uses the same slots as the period, so the constant 7
    consumed before the periodic phase cannot be changed by the gadget).

Why it is not f_(omega+1): the growth stage turns the accumulator into a parked DIGIT token 2R-7 (cleared by the next
jump as ~2R/3 full cycles) and adds a CONSTANT 11 zeros; the depth grows by 13 per period, not by R.
Score: periods ~ (4B-6)/3 ~ 1.33B; final depth n_end = (76B+135)/3 ~ 25.3B; the last jump is one full cycle at depth
n_end+1 applied to 2R'+5 where R' is the result of (2R''-8)/3 ~ huge cycles at depth n_end.  In the lead's convention
(one cycle at depth d ~ f_(d+2)): sigma ~ 2 f_(n_end+3)(f_(n_end+2)^(huge)(..)) ~ f_(25.3B+3)^2(..).  Omega-level 1, but
the INDEX 25.3B beats every current BB(10) candidate (M3: f_(8B+51)^4; three-cycle F/H sibling: f_(K+42), K ~ 4.8B;
D9 counter: f_(K+3)), since the index wins over the number of cycles.  No M3 trap: the literal stages only write the
accumulator into a token (cost ~R^2, checked up to R = 5059) and add constants; every huge token is consumed by jumps.
Evidence level: mini-follower chain + three size-ordered policies + literal grid of all three period stages and the halt
+ 7 start values; no Coq, and the jumps rest on follow2's rules (R1-R3 + counter/blocker treatment).

## 6. Verdict on the f_(omega+1) design in 10 states

Reachable in SHAPE (G6: accumulator-sized growth per period with a D6 counter, omega-level 2 after 6 stages), and
halting-at-exhaustion is reachable in SHAPE (c1: the walk reads an undefined slot exactly when the counter has one D6
left).  The two have not been combined: in G6 the unpack walk itself reads I0/I1/J0 at every step (the "0001" pattern
needs q-1 = 0), so exhaustion is invisible; in c1 the walk reads only I1/J0/J1 (q-1 = 1) and the accumulator ends up
as a token, not as list length.  An f_(omega+1) machine needs an unpack-into-digits walk whose E0 reads all have q-1 = 1
(or a J1 reached only on the blank).  Searched: the complete gadget tree around G6's growth stage (160165 leaves) and
around c1's growth stage (gs_T1c, see table), each followed from the real start; none found.  With the base family
fixed and only I/J free (and J1 unreachable in the G6 gadget), I consider it unlikely but not excluded: the remaining
freedom is a different base sibling (H / SIB / record families of mf35g) with the same two gadget ideas.

## 6b. n1: the grow-and-count machine (found after the lead's correction: judge growth by the CLEARED list)

    n1 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC   (E0 = 1LI, I = 0LJ0LI, J = ---0LC; J0 = halt)

mf_GH/mg80 listed it as HALT after 37 stages with small k-growth (total token count), so every k-based filter (the
lead's and my first one) dropped it; filtering the histories on 'zeros=' (the list a jump clears) finds it: zeros
32 -> 329 over 37 stages, non-zero tokens 85 -> 1.
Run (std r = 19: logs/n1_1LI_0LJ0LI_---0LC.log; big r = 2539: n1_big_b6.log / n1_big40_b6.log):
    stage 0: [2 5 1^79 0^3 9 1^32 | 1 | 1]  (parked list 1^79 behind D2/D5 blockers: the COUNTER; 32 zeros: the cleared list)
    PERIOD (6 stages, 6 jumps; the counter list loses 14, the D2 run gains 4, the cleared zero list gains (4R+4)/3):
      [2^k 5 1^m 0^3 1 (2R'+3) 0 1^n | 1 | R]  -lit->  [2 (2R+3) 1^(n + (4R+4)/3)] + ~130 far bits (the parked region)
        (std: zeros 31 -> 59 -> 87 -> 113 ...; big: 32 -> 3419 -> 6807 -> 10193 -> 13581 -> 16967 -> 20355: +3388 = (4*2539+4)/3)
      -J (2R+3 = 2 mod 3 is borrowed down to 2: ~2R/3 full cycles at the new depth; ev=block)->  [2^2 1^n'] + far
      -lit->  [2^(k+2) 5 1^(m-8) 0^2 (2R+5) 1^n']   -J->  [.. (2R+2) 3 1^(n'-1)]  -lit->  [.. (2R+2) 0 (2R+5) 1^(n'-2)]
      -J->  [.. (2R+2) 0 1^(n'-1)]  -lit->  [2^(k+2) 5 1^(m-10) 0^2 (2R+1) 1^(n'+28)] ... -> [2^(k+4) 5 1^(m-14) 0^3 1 (2R+3) 0 1^n'' ]
      every jump of the period clears the whole zero list (ev=block, zeros = n): full cycles at depth n.
    EXHAUSTION (counter list gone, b0 = 6 at stage 35): [42 1^n] + far -> [0 (2R+5) 1^(n-1)] -J-> [0 1^n | 1 | R] + far
      -lit-> HALT in J reading 0.  Replayed from the log with its far bits for R = 19 and 2539: HALT J0, ones = 2R + 735;
      WITHOUT the far bits the same tokens give `7 1^(n+80)` (no halt): the parked region takes part in the detection.
    Literal replays of two period stages with R = 19 / 2539 (stage 29, 30 of the std log, with far bits): same shape,
    tokens 2R+5 / 2R+3 scale exactly.
Shape: n_(j+1) = n_j + (4R_j+4)/3 with R_j the accumulator after ~2R/3 + 5 full cycles at depth ~n_j: n_(j+1) >~ f_omega(n_j);
the counter 1^79 (b0 = 6; formula in b from the other-b0 runs) loses 14 per period: ~(12B)/14 periods if it is ~12b.
If it holds: sigma ~ f_(omega+1)(0.86B)-class, the design the lead asked for.
follow2 (symbolic in b, logs/n1_follow2.log): counter list D(1)^{12b+7} at stage 1, 12b-7 at stage 6, 12b-9 at stage 9
(-14 per period); cleared zero list 32 (level 0) for the transient, then 4/3 R3 + 35 at stage 6 (omega-level 1) and
4/3 R3 + 4/3 R6 + 39 at stage 9 (omega-level 2): the level rises by one per period, exactly the 0RB looper's growth
signature, now with a b-counter.  The parked far bits are IDENTICAL in the std and big worlds at every growth stage
(236, 214, 192, 170, 148 bits at stages 5, 11, 17, 23, 29), so the halt replay with R = 2539 is valid for the big world
too; the big-policy run itself reproduced the structure for 29 stages (4.5 periods) and then hit the follower's
recursion limit (30515 zeros), a tool limit.
Shrink policy (parked tokens shrunk to their residue class, r in the 2539 window; logs/n1_shrink1_b6.log, 14 stages):
same event chain; the growth stage [.. 1 P 0 1^n | 1 | R] -> [2 (2R+3) 1^(n + (2P+4)/3)] shows that the zeros come from
the PARKED token P = 2R'+3 of the previous period (P = 40: +28; P = 5080: +3388), the new parked token from the current R;
no comparison between the two sizes, so no M3 trap (the stage unpacks P into 2P/3 zeros and erases it).
Endgame and residues: the counter list is 12b+7 and loses 14 per period, so the exhaustion phase depends on b mod 7.
b0 = 6 and 20 (b = 6 mod 14) halt identically (`[0 (2R+5) 1^n] -> [0 1^(n+1) | R] + far -> HALT J0`, stages 37 and 109,
ones 773 / 2213 = 2R + 735 / 2R + 2175); b0 = 11, 16, 21 reach a junk structure after exhaustion and continue for 100+
stages (no halt seen); b0 = 34 and 48 halt the same way at stages 181 and 253 (ones 3653, 5093): 37 + 72k stages for
b = 6 + 14k, i.e. 12 periods per 14 units of b, as the counter formula predicts.  The real B = 6 mod 2520 is in the halting
class (B = 6 mod 7, even), and b0 = 6 is its mini-follower representative.
Far region structure: the parked bits are (10101)^k (a run of D2 tokens; k = 17 at b0 = 6 before the halt) followed by
the FIXED 44-bit tail `10110101010101010010000010111100100100100100`; identical in the std, big and shrink worlds and
depending on b only through k.  Halting-stage replays `far + [0 1^n | 1 | R]`: HALT J0 for k in {2, 23, 71, 200},
n in {50, 329, 977}, R in {19, 2539}; the step count does not depend on k (the head never enters the D2 run);
ones = 2R + 2n + 3k + 26.  Literal probes used R in {19, 2539, 5059} (one class mod 2520, different residues mod 16, 25,
27, 11, 13) with outputs affine in R: no finer residue dependence visible.  Lead's real residues: B = 6 mod 14 (halting
class), R = 49612750485498 mod 54305848396800.  Not checked: b = 2526 itself (too long under the CPU cap), Coq.
follow2 was stopped at stage 12 (omega-level 2, each stage at level >= 2 takes minutes) to free the single CPU slot.

## 7. Results table

| search | size | outcome |
|---|---|---|
| mf_GH / mg80 re-analysis (k grows, non-zero tokens shrink) | 11447 + 1005 rows | one family: G6 (D6 counter, 2 per period, R-growth), non-halting rounds |
| gsearch around G6's growth stage `[6^4 1 41 0 1^19]` | 160165 leaves | 11 exact growth-preservers, 7 with the same stage 0, all forced to `7 1^95` at exhaustion |
| gs4: real-start 50-stage follow of the 2885 near matches | 2885 machines | D6 families: rebuild / W / early halt; c1 family (constant growth) halts at exhaustion |
| branch.py: 69 growing halting parents x 40 | 2760 children | no halting child |
| gsearch around c1's growth stage `[6^3 0 1^20]` | 167685 leaves | 11 near matches with >= 55 zeros, none a counter family (gs4_nearc.tsv) |
| c1 verification | 58 literal grid checks, 3 policies, 7 start values, 3 base families | consistent halt, ones = 2R + 2n + 21 |

Verdict (updated): the f_(omega+1) grow-and-count design IS realised by n1 (section 6b) if its chain survives the
pending checks: R-proportional growth of the cleared list per period, a parked counter list, halt at exhaustion
(literal halt replays with far bits for R = 19 / 2539).  c1 (section 5) stays as the best omega-level-1 fallback
(index ~25.3B).  n1's evidence: mini-follower chain (b0 = 6, 20, 34, 48 all halt), follow2 omega-level chain to level 2
(stopped for CPU), big/shrink policies, literal halt replays with far bits for R = 19/2539; no Coq.  G6 is the non-halting f_(omega+1)/f_(omega+2)-shaped cousin.  The negative gadget-enumeration results
of section 3 apply to G6's walk only.
