# c7m12 group-2 tail lead: the (10)^Y sublist at g's end configuration

Status: DONE (2026-10-08). Verdict in section 4.

Machines: g = `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---`,
h = `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RE0LG_1RH---` (see `bb9_c7m12_1RB0RA_0RI0LC.md` section 9).
Start: g's real end-of-list configuration `bb9_c7m12_1RB0RA_0RI0LC/g2/endtoks_B6.txt` with D(6139) exhausted to D1 and
accumulator D(X) (as in `endhalt.py` / `endtest.py`).

Question: is the `11 (10)^Y` sublist (Y = 48*4^b - 9) consumed as a LIST of accumulator-dependent length (omega-level
>= 2 potential), or as a unary token/counter? Where is the undefined transition read?

Scratch: `bb9_c7m12_tail/` (`nxt.py` builds g-world token configurations and runs the tracer `tr9t.exe` = copy of
`tr9run3.exe`; `renum_c3.out`; `t_completions.txt`). Simulators were run at Idle priority, one at a time.

## 1. What the (10)^Y sublist is (hand analysis + literal traces, g, X = 2, 5, 8)
Notation as in `bb9_c7m12_1RB0RA_0RI0LC.md`: D(m) = (10)^m 1; champion digit d is D(3d+1); the a-digit is D(3a+1);
the accumulator b is D(3b+2), followed by g's merged-counter tail. End configuration (B = 6 proxy, k = 6 groups):
`P5 D4 D2 D2 | d = D1 | a = D1 | acc D(X)`, X = 3b+2, where P5 = `11 D4 D9 D6 D210 D14 D10 (D4 D2 D7)^5`.

Literal token trace of g (`tr9 dshape`, X = 2 and 5; every snapshot read off):
1. a = 0 and d = 0, so R3 borrows. The accumulator is moved into a new a-digit while the borrow walks left
   ((10)^2, (10)^4, ... (10)^12 for X = 5). The walk crosses D1 and the two D2 tokens.
2. `D2 D2 D1 D1` collapse into a single `D0` = one cell `1`. Together with the terminating 1 of the group's D4 this
   is a fresh **list prefix `11`**. Result: `P5 D4 | 11 | a = D(6b+7) | acc D2`, i.e. a K-type list with **zero
   digits**, a = 2b+2, b = 0 (X = 2: `4 0 7 2`; X = 5: `4 0 13 2`).
3. Champion R1 runs a = 2b+2 times: acc b -> 2b+2 each round. Final acc b_f = 2^(2b+3) - 2 = g(b) (X = 2: 6; X = 5:
   30; X = 8: 126). This is exactly one more champion digit decrement.
4. a = 0 and there is no digit left: R2's borrow converts acc into the new a-digit, which is the run **(10)^Y,
   Y = 6 b_f + 3 = 48*4^b - 9** (39, 183, 759), and walks left onto the `11` prefix. D1 = 1LE, E reads the 0 of the
   D4's last `10` pair (this is the champion's own end-of-list move, an A-event), E0 = 0LI moves onto the 1 of that
   pair: **I1, undefined in g: HALT** (steps 26571 / 166951 / 1287179 for X = 2 / 5 / 8; ones 448 / 592 / 1168).
   Same for h (E0 = 1LI, I1 undefined): 26639 / 167301 / 1288675 steps, ones 449 / 593 / 1169.

So **the (10)^Y run is not a list**: it is the accumulator (half converted into an a-digit) of a champion list
that has no digits at all. Its length is accumulator-dependent (Y ~ 6 b_f), but it carries one number, and in g it
is never read again. The list whose exhaustion causes the halt has length 0 (built from `D4 D2 D2 + d + a`), not
an accumulator-dependent length. g and h stay at omega-level 0 (score ~17.1*(2^^13 3), as in section 9 of the c7m12
report); nothing here changes that verdict.

Tape at the halt (X = 2), head in I on the cell marked: `... (D4 D2 D7)^5 (10)^3 [1]0 1 1 (10)^39 0 11 00 ...tail`.
The undefined slot read is **I1**, with the 1 of the last group's D4 under the head, the `11` prefix to its right
and the remaining k-1 = (12B-37)/7 groups (plus the merged prefix) intact to its left.

