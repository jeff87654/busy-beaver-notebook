# C13/C14: exact local word dynamics, still no blank-tape classification

C14 is

```
1RB1LA_0LA0RC_1RA1LD_0LE1RZ_0LC1LF_1RH1LG_1LA0LE_0RE0RH
```

C13 has the same blank-tape outcome by the previously proved G1 time-change
equivalence in `unresolved_family_equivalence.md`. This note derives exact
word transformations for C14. They support a smaller word-rewriting model,
but do not yet prove halting or nonhalting from blank.

## Rightward sweep and its boundary

For every r>=1, H scanning the first symbol of `01^r` transforms it into
`10^r` and ends as H on the cell immediately after this block, in r+3 steps.
The transition sequence is H0 E1 F0 H1 followed by r-1 further H1 steps.
An H head on a one simply clears it and moves right in one step.

H scanning the first zero of `000` takes
H0 E0 C0 A0 B0 A1 A1. It writes `110` and ends as A immediately to the left
of that word, in seven steps. The third zero is read and preserved.

These rules explain the role of run lengths: a rightward pass converts
blocks of ones into gaps between isolated ones. The following leftward
phase uses those gap lengths to determine its next carry operation.

## A's first carry

Place A's head at coordinate zero, scanning a zero, and suppose positions
1 through n contain ones, n>=2. After A0 B1 C1 D0 E1, F is at -1; the tape
has a one at 0, a zero at 1, and the remaining n-1 ones at 2 through n.
There are three exact continuations:

| Initial cells to A's left | Outcome | Total steps |
| --- | --- | --- |
| cell -1 is 0 | Ones at -1 and 1, zeros at 0 and 2..n; H at n+1 | n+9 |
| cells (-2,-1) are 01 | New word `1110 1^(n-1)` starts at -2; A at -3 | 7 |
| cells (-2,-1) are 11 | New word `0110 1^(n-1)` starts at -2; E at -3 | 7 |

The first row uses F0 H1 followed by the H run rule above. The second and
third use F1 G0 or F1 G1. No unspecified cell is read. If the final A head
sees an additional left run of ones, ordinary A1 steps merge that run with
the newly created three-one run.

There is a different, useful carry when the leading right run has length
one. For r>=1, with A initially scanning the first zero,

```
A> 0 1 0 1^r V  ->  1 A> 0 1^(r+1) V     in 5 steps.
```

The trace is A0 B1 C0 A1 A1. Thus a one-run is consumed and increments the
following run length. This arithmetic effect explains why bounds such as
"all runs have length at most four" are not automatically invariant.

## E's leftward carry

In this table E initially scans the final cell of the displayed word.

| Initial word | Output word | Final position/state | Steps |
| --- | --- | --- | --- |
| `01` | `10` | H immediately right of the pair | 3 |
| `011` | `111` | A immediately left of the triple | 3 |
| `111` | `011` | E immediately left of the triple | 3 |
| `010` | `010` | E immediately left of the triple | 3 |
| `110` | unchanged until halt | halt | 3 |

The traces are E1 F0 H1; E1 F1 G0; E1 F1 G1; E0 C1 D0;
and E0 C1 D1, respectively. In particular, repeated triple-one carries are
an exact parametric sweep, rather than an inference from a long run.

When E scans the central zero in `000`, E0 C0 A0 B0 A1 A1 writes ones on
the initial head cell and its left neighbor, preserves the right zero,
and ends as A two cells left of its initial head. This takes six steps.
The E0=1 variant C16 uses four steps to reach the same result.

## A complete rightward pass as a word identity

Let A scan coordinate zero, with cell -1 blank. Let its right-hand word be

```
R = 1^n (0 1^r1) ... (0 1^rk) 01,
```

where n>=2 and each ri>=1, followed by at least three blank cells. Let U
denote the arbitrary unchanged tape through coordinate -2. The A entry,
H sweep, and terminal reset give exactly

```
U 0 A> 0 R 000...
   -> U 101 0^(n-1) 1 (0^r1 1) ... (0^rk 1) A> 0 11 0...
```

