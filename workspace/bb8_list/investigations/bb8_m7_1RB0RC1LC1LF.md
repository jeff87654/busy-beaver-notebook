# m7 holdout `1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---` (H1 undefined = the halt)

Source: holdout of the m7 champion subtree, graded R4-SOME by the generalised digit-list screen.
Scratch dir: `bb8_list\investigations\bb8_m7_1RB0RC1LC1LF\`. Proof: `bb8_list\proofs\BB8_m7_1RB0RC.v`.

## Verdict

**NEVER HALTS. Confidence: proved (Coq PASS).**
`python check.py BB8_m7_1RB0RC.v` in `bb8_list\proofs` prints
`PASS BB8_m7_1RB0RC.v: 1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA--- never halts (machine-checked, no axioms)`
(`Theorem nonhalt : ~ halts tm c0.`, 8-state setup `Individual82`, about 30 s). README row added.

- **No record claim.** It is a non-halter, so there is no sigma and no rebuild count to report. It cannot approach 2^^37 3.
- The R4-SOME suspicion is resolved: R4 (list used up) halts only for b <= 1, and **b >= 2 at every exhaustion**
  (rule-level argument below). The rebuild never produces a used-up list with b <= 1.
- Total token cost of this investigation: about 310k tokens.

## Structure found (finer than the K(ds; a; b) rules)

Read the tape in three-cell blocks U = `010`, S = `100`, V = `110`. The screen's family
K(ds; a; b) (dlscan2 template L,G,P=1001,u=010,s=001, unary d, b) is, in the original orientation,

    0^inf G> 0 U^b S U^a S U^dn S ... U^d1 S S 0^inf          (the last S is followed by blanks)

with the head in G on the blank cell left of the word. The blank-tape run first enters it at step 88 as `U S U S S` = K(;1;1).

**Token-word rewriting.** For a token word w, the machine returns to G with nothing on its left after a bounded number of
passes, and the new word depends only on the prefix `U^i S^k T` (S-run maximal, T the next token). Here i, k >= 1:

| rule | word | next G-visit word | literal steps |
| --- | --- | --- | --- |
| A | `U^i S^k U r` | `U S^(i-1) U^(k-1) S V r` | 12i + 10k - 2 |
| B | `U^i S^k V r` | `U S^(i-1) U^k S r` | 12i + 10k + 2 (i >= 2), 10k + 14 (i = 1) |
| C3 (i >= 3) | `U^i S^k` (end of word) | `U^(i-2) S V^(k+1) S` | 8k + 10i - 5 |
| C2 (i = 2) | `U^2 S^k` (end) | `U^2 S V^k S` | 8k + 40 |
| C1 (i = 1) | `U S^k` (end) | garbage tokens `111 (011)^k 01`, leads to the halt | 8k + 14 |

(A, B, C2, C3 verified literally by `absys.py` / `cr.py` for i, k <= 6-8 with several tails, and by the Coq proof for all i, k.)
`abrun.py` runs this rewriting system next to the literal machine from the blank tape and compares **all 30,000 first G-left-visits**
(they include several rebuilds): 0 mismatches. The first visit is the word `U U S V S` at step 52.

The nested counters of the screens are an *abstract* phenomenon: the literal cost of R3 is a polynomial of degree b in the
number of zero digits (symmetric in (b, j); e.g. 22, 66, 220, 924 steps), but it is a composition of A and B passes, each linear.

## Macro rules of the screens (derived from A/B/C, checked)

Unified R1/R2/R3: `U^b S^j U Z -->* U S^(j-1) U^b S Z` (b >= 1, j >= 1). In digit-list terms, with ds = d1..dn, d_n nearest a:
- R1 (a >= 1): K(ds; a; b) -> K(ds; a-1; b+1).
- R2 (a = 0, last digit y+1): K(.., y+1; 0; b) -> K(.., y; b; 1).
- R3 (a = 0, trailing zeros 0^k, k >= 1): K(.., y+1, 0^k; 0; b) -> K(.., y, **b**, 0^(k-1); 0; 1). The refilled digit b goes next to the
  non-zero digit y, the other k-1 zeros stay on the a side (the lead's description "zeros kept, writes b" is right; my first guess had the order reversed).
  No halting boundary in k: it holds for all k, b >= 1.
- R4 (a = 0, all digits zero, n >= 0 of them): halts for b = 0 and b = 1 (all n); for b >= 2 it rebuilds. With b' = max(b, 3):
  - n = 2t: K(0^n; 0; b) -> K(b'+t-1, 0^t ; 0; 1)
  - n = 2t+1: K(0^n; 0; b) -> K(t+3, 0^(b'+t-3) ; 0; 1)
  (b = 2 and b = 3 give the same list.) Literal machine: n <= 4, b <= 13 (`r4.py`); abstract system: n <= 7, b <= 8 (`macro.py`);
  rule-level R1-R3 on 949 literal configurations (`rules.py`; the 23 other cases exceeded the 3M-step cap, none mismatched) and 378 random abstract ones.
  Examples from the blank tape (literal): K(;1;1) -> K(;0;2) -> K((2);0;1) -> ... -> K((3,0);0;1) at step 4038 -> K((4,0);0;1) at 9815.

## Why it never halts (proved)

The Coq proof does not use the digit-list rules at all. It uses only A, B, C2, C3 on token words plus a trivial invariant:

    Inv w := w = U^(i+1) S^(k+1) rest, rest empty or starting with U or V (so the S-run is maximal),
             and rest = [] -> i >= 1 (at least two leading U's when the word ends after the S-run).

Every rule output again starts with a U-run followed by an S, and it is a pure `U^x S^y` word (the only case C1 could bite) only
when produced by B with i = 1, which gives `U^(k+1) S ...`, so x >= 2. A and C outputs contain a V. Hence every word satisfying
Inv has a next step (A, B, C2 or C3), and the result satisfies Inv. The blank tape reaches `U U S V S` in 52 steps, which satisfies Inv.
`progress_nonhalt_cond` closes it. This is the token-level form of "b >= 2 at every exhaustion": the rebuild's own list always contains
a V, i.e. a non-zero digit, and R3/R2 results have b = 1 but never an all-zero list.

## Machine-level lemmas (all generated, none hand-written)

`planner8.py` (champ12 version with mode-2 crossings) derived each pass for symbolic runs `i`, `k` and a free tail `l`:
- `PA`: `0 U^(1+i) S^(1+k) U l -->+ 0 U S^i U^k S V l` (20 literal steps at i = k = 0, plus crossings `cr_DR_010_101`, `cr_AR_100_110`, `cr_BL_101_001`, `cx_FL_110_010_c1`)
- `PB`: `0 U^(1+i) S^(1+k) V l -->+ 0 U S^i U^(k+1) S l`
- `PC3`: `0 U^(3+i) S^(1+k) 0^inf -->+ 0 U^(1+i) S V^(k+2) S 0^inf`; `PC2`: `0 U U S^(1+k) 0^inf -->+ 0 U U S V^(k+1) S 0^inf`.
The rest of the file (`tok`, `tp`, `Gc`, `inv_step`, `init_reach`, `nonhalt`) is about 120 lines of list manipulation.
Pitfall met: `rewrite (align_lpow_const x xs n)` with an explicit counter fails to match; use `_` (patched in `scr2coq.py`).

## Reproduction

In `bb8_list\investigations\bb8_m7_1RB0RC1LC1LF` (python = `..\..\..\third_party\venv311\Scripts\python.exe`):
- `python gen.py ..\..\proofs\BB8_m7_1RB0RC.v` regenerates the Coq file from `head.v.in`, the planner phases (`ph3.py`, `planner8.py`, `scr2coq.py`, `phc.py`, `coqgen_util.py`) and `tail.v.in`.
- In `bb8_list\proofs`: `python build.py BB8_m7_1RB0RC.v`, then `python check.py BB8_m7_1RB0RC.v`.
- Rules/checks: `fam0.py` (K-trajectory from the blank tape), `r4.py` (R4 grid), `rules.py` (R1-R3 literal grid), `absys.py` (A, B literal), `cr.py` (C literal),
  `abrun.py 30000` (abstract vs literal, blank tape), `macro.py` (macro rules from the abstract system), `shapes.py`/`subr.py` (how A/B/C were found),
  `tr.py` (tape tracer), `gvis.py`, `cvis.py`.

## Open questions

None for this machine. For the lead: the same trick (fine-grained prefix rewriting on three-cell blocks, which turns the nested counters into
linear passes) may apply to the other R4-SOME / rebuilder machines and to the unproved champ12 rebuilders; the rule-finding script is `subr.py`
(collect (prefix -> prefix) pairs at consecutive G-left-visits, strip the common suffix, run-length encode).
