# Route 2: the prefix digit as outer counter d, with a class-invariant borrow (inv-w2-borrow, Opus, 2026-10-10)

## Verdict
**NEGATIVE at 12-13 states (screening), with a correction to the premise.**

1. **P11's borrow is a small-k artefact.** The base n1 borrows a prefix digit at a class-7 round end only when the
   round's own D2 run is short (k in {9, 17}).
   - The real P11 round 2 has c = 2R-3 = 35 mod 5040, so k = 9 mod 1440 (k = 1449 for U = 2539).
   - At that k the class-7 end goes into n1's growing-far junk cycle. d and the 2^1414 run stay untouched through
     160 stages (big policy, d = 31, 1399, 1501, 3001).
   - The earlier 'big 2539 -> 2536' came from a counter-TRIMMED big run (ctrim keeps c mod 42, so k = 9).
   - Robust in the crafted true-k end over d = 31..3001 and start depths z = 37..1037 (end depths about 20k).
   - An untrimmed P11 big run reproduces round 2's start (P=[2539], c = 5075). It was stopped at stage about 150 of
     about 2200: the stage cost grows with the depth list.
2. **At true k the only borrowing end that reaches J0 is class 12** with k = 9 mod 12 (big-checked at k = 1449). It
   leaves exactly n1's halt shape '[d-3] 0 1^w | U'. But J0 is read LEFT of the digit (at the old far end, farcount's
   site), after the left walk has unrolled d-3 into (111110)^((d-4)/3) marks.
   - Class 2 also borrows at true k, but then leaves a (2k-2) digit and runs into junk with no J0.
3. **Gadget side: every in-place J0 restart is a copy.** The new counter is built from U by a copy loop that leaves
   a fresh accumulator-derived digit (U, U-1, 2R+3, 2R+4, ...) nearest the new round, so a later borrow could only
   take that fresh digit.
   - In exhaustive ns <= 2 enumerations (12 states) on the class-7, class-12 and class-2 borrow tapes, and in
     three capped ns = 3 slices (13 states: J0 = 1RK on class 7; J0 = 1RK and 0LK on class 12), NO gadget keeps the borrowed digit as the nearest digit
     of the next round. This was checked by varying d.
   - In class 12 the only d-dependent outcome re-rolls the marks into the COUNTER (c = d-3), not into a digit.

So a borrow-type outer counter would need three things, all missing:
- a class-12 counter with k = 9 mod 12;
- a restart that re-rolls the marks into a digit and MOVES U into the counter;
- a round-1 copy that creates d.

## Task 1: P11 dissection
P11 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1RC--- (J0 = 1RK, K = 1RC---, K1 never read).

- **Round 1 end.** J0 = 1RK and K0 = 1RC write '11' into the far tail. The base then eats the tail and part of the
  D2 run (stages 1-6) and leaves the accumulator as a run of B = '100000' blocks.
  - A copy loop (J0 and K0 once per pair of blocks) lays out the round-2 start [R] 2 5 1^(2R-3) 0^3 9 1^z.
  - So R is both the prefix digit and the source of the counter 2R-3.
  - Round 2 is class 7, and 2R-3 = 35 mod 5040 gives k = 9 mod 1440.
- **Round 2 end (class 7) at SMALL k only** (crafted c = 35, k = 9, std and big U; and the old trimmed big run). At
  the true k = 9 mod 1440 there is no borrow: see the verdict, point 1.  At small k the borrow is base behaviour:
  n1 itself (J0 = halt) does it before reaching J0.
  - Tokens 'd 2^9 5 1^5 0^2 (2U+3)' become 'd-3 8 2 5 1^3 0^3 1 4 1^2 0^3 1 (2U-3) 2 5 0^3 9 ..'.
  - The junk J = '8 2 5 1^3 0^3 1 4 1^2 0^6' is the same constant junk for every d >= 2, in std and in big.
  - Pre-J0 tape: [d-3] J _2 (B)^X1 1 _4 (B)^X2 0 _2 | J0 | depth.  Big: X1 = 1690, X2 = 1695.
