# Route 1: the far run as the outer counter d. REPORT (Opus investigator, 2026-10-10)

## Verdict: STRUCTURAL NEGATIVE at 12 states (screening level); no hits
No machine found eats the round-1 far D2 run more than once. Every eater or restarter found takes a FIXED number
delta of D2s once (or the whole run in one pass). After that the far run is never read again. So rounds-to-halt never
scale with k1, and no f_(omega+2) candidate came out of this route.

The reason is geometric:
1. Every round builds its OWN D2 run (Per 2^k, +4 per period, so about 2c/7, accumulator-sized). It sits at the left
   end of the round's word, i.e. RIGHT of any older far region.
2. Every round-end class except one reads J0 at or to the right of that new run (or of its tail). The old far is then
   behind an accumulator-sized run plus deposits.
3. The one exception is class 12 (counter c = 12 mod 14). Its end walks left over its own run and reads J0 exactly at
   the OLD far's tail idx 22, the same site as n1's round-1 end. This is robust in K, c, std and big.
   - But every restarter that reaches class 12 leaves a prefix between the new word and the old far.
   - The prefix either shields the old far, or it is a digit that the class-12 end borrows 3 from instead.

## 1. Survey (task 1): D2s eaten per round
Method: farfol.py, start far_k + [0 1^n | 1 | R]. At each round start I record kD2 (the leading D2 count of the far
string), the prefix P and the counter c. Raw rows are in t1tab.txt. Real classes used: k = 29, 71 (29 mod 42) and
n = 29, 71.

| machine | D2s eaten (std, k = 7..71) | round-start classes | far re-read later? |
|---|---|---|---|
| L12 | whole run (k -> 0), then leftward unpack | 9, 9, 9, ... (c = 79) | no far left |
| D1 / H14 eater | whole run in round 1 (true order, h14verify: 7 + 5, then a one-stage whole-run conversion); not in place | 10 | no (H14 halts N1, D1 loops) |
| C13a 1LK eater | std: whole run; true order: inert debris (h14verify) | 1 (std) / 9 (true) | no |
| T12a | 7, once (far -> D2^(k-7) + 22-bit tail) | 5, then HALT L1 | no |
| H13c / F12 | 12, once | 8 -> HALT (F12: 8, 4, 7, 4, ...) | no; kD2 constant over 4 restarts |
| Q12a | 6, once | 9, 9, 9, 9 | no; the tail grows +79 bits per round |
| P11 | 14, once | 7, 13 | no (borrows a prefix digit instead) |

- delta is k-independent wherever k >= delta.
- Small k (k < delta): H13c/F12 at k = 7 switch to a class-12 round, and P11 at k = 7 / 11 changes path. Nothing
  scales with k.
- Big policy: same first-restart counters (H13c 3382, Q12a 5077, P11 5075). Later stages hit the 2e8-step cap.

**Survey of all restarters in the existing trees (survey.py -> survey.tsv).**
- Scope: every RS leaf of inplace ie2_1RK / ie2_0RK and all t12scan trees (J0 = 0RK / 1RK, 12 states), 2373
  machines, followed for 6 round starts from far_29 + [0 1^29 | 1 | 19].
- 2174 machines have 2 or more round starts. kD2 decreases at MOST ONCE in every one of them (2118 never, 56 once).
- The J0 = 0LK / 1LK restarter trees (tier1, d13) were not re-surveyed. Their known families are all whole-run
  eaters, as the table shows.

## 2. Where each round end reads J0 (j0site.py, j0big.py, dumpj0.py)
Setup: n1 with J0 undefined, started from an old far region plus a fresh round, far_K + [2 5 1^c 0^3 9 1^z | 1 | R].

| class (c mod 14) | J0 read site |
|---|---|
| 9 | the NEW round's own tail, idx 22 |
| 4, 6, 11 | the right end of the NEW D2 run (moves +20 cells per period) |
| 1, 2, 5, 7 | thousands of cells to the right |
| **12** | **the OLD far tail, idx 22 (abs 5K + 22)** |

- Class 12 holds for K = 5, 20, 29, 37 and c = 26, 40, 82, 124, in std. It also holds under big (R = 2539) for
  c = 40 at K = 29 and 71.
- Left context at the class-12 read: D2^K + tail[0:22]. The right side differs from round 1 at offset +2 ('0001111..'
  vs '0010111..').
- Prefixes 1, 2, 3 and 9 keep the class-12 site at idx 22. Prefixes 7 and '3 1' move it to idx 42.
- A real restarter's prefix ('2 1 6 6 36 2 0 7') moves the site into the new word.
- A prefix digit d >= 3 is BORROWED by the class-12 end (d -> d-3); see section 4.

## 3. Gadget enumeration at the class-12 end (task 3; enum12.py)
Start: far_29 + [2 5 1^40 0^3 9 1^29 | 1 | 19], run with n1 to the J0 read at the old tail. From there, a lazy TNF
enumeration of J0 + 2 new states (12 states).

Leaf types:
- EAT = a round start with kD2 < K. These are followed through further round starts in any class.
- KEEP = a round start with the far unchanged.
- NOEAT = no change inside the D2 run within 15 stages.
- JUNK = n1's growing-far junk cycle (tokens '1 3 1^2 0 1^2 ..'). It reads base slots only and never restarts; this
  held in 30 of 30 samples.

| subtree | coverage | result |
|---|---|---|
| J0 = 0LA..0LJ, 1LA..1LJ, 0RA.., 1RA.. (into base states) | complete | no round start with an eat |
| J0 = 0LK | partial, 17k nodes (K0 up to 0RC..), file e12_ns2.tsv | 3 EAT, 6 NOEND |
| J0 = 1LK | partial, 22.5k nodes (K0 = 0LA..0LL..), file old_e12_1LK_partial.tsv | 15 EAT, 4 NOEND |
| J0 = 0RK, 1RK | not run (CPU starvation, see below) | none |