## 2. Which 9-state machines can continue past this halt
- g and h use all 17 defined transitions (transition counts on the end-configuration run and over 4e8 steps from
  the blank tape: every slot except I1 is used). Defining I1 leaves no halting slot, so g and h have **no 9-state
  completions**. The same holds for the group-2 variants #5 `..._0LG0RE_1RH---` and #9 `..._1RG0RE_0RH---`.
- The only 9-state group-2 base with a spare slot is #3 = `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_---0RE_0RF---`
  (H0 never used, I1 = halt). It is in the c7m12 holdout list. Its I1 was never branched by the enumeration,
  because #3 did not halt within the enumeration's budget. It is token-identical to g and halts at the same I1
  event (26501 / 166599 / 1285681 steps, 448 / 592 / 1168 ones, for X = 2 / 5 / 8).
- **Enumeration** (`halt_redirect/renum.exe` #3 9 starts 2e8 1e6, run unchanged; starts = g's end configuration
  for X = 2, 5, 8; output `bb9_c7m12_tail/renum_c3.out`): 36 completions of I1, with H0 the only halting slot left.
  - 7 halt in H0 immediately after the event, with ones 448 +- 1 (or 191 for I1 = 0LE). These are g's score: not
    records. The 7 are I1 = 0LE, 0LF, 0LG, 0LH, 0RH, 1LH, 1RH.
  - 29 do not halt within 2e8 steps for any X (`t_completions.txt`).
- `1RE` is a 2-cycle: E0 = 0LI and I1 = 1RE bounce on the same two cells forever (checked to 1e6 steps). It does
  not halt.
- **For all 28 others, the (10)^Y run becomes ONE token.** The first right-edge snapshots after the event for
  X = 2, 5, 8 have identical token lists except for one token of value Y + c (c = -4..+8 depending on I1; for
  example I1 = 0RE gives `P4 4 2 6 (Y+7) ...` with 46 / 190 / 766). So the accumulator turns into a single digit
  (an a-digit or list digit) of value about Y/3 = 2 b_f + 1, as in champion R2. It never becomes a list whose
  **length** depends on Y.
- Token-identical classes after the event: {0RE, 0RF, 1LG}, {0RB, 1LD, 1LI}, {1RB, 0LC}, {0RC, 1RD, 1RI},
  {0LB, 1RC}, {1RG, 0LI}, {0RD, 0RI}. The singles are 0LA, 0RA, 1LA, 1RA, 1LB, 1LC, 0LD, 1LE, 1LF, 1RF, 0RG.