- **P11's restart after the borrow.** (B)^X1 becomes 1^(2 X1), a MOVE into cleared zeros. (B)^X2 becomes
  '0 (U-1) 2 5 1^(2U+3)', a COPY.
  - New prefix [d-3 8 2 5 1^3 0^3 1^2 5 1 0 2 1^((4U-16)/3) 0 (U-1)], counter 2U+3 (class 13).
  - Class 13 ends in n1's junk cycle.
  - Even with a class-7 counter, the next borrow would take U-1, not d-3: with this junk prefix a class-7 end
    turns 18 into 15.
- **Class table for P11** (rtab.py, prefix [19], P11's stage-7 far; std, with big for classes 7, 8 and 12):

| c mod 14 | base end | P11 restart |
|---|---|---|
| 7 (k = 9, 17 only) | BORROW d -> d-3 + junk J | [d-3 J .. 0 (U-1)], c = 2U+3 (13) |
| 7 (k >= 41, incl. true k = 1449) | n1 junk cycle, d intact | none |
| 8 | no borrow; d and the 2-run untouched, U laid out as blocks | [U], c = 2U-3 (7); old prefix kept left as debris |
| 9 | standard J0 | [U], c = 2U-3, z = 0 (std) / T (big) |
| 12 | BORROW, d unrolled into marks | junk prefix, c = 26 std / (4U+82)/3 big |
| 2 | BORROW + k- and U-sized digits | [16 24 33], c = 6 |
| 1, 4, 5, 10 | no borrow | '4 45' junk round |
| 6, 11 | no borrow | junk prefixes |
| 0, 3, 13 | n1 junk cycle | no restart |

So P11's only borrow-class cycle would be 8 -> 7 -> 8 -> 7. In it, every class-8 restart lays a FRESH digit U in
front, and the class-7 end borrows that fresh digit. That is a looper, not a counter, and at true k even the
class-7 borrow is gone.

### Base round-end table with a prefix digit (endtab.py, n1 with J0 = halt, P = [31])
- **No borrow** in r = 1, 4, 5, 6, 8, 9, 10, 11 (d intact, independent of k). r = 0, 3, 13 end in a junk cycle.
- **Borrow** in r = 2, 7, 12, depending on k. Big policy (U = 2539, k up to 1457) agrees with std wherever k < U:
  - r = 7: borrow at k = 9 and 17 (k = 9 mod 1440 confirmed by P11's real big run, 2539 -> 2536).
  - r = 12: clean borrow '[d-3] 0 1^w | U' iff k = 9 mod 12 (21, 33, 45, 1449, big-confirmed).
    - k = 5 mod 12 adds the digits '(2k+12) (2U+3)'.
    - k = 1 mod 12 gives junk.
    - The clean shape is exactly n1's halting shape FarE + [0 1^w | f], with D(d-3) in place of FarE. But J0 is read
      LEFT of D(d-3), at the old far end (same site as farcount's class-12 site), after the left walk has rewritten
      D(d-3) as (111110)^((d-4)/3) marks.
  - r = 2: borrow, then the 2-run becomes a digit 2k-2 (big: 2888 at k = 1445) and an accumulator-sized digit
    (2U-5 at k = 13). These sit between d-3 and the J0 site.
- The borrow always takes the nearest token (crafted prefixes, class 7):
  - x >= 3: x -> x-3 plus junk J.
  - x = 1 (cleared zeros): the borrow passes, but the 1s turn into new digits.
  - x = 0 or 2: no borrow, J0 at once.

### Arithmetic of the class condition
Every jump output is U = 19 mod 2520, so a restart counter aU+b has a fixed class mod 5040.
- A post-borrow reload 2U-3 (or 2U+11) would re-enter class 7 with k = 9 mod 1440, the same as round 2.
- For class 12 a reload needs k = 9 mod 12 to borrow cleanly.

The class condition can therefore be met, at least as arithmetic. **The obstruction is the fresh nearest digit, not
the class.**

## Task 2: mining and enumeration
### Gadget-only enumeration (benum.py)
benum.py is a lazy TNF enumeration of J0 plus NS new states.
- **Start.** A saved pre-J0 word (mkstart.py), with crafted prefix d = 31 in front of P11's round-2 far region.
- **Criterion.** The first RSIG after the J0 read must keep the borrowed digit as the nearest digit, with only
  tokens < 3 after it.
- **Check.** bverify2.py re-runs each RS machine with d = 37 and d = 43 and requires the nearest digit to MOVE with
  d. A plain value check is fooled by gadget-made constants: 28 appears as a gadget constant on both the class-7 and
  the class-12 tapes.

| tape | space | nodes | RS leaves | MOVES (keeps d) |
|---|---|---|---|---|
| class 7, k = 9 (P11's) | ns <= 2, all J0 (12 st) | 341,280 leaves | 7,368 (7,048 machines) | **0** |
| class 12, k = 21 (clean) | ns <= 2, all J0 | 366,285 | 2,989 (2,804) | 70 moving, **none keeps d** (see below) |
| class 2, k = 13 | ns <= 2, all J0 | 349,197 | 3,518 (3,246) | **0** |
| class 7, k = 9 | ns = 3, J0 = 1RK, K0 = 0LA..0LK only (13 st, capped) | 300,189 | 6,751 (6,483) | **0** |
| class 12, k = 21 | ns = 3, J0 = 1RK, K0 = 0LA..0LK (13 st, capped) | 250,113 | 1,865 (1,762) | 46 moving, none keeps d |
| class 12, k = 21 | ns = 3, J0 = 0LK, K0 = 0LA..0LC (13 st, capped) | 250,161 | 3,263 (3,219) | 14 moving, none keeps d |

- Class-12 'MOVES' are the wrong kind. In 56 of them the gadget re-rolls the marks into the COUNTER:
  - c = d-3 and P = [x], with x = 2U - (d-3)/2 (0RL1RF_0RK0LJ family).
  - The counter is then built from d, not from U, and a fresh U-derived digit is still nearest.
  - The other 14 change prefix structure between d values (irregular).
- In-place restart prefixes seen across all trees have an accumulator-derived nearest digit: P11 [R] / [.. U-1],
  T12a [3, 2R+4], H13c [.. 2R+3], Q12a [3 1 0 R], and here 40/41/42/45 = 2U+2.. digits.

### Mining existing trees
bscan.py follows each machine for up to 150-300 stages from far_29 + [0 1^323|1|19]. It records full prefixes and
flags a prefix digit >= 10 that is decremented by 3 between consecutive rounds.
- **mine1**: 1,562 machines (inplace ienum RS/NOEND leaves with restarts: J0 = 1RK / 0RK ns 1-2).
- **mine2**: 1,172 machines (t12scan RS leaves with a prefix, d13/tier1 RESTART leaves with >= 2 prefixed restarts).
- **Result: 0 machines with two consecutive borrows of the same accumulator-sized digit.**
  - The 89 single borrow events (46 in mine1, 43 in mine2) are almost all the P11 family: round 2 c = 35 (class 7)
    borrows 19 -> 16, then c = 41 (class 13) junk. These are std-only, small-k events, and at true k they vanish.
  - The rest are c = 6..48 cyclers that rebuild the same prefix digit (e.g. ..._0RK1RL_0LI1RK: 20 -> 17 -> 20 ...).
- Earlier data recorded only P lengths (P{n}), so full-prefix re-following was needed.

## Task 3: scaling
No machine reached the scaling stage. No screen ever showed even two consecutive borrows of the same digit with
accumulator-sized rounds.

## Task 4: structural negative and minimum extra cost
A d-counter by borrowing needs the same digit to be the nearest borrowable token at every borrowing round end.

1. **Base, true sizes.** Of the borrowing classes, class 7 borrows only for k <= 17, and class 2 runs into junk
   after its borrow.
   - Class 12 (k = 9 mod 12) is the only clean borrowing end at true k, and it unrolls d-3 into marks before J0.
   - At small k, class 7 and class 2 leave constant junk with digits 8, 5, 4 (class 7) and a k-digit plus a U-digit
     (class 2) between d-3 and the J0 site.
2. **Gadget.** In place, the counter is made from U by a copy loop over block runs.
   - The base end event outputs two accumulator-sized tokens (class 7: 2U-3 and 2U+5; class 8: 2U+2 and 2U+5).
   - In every restart seen, one token becomes the counter and the other remains a digit, or both are copied.
3. So the round after a borrow always presents a fresh U-sized digit nearer than d-3. In class 12 the old digit is
   not even a token any more.

**Arithmetic.** The class condition itself is satisfiable. U = 19 mod 2520 fixes aU+b mod 5040; for example 2U+b
with b = 2 mod 14 gives class 12, and k = 9 mod 12 is a further congruence on aU+b. So the obstruction is mechanical,
not residual.

Minimum extra machinery on top of the base, as an estimate (not built). A class-12 version needs:
- (a) a J0 gadget that re-rolls the (111110)^m marks back into a digit d-3 (the 0RL1RF_0RK0LJ family shows a
  12-state gadget can re-roll marks, but only into the counter);
- (b) a counter built from U by a MOVE (no leftover U-digit), landing in class 12 with k = 9 mod 12;
- (c) a left-context test so that round 1 (FarE context) creates d by a copy instead. At the J0 site the round-1
  tape and the class-12 tape first differ 8 cells right of the site.
- The halt slot would sit on the d < 3 exhaustion path. d = R1 = 1 mod 3, so the last borrow leaves a cleared
  zero and the walk reaches round-1 debris.

At 1-2 states each, that is roughly **13-16 states**: base 10 + J0 gadget 1 + (a, b) 2-3 + (c) 1-2.  BB(14)-BB(16)
champions are only f_(omega+1), so this would still be a record, but nothing here suggests the pieces exist.
- Exhaustive ns = 2 (12 states) on the class-12 tape: no gadget does (a).
- The capped 13-state slices (J0 = 1RK and J0 = 0LK) on the class-12 tape find none either.

## Coverage and caveats
- All benum starts are crafted and std (U = 19). d = 31 (37/43 for verification) sits on P11's round-2 far region,
  with k = 9 / 21 / 13 for classes 7 / 12 / 2, z ~ 146-249.
  - Std matches big for the class tables at k <= 45. True k was big-checked for classes 7, 12 and 2: only class 12
    survives.
  - The gadget's first restart was not big-checked: nothing passed std.
- benum leaves 'MAX' (no RSIG within 6 stages, or 14 for the J0 = 0LK part of class 7) are not followed further. A
  gadget that restarts later than 6 stages after J0 is not covered.
- 433 class-7 RS machines read an undefined slot on the d = 37/43 tapes. They were not branched (gap).
- ns = 3 is covered only by capped slices:
  - class 7, J0 = 1RK, K0 in 0LA..0LK (not representative at true k);
  - class 12, J0 = 1RK, K0 in 0LA..0LK;
  - class 12, J0 = 0LK, K0 in 0LA..0LC.
  The rest of the 13-state space (other K0, J0 in {0RK, 1LK}) was not run.
- The two-round periodic option (a borrow round followed by a non-borrow round) was screened only through the first
  RSIG after the borrow. A non-borrowing round that later cleans the prefix was not tested; no restart seen cleans
  anything.

## Tools (borrow/)
- rtab.py: round-start class table (next RSIG per c, any prefix).
- rtrace.py / fromword.py: per-stage traces with gadget slot reads.
- endtab.py: base round-end table with the k replacement; pre-J0 word in loose form.
- mkstart.py: save a pre-J0 word.
- j0at.py / j0lit.py: the literal J0 site.
- loose.py / prle.py: a loose token view of debris and a periodic RLE.
- jview.py: loose views at chosen stages.
- benum.py: gadget-only lazy enumeration.
- bfilter.py / bfilter2.py / bverify.py / bverify2.py: the d-keeping filters and d-variation checks.
- bscan.py + mpost.py: multi-round prefix-borrow mining.
- queue.sh: the single-process job queue.
- Data:
  - be_*.tsv (trees), bverify2_*.txt, endtab_std.txt, endtab_big12.txt, endtab_big2.txt, endtab_big7.txt,
    jv_big_c35/36.txt;
  - mine1.tsv, mine2.tsv.

## Suggested next step
Do not spend more 12-13 state compute on route 2.  If the route is pursued at 14-16 states:
- (i) first look for a pure MOVE restart: a gadget that from the class-8 or class-7 pre-J0 tape builds a counter from
  ONE block run and dissolves the other into cleared zeros, with no new digit. Use benum with a 'no digit >= 3 left
  of the counter except d-3' filter.
- (ii) only then add the left cleaner and the round-1 copy test.

The cheaper Tier-2 lead remains the farcount route. Class 12 is the only end whose J0 site sits on the old far
region, and the clean class-12 shape needs k = 9 mod 12; that is useful to farcount.

## Addendum (2026-10-11): farcount coverage and the handed-over class-12 looper
- **farcount's class-12 borrow scans** (farcount/NOTES.md, section "PREFIX-DIGIT BORROW"; enumD.py, D = 100, std, no
  far region, ns = 2, J0 free):

  | start | coverage | result |
  |---|---|---|
  | c = 40 | 91,820 nodes, complete | 1 DDEC1 (class 8, writes left), 0 class-12 cycles |
  | c = 26 | 253,100 nodes, complete | 0 DDEC |
  | c = 30 (class 2) | 109k nodes, partial | 452 restarts that keep 97 somewhere in the prefix, never nearest |
  | c mod 42 = 44, 25, 38 | not run | — |

  - btable.py: the digit survives as D-d at J0 for c mod 42 in {25 (class 11, d = 9), 26, 40 (class 12), 30, 44
    (class 2), 38 (class 10)}. This is consistent with my base table, which is indexed by k instead of c mod 42.
  - Together with my class-12 k = 21 tree (366k nodes) and the two class-12 13-state slices, there is still no
    class-12 cycle that keeps the borrowed digit.
- **The farcount looper** L12f = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1LK0LC_0LL0RA_1LL0LI
  (12 states, never halts):
  - It is a clean in-place class-12 accumulator reloader: big gives P = [2^2 0^2 (2U-13) 2 0 7], c = (4U+82)/3.
  - Each class-12 end borrows the nearest digit 7 -> 4.
  - The "refill" is a FULL REBUILD of a constant prefix. I crafted the last digit X = 7, 13, 22 and 31 (std), and
    X = 7 or 31, or the 25 replaced by 2539 (big). In every case the next round has the identical prefix
    '2^2 0^2 (2U-13) 2 0 7'.
  - The far region grows by exactly 2(X-7) bits, so the whole old prefix is pushed into the far debris. That
    includes the borrowed X-3 and the previous round's U-digit, and none of it is read again.
  - So:
    - (i) there is no "refill less" knob, because the 7 is a gadget constant and not a +3;
    - (ii) the decrement cannot be carried onto the accumulator-sized digit, because 2U-13 is rebuilt from each new
      U and the old one is dumped.
  - L12f belongs with Q12a and L12 (identical rounds), not with counters.
  - A Tier-2 use would need the class-12 end to reach an OLD deposit in the far debris, which is a far-region walker
    (farcount's route-1 obstruction).
- **Priority bug.** The copied ilib.py's SetPriorityClass call passes the 64-bit pseudo-handle without argtypes and
  fails silently. The python processes stayed at Normal; only the igstage children were Idle, via creationflags.
  - Fixed in borrow/ with idle.py, imported by every script and verified Idle.
  - The same bug is in the other ilib copies (inplace/, t12scan/, farcount/, ...).