The final A head scans the cell formerly containing R's final one. The
time is n+20+sum(ri)+3k. For C16 it is two steps shorter. All of U and every
cell beyond the three specified trailing zeros remain untouched. This
identity follows by concatenating the already proved local traces; the
parameterized run lengths are handled by H1 iterations.

## Three complete boundary families

Write a finite run list [a,b,...,1] for A on the blank immediately left of
`1^a 0 1^b ... 01`, with blank tape elsewhere. Here `2^k` in a run list
means k repeated entries equal to two. For every k>=0:

| Initial run list | Next A left-boundary run list | C14 steps | Head displacement |
| --- | --- | --- | --- |
| [2,2^k,1] | [3,3,2^k,1] | 37+12k | -3 |
| [3,2^k,1] | [4,2^(k+1),1] | 38+12k | -2 |
| [4,2^k,1] | [3,4,2^(k+1),1] | 77+24k | -3 |

The full rightward pass costs n+20+5k. Each trailing two-gap then takes
one seven-step A carry and contributes a two-run to the output.

For n=3, the final carry lands on the remaining isolated left one. One A1
step merges it into a four-run. The post-pass cost is 15+7k, giving
38+12k in total. For n=2, the analogous landing first merges a four-run,
then one more seven-step carry reduces it to a three-run behind a new
three-run. The post-pass cost is again 15+7k, giving 37+12k.

For n=4, the first pass and k+1 carries take 31+12k steps. They leave A
with the right word [3,2^k,1] and a zero on its left. A second pass costs
23+5k, then k+2 carries cost 14+7k. Two A1 steps merge the remaining double
one into a five-run; one final seven-step carry reduces this to a four-run
behind a new three-run. The resulting total is 77+24k. Every G in these
derivations reads zero. Each E0 occurs in the terminal three-zero reset.

Consequently these families also hold for C16, with the same outputs and
displacements, and respectively two, two, and four fewer steps. They explain
some initial growth but do not cover arbitrary mixed two/three tails.

## Why a larger grammar proof is still needed

Actual early left-boundary checkpoints have words made of runs 2, 3, and 4
separated by single zeros and ending in a single one. However, the broad
grammar also includes halting configurations. C14 started as A on the blank
immediately left of

```
11110110111101     (run lengths 4,2,4,1)
```

halts in 1,086 steps with 30 ones. Its first fourteen E0 events have blank
neighbors on both sides. The fifteenth E0 event, at step 1,083, has a one
on its left and then executes E0 C1 D1, the halting triple above. This
input is artificial; it has not been shown reachable from blank.

Therefore neither a long initial period satisfying the E0 neighborhood
condition nor membership in that simple run grammar proves nonhalting.
Restrictions on marker positions or carry parity need a universal proof.
The explicit local rules above provide the exact operations that such a
proof must preserve.

There is also an explicit obstruction to equating C14 and C16 on the whole
run grammar. From the artificial run list [3,2,3,1], both reach an E0 head
with leftward ending `010`. C14 leaves those three cells unchanged, while
C16 changes them to `011`. C16's first A left-boundary return is at step
827 with run list [2,2,2,4,3,3,2,2,2,2,2,2,1]. C14's first return is at
step 853 and contains a double-zero gap. These are not the same tape
configuration. `lastfive_family_theory_variant_counterexamples.json`
records the independently simulated examples and the first exceptional
E0 neighborhoods. No difference in blank-tape halting outcome is claimed.

Even the more restrictive grammar with leading run three or four and
exactly one four-run is unsafe: the parent's C16 literal check of
[3,2,3,4,1] halts after 10,910 steps. Its saved artifact is
`lastfive_grammar_exactly_one4.json`. Therefore uniqueness of a four-run
is not a sufficient invariant.

`lastfive_family_theory_macros.py` checks these formulas on finite grids,
rejecting any read outside each known interval, and replays the artificial
halting example. Its output is `lastfive_family_theory_macros.json`.
The finite checks guard against transcription mistakes; they are not the
reason the parameterized H sweeps hold universally.