Every EAT / NOEND machine was re-followed at K = 29, 71 and 113 (chk_eat.py). All of them eat a CONSTANT delta
(2..27) ONCE and then:
- loop in class 12 or class 4 with kD2 constant over 6 rounds, or
- fall into junk, or
- (one machine, 0LK0LC_0LL1RI_0RL0RK) eat the whole run.

Example looper (12 states, never halts): ..._1LK0LC_0LL0RA_1LL0LI. It rebuilds the prefix '2^2 0^2 25 2 0 7' every
round. Each class-12 end borrows 7 -> 4 and the gadget restores 7. The far tail grows +190 bits per round. So the
prefix digit 7 is the buffer, and the far run is never reached again.

Compute note: the governor-shared CPU dropped my rate from about 45 to about 1 node/s. The remaining subtrees were
stopped. queue5.sh resumes them in the order 1LK, 0LK, 0RK, 1RK; it restarts each subtree from scratch.

## 4. Side lever found: the class-12 (and class-2/11) end BORROWS from a prefix digit (overlaps route 2)
- From [D 2 5 1^c 0^3 9 1^z | 1 | 19], the class-12 end takes D -> D-3 and then reads J0. Checked for D = 30..3000 in
  std, and in big for D = 100 and 3000.
- btable.py, at D = 100, the digit survives as D-d at the J0 stage for:

  | c mod 42 | class | borrow |
  |---|---|---|
  | 25 | 11 | 9 |
  | 26, 40 | 12 | 3 |
  | 30, 44 | 2 | 3 |
  | 38 | 10 | 3 (messy) |

- At the J0 read the digit is walk-marked: '0 11111' per 3 units for c = 40, '100000' blocks for c = 26. The J0
  context does not depend on D.
- enumD.py (12 states, J0 free; target = a restart that keeps D-d in the prefix and repeats):

  | start c | nodes | outcome |
  |---|---|---|
  | 40 | 91,820, complete | 1 DDEC1, class 8 |
  | 26 | 253,100, complete | 0 DDEC |
  | 30 | 109k, partial | 452 DDEC1: restarts that keep 97 somewhere in the prefix; never the nearest digit, and the round classes differ |

  Here DDEC1 means one restart whose prefix still contains D-d, with d <= 12.
- I then found w2_search/borrow/ (inv-w2-borrow), which owns exactly this route. Its class-12 ns = 2 run (366k nodes)
  is negative, with the same mark-unrolling observation. I stopped my digit runs to avoid duplicating it. My enumD
  files (eD40_ns2.tsv, eD26_ns2.tsv, eD_ns2 partials) are available to them.

## 5. Scaling criterion (task 2)
No machine has a per-round eat, so rounds-to-halt is k-independent everywhere it is defined:
- T12a halts at stage 26, H13c at stage 16, and Q12a / F12 loop identically for k = 11..71, n = 29 / 71.
- The only k-dependence is the small-k boundary k < delta.

Not done: the n-sweep (323 / 2129) and U-variation for candidates, because there was no candidate to test.

## Why route 1 is closed at 12 states, and what a 13-14 state version would need
- A far-run counter needs a class-12 in-place restart whose prefix is TRANSPARENT (only 1, 2, 3 or 9 tokens, and no
  digit >= 3 adjacent: that digit would be borrowed instead).
- It also needs a gadget that deletes one D2 and restores the tail pattern exactly.
- Every class-12 restarter found builds a junk prefix ending in a digit (7, 25, 36, ...). That digit is what the next
  class-12 end consumes, and the gadget refills it.
- The far tail itself is never shifted. Removing 5 cells from the right end of D2^K while keeping
  tail[0:22] = 1011010101010101001000 adjacent is a shift-by-5 operation. No 2-state gadget does it.
- A 13-14-state version (3-4 new states) is not excluded. The cheapest variant is probably to eat at the LEFT
  (blank) end of the D2 run, with a walker that crosses tail[0:22]. That needs a skip-the-tail state, a walker, a
  deleter and a return path: at least 4 states on top of the restart states, so about 15 or more states.

## Files (all in farcount/)
Tools:
- fgstage.cpp / .exe: igstage plus a gadget-read list with positions.
- fl.py: ilib copy that uses fgstage.
- farfol.py: kD2 at each restart.
- survey.py: survey of tree leaves.
- gread.py, g12.py, ttrace.py: stage traces with absolute gadget reads.
- j0site.py, j0big.py, dumpj0.py, dctx.py: locating the J0 read site.
- prefscan.py, btable.py: the borrow table.
- enum12.py: far-route enumerator.
- enumD.py: digit-route enumerator (enumD_v1.py is the class-locked version).
- chk_eat.py: K-dependence check.
- queue5.sh: resumable far-route queue.

Data:
- survey.tsv, t1tab.txt
- e12_ns2.tsv, old_e12_1LK_partial.tsv, old_e12_ns2_a.tsv
- eD40_ns2.tsv, eD26_ns2.tsv, old_eD_*.tsv
- NOTES.md, pids.txt

Nothing of mine is running.

## Suggested next step
- Drop route 1 at 12-13 states.
- If the far run is pursued at all, do it as a deliberate 14-15-state design: a class-12 in-place restart with an
  empty prefix plus a left-end D2 deleter, verified with the class-12 site facts above. Its first test should be
  K = 5 / 20 / 37 to show kD2 dropping by delta every round.
- Otherwise, fold the class-12 / class-2 borrow table (section 4) into inv-w2-borrow's route, which is the same
  "object the machine already reads" idea with a native decrement.