## 3. What the continuing completions do (mini event follower, proxy accumulators)
Tool: `bb9_c7m12_tail/fol9b.py MACHINE TOKENS X1,X2,X3`.
- It starts from g's end configuration (`P5 4 2 2 1 1`) and runs literally (tr9 `dall`) until a canonical
  snapshot (numeric a-digit and accumulator followed by g's tail) has a token above 30.
- Then it JUMPS. The rightmost token that is not a 3d+1 digit (or a raw block) is the blocker; every token to its
  right is set to D1 (= 0), i.e. the champion rules are taken to exhaust them, and the accumulator is reset to D(X).
- Each event is run for X = 5, 8, 11 (b = 1, 2, 3).
  - **ACCDEP** = the next list's token count differs across X: a list whose length depends on the accumulator was
    built.
  - `zeros=` = the number of tokens the jump clears.
  - Any HALT, for any X, is printed with the tape.
- With `--shrink 40`, a numeric blocker above 40 is reduced to its class mod 12, plus 12.
- The parser fails loudly: a snapshot that is not in g's tail form is never used for a jump.
- Validation:
  - from the same start, g reproduces its literal halt (26571 steps, 448 ones);
  - every hit is a literal configuration;
  - a jump only zeroes 3d+1 digits that the champion rules consume.
- Caveat: it is a proxy (small accumulators, shrunk big blockers). The regime of the real run, where the
  accumulator is far larger than every fixed token, differs at some events (3.2).

### 3.1 The group conveyor is unary
- In every class the first events consume the k - 1 remaining groups `(D4 D2 D7)` one at a time from the right.
- Each group turns into one or two digits whose values come from the accumulator (for example I1 = 0RE gives
  `P4 4 2 6 a` -> `P3 4 2 4 (big) ...`). Groups further left are untouched until the borrow reaches them.
- No ACCDEP event and no growth of the token count happen while groups are consumed.
- So the ~1.7B groups are a **unary counter**. Each group applies a bounded-level function to the accumulator, the
  same picture as the 27 non-halting 10-state endtest relatives.

### 3.2 The merged prefix, the Q token, and accumulator-length rebuilds
After the groups, the borrow reaches the merged prefix `11 D4 D9 D6 D(Q) D14 D10`, where Q = 212*4^b_f - 2 is
the only token that depends on the second-level counter.
- **I1 = 0RA (literal):** when the borrow reaches D0 and then D(Q) with accumulator X:
  - D(Q) loses X+1;
  - the zeros between are rebuilt into a list `D3 0^(2X+4)` that is consumed by R1-R3. Examples:
    `155 0 1*6 | 5` -> `149 3 1*14 2`; X = 8 gives `146 3 1*20`; X = 14 gives `140 3 1*32`.
  - That is an **accumulator-length champion list** (f_omega-type step).
  - When X+1 > Q (the real regime, since the accumulator is far larger than Q there), D(Q) and the D6 are used
    up. The new list length then saturates at 2Q+7 (Q = 18: `4 9 1 7 1*43` for X = 20, `4 9 1 19 1*43` for
    X = 26), and the excess goes into one digit.
- **WHOLE exhaustions (all classes seen so far):** when the borrow walks off the left end `11` with blank on the
  left, I0 = 0RF repeats g's first rebuild with the new accumulator.
  - In the completions the rebuilt list is later consumed as a champion list.
  - Literal example, I1 = 0LA, from `2 5 | X = 8`: `0*2 4*2 7 1*88 | 2` and then R3 sweeps `4*k 7 1*(90-k)`, i.e.
    K(1,1,2,0^88;0;0).
  - The list length is 8X + 26 (follower counts 70 / 94 / 118 for X = 5 / 8 / 11).
  - So after each full cycle the next cycle runs on a list whose length is the accumulator: an **infinite
    rebuilder**. The omega-level rises by at least one per cycle.

### 3.3 Follower results for all 18 classes (`bb9_c7m12_tail/fol/`, summaries by `summ.py`)
- **Pass 1, small accumulators**: X = 5, 8, 11, blockers above 40 shrunk mod 12. 400 events per class, except
  0RA (stopped at event 63) and 0LB (stopped at event 259). Both stopped loudly: a configuration with no
  blocker, a bare `D4 | acc` or `D7 | a | acc` after a WHOLE event. The parser does not guess.
  Logs: `fol/b_<I1>.log`.
- **Pass 2, real regime**: X = 29, 32, 35, larger than every shrunk fixed token (<= 23), threshold 70, 80 events
  per class. Logs: `fol/g_<I1>.log`.
- Single-X exploratory runs (X = 2; b = 0 is degenerate at rebuilds, so only H0 screening): `fol/<I1>.log`.

| I1 class rep (members) | HALT (H0) in any run | ACCDEP rebuilds with slope >= 2 tokens per unit X (pass 1 / pass 2) |
|---|---|---|
| 0RE (0RF, 1LG) | no | none (only +1-token jitter) |
| 0RB (1LD, 1LI) | no | 3 (slope 4) / none |
| 1RB (0LC) | no | none |
| 0RC (1RD, 1RI) | no | none |
| 0LB (1RC) | no | 2 (slope 4) / none |
| 1RG (0LI) | no | none |
| 0RD (0RI) | no | none |
| 0LA | no | 3 (slopes 8, 4, 2) / none |
| 0RA | no | 2 (slope 3) / 1 (slope 2); Q-event rebuild of 2X+4 zeros (3.2) |
| 1LA | no | none |
| 1RA | no | 4 (slopes 4, 4, 7.8, 3.7) / 1 (slope 2) |
| 1LB | no | 2 (slopes 4, 8) / none |
| 1LC | no | 2 (slopes 8, 2.5) / 2 (slopes 8, 4) |
| 0LD | no | 2 (slope 8) / none |
| 1LE | no | 3 (slopes 32, 16, 16) / 1 (slope 16) |
| 1LF | no | (one shape-change artefact) / none |
| 1RF | no | 4 (slopes 8, 2.5, 4, 4) / 3 (slopes 8, 4, 8.3) |
| 0RG | no | 1 (slope 8) / 1 (slope 4) |

Reading the table:
- **Halts:** none in 8,162 follower events × 3 accumulators. The only halting slot of these machines is H0,
  i.e. G0 with a 0 to the right (a G0 over `0 0`). It never occurred.
- **The slope >= 2 rebuilds** are all of the same kind. At a WHOLE exhaustion (walk off the left end with blank
  to the left, I0 = 0RF) or at the Q token, a list of length 4X-32X is built and then consumed by R1-R3. Those are
  the cleared lists that grow with the accumulator ("zeros=" of the following jump: e.g. 0LA zeros=67 after the
  `4*65` list).
- So these completions behave as **infinite rebuilders**: each cycle clears a list of accumulator length, so the
  omega-level rises by one per cycle, and nothing stops the cycles.
- The classes without slope >= 2 entries had not yet reached such a rebuild within the event budget, or stayed in
  the second-level-counter phase (pass 2 is short).

## 4. Verdict
1. **The (10)^Y sublist is not a list.** It is the accumulator of a zero-digit champion list formed from the last
   group's `D4 D2 D2 + d + a` (Y = 6 b_f + 3, b_f = 2^(2b+3) - 2). In g and h it is never consumed: the borrow
   walks onto the fresh `11` prefix, which is the champion's end-of-list move, and then E0 -> I, and **I1
   (undefined) halts**. The list exhausted there has length 0, not an accumulator-dependent length.
2. **g, h: omega-level 0**, score about 17.1*(2^^13 3), unchanged from the c7m12 report. No 9-state completions
   exist: all 17 other slots are used.
3. **The only 9-state completion family is #3 + I1** (36 machines, H0 = halt):
   - 7 halt immediately with g's score;
   - 1 cycler (I1 = 1RE);
   - 28 continue.
   In all 28, the (10)^Y becomes a single digit value (unary/argument use, never a list length). Afterwards the
   groups are a unary conveyor, and full cycles rebuild accumulator-length champion lists. Within all proxies
   **none reads H0**, so none is a halting record candidate. They are probably non-halting infinite rebuilders.
   **No record, no candidate.** Nothing here comes near omega-level 2 for a halting 9-state machine.
4. For the BB(10) side: the 28 continuing completions are new looper bases of the
   "accumulator-length rebuild every cycle" type. A 10th state used as a selector or counter could in principle
   turn one into a halter; that is outside this task. The strongest rebuilders by slope are
   - `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_---0RE_0RF1LE` (lists of 16X-32X)
   - `..._---0RE_0RF1RF`
   - `..._---0RE_0RF1LC`
   - `..._---0RE_0RF0LA`
   - `..._---0RE_0RF0LD`
   - `..._---0RE_0RF0RA`, which also has the Q-event rebuild
   These are leads for the halting-looper search, not records.

## 5. Literal checks run
- g / h from the real end configuration, X = 2, 5, 8: halts at I1 (steps and ones in section 1). Token traces
  (tr9 dshape) for X = 2 and 5, read off snapshot by snapshot.
- `nxt.py` rebuild of the end configuration reproduces the tr9run3 halt exactly (26571 steps, 448 ones).
- Transition-usage counts for g, h, #3, #5 and #9:
  - end-configuration run;
  - 4e8 steps from the blank tape.
- `renum.exe` (halt_redirect, run unmodified) on #3 from the three end configurations, budget 2e8.
- First post-event snapshots for all 29 non-halting completions at X = 2, 5, 8: same token list across X except
  one token of value Y + c.
- I1 = 0RA Q-event, literal:
  - Q = 155 with X = 5, 8, 14: Q - (X+1), and a list of 2X+4 zeros;
  - Q = 18 with X = 14, 20, 26: saturation at 2Q+7.
- I1 = 0LA WHOLE rebuild, literal, from `2 | X = 8`: K(1,1,2,0^88;0;0), then R3 sweeps.
- Follower passes 1 and 2 (section 3.3): 8,162 events, each run literally for 3 accumulators, at most 1e8
  steps per run, at most 3 tracer processes at Idle priority.

Not done:
- the follower is a proxy (jumps use the champion rules on 3d+1 digits; accumulators and big blockers are small);
- no event was checked with astronomically large values;
- no Coq.
Nothing under `halt_redirect/` or `proofs/` was modified.
