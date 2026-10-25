# Neighbourhoods of the champion-rule rebuilders (2026-10-04)

**Question.** Four 8-state machines follow the BB(7) champion's digit-list rules exactly but rebuild the list
when it is used up instead of halting. A 1- or 2-transition neighbour whose rebuild halts for *some* list
states (the BB(9) champion's mechanism: halt for odd b) would grow at Ackermann level, beyond any fixed number
of up-arrows. Does one exist?

**Answer: no.** All 2,013 radius-1 neighbours were checked, and so were all radius-2 combinations that keep the
digit rules. No neighbour mixes halting and rebuilding. No neighbour halts with a list longer than 35 digits.

| # | parent | start-up | rebuild K(0^n; 0; b) → |
|---|---|---|---|
| p0 | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RF` | 30 digits, step 4775 | 12b + n + 7 digits |
| p1 | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RH` | 30 digits, step 4775 | 12b + n + 7 digits |
| p2 | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE` | 11 digits, step 2133 | 12b + n + 4 digits |
| p3 | `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE` | 11 digits, step 2133 | 12b + n + 4 digits |

(digit counts in dlscan2's template, `K(2, 0^m; 0; 0)` with m + 1 digits; `usage_phases.txt`)

## 1. Structure: the rebuild uses no transition of its own

`usage_phases.py` records which transitions each phase uses:

- the start-up from the blank tape;
- R1–R3, on 28 constructed configurations, each run until the exact successor the rules predict;
- R4, the used-up list `K(0^n; 0; b)` for n = 0–3 and b = 0–5.

In all four parents, **R4 uses only transitions that R1–R3 also use**. The only transition no phase uses is the
undefined one (E0 for p0/p1, H0 for p2/p3), and it is never reached. The rebuild is the start-up machinery run
from a used-up list: the same transitions write the list from the blank tape.

So any neighbour that changes the rebuild also changes a transition the digit rules use. It keeps the rules only
if that transition's use in R1–R3 happens to be insensitive to the change. H1 is the example: the 35-digit
champion `…_1RG1LF` is p0 with H1 = `1RF` → `1LF`, the R1–R3 rules are identical, and H1 alone decides between
rebuilding and taking E0 to the halt.

## 2. Radius 1 (2,013 distinct neighbours, `gen_nbrs.py 1` → `r1.tsv`)

**Full dlscan2 with template inference** (`grade_timeout.py`, 30 s per machine) → `r1_graded.tsv`. Genuine
champion-type machines grade in under 1 s (`time_one.py` on the parents, the 35-digit machine and the BB(7)
champion: 0.5–0.9 s).

- **989 inside the m8 subtree** (no change to the champion's first eight transitions A0 A1 B0 C0 C1 D0 D1 E1):
  742 no fit, 123 timeouts, 122 NOBOUNDARY, 2 CHAMPION.
  - Apart from copies of a parent that differ only in its never-used slot, the fits are the 35-digit machine
    and its `1LH` sibling (CHAMPION, known) and three rebuilders (p2/p3 `G0=0RG`, p3 `H1=0RF`).
  - The timeouts need no second look: the m8 subtree was enumerated and graded exhaustively, with no timeout
    (0 R4-SOME, 0 HALT-SOME among 13,364 holdouts).
- **1,024 changing the prefix** (new territory): 936 no fit, 88 timeouts.
  - The 88 were redone with `timeout_pass2.py infer` → `r1_timeouts2.tsv`: list dlscan2's inferred templates,
    keep the 2,132 with a unit of length ≥ 2, fit each with `dlscan2 --tmpl` at N = 5,000, then refit at
    N = 100,000 only if that passes.
  - Stage 1 is a valid filter: the four parents, the 35-digit machine and the BB(7) champion all pass it with
    the exact R1–R3 parameters.
  - Result: **0 of 2,132 templates pass**. No prefix-changing neighbour has a digit-list structure.

**Fixed-template singles** (`tmpl_scan.py singles` → `singles.tsv`): every single change fitted against its
parent's own template, so no inference is needed. Besides the never-used slot, the changes that keep R1–R3
exactly are:

| change | parents | R4 | note |
|---|---|---|---|
| `H1=1RH` / `H1=1RF` | p0 / p1 | rebuild | turns one parent into the other |
| `C0=0LC` | p0–p3 | none (T) | walks left on blanks forever from step 2 |
| `F0=0LH` | p1 | none (T) | 126k-cell tape after 3M steps, never forms a list |
| `C0=1LH` / `C0=1RH` | p2 / p3 | halt | halts at step 3 from the blank tape (C0 → H → undefined H0) |
| `G0=0RD`, `G0=0RG` | p2, p3 | rebuild | |
| `H1=0RF` | p3 | rebuild | |

The 19 singles whose fixed-template fit timed out all fail stage 1 of `timeout_pass2.py fixed`
(`singles_timeouts2.tsv`), so they break the rules.

**R4 over (n, b)**: dlscan2 probes R4 only on the empty list, but in a real run the used-up list is `0^n` with n
large, and the finale loops over those zeros. `r4grid.py` therefore runs R4 for n = 0–6 and b = 0–8 on every fit
above (`r1_r4grid.txt`, plus 70 rebuilding variants in `rebuild_rest.tsv`). Every machine either halts for all
(n, b) or rebuilds for all; **nothing is mixed**.

## 3. Radius 2

A blind radius-2 sweep is 475,710 machines. About 20% of them hit dlscan2's slow template inference, which would
cost hundreds of CPU-hours. By section 1, a radius-2 neighbour keeps the rules only by combining single changes
that each keep them, so the targeted set is the **pairs of rule-preserving singles of the same parent**
(`tmpl_scan.py pairs` → `pairs.tsv`, 464 pairs including never-used-slot variants):

- 4 CHAMPION, all containing `C0=1LH`/`C0=1RH` (trivial halters from the blank tape);
- 230 rebuild (`KKKKK`), and the (n, b) grid shows no halting case;
- 228 with no R4 outcome, all containing the dead `C0=0LC`;
- 2 that break the rules.

**Not covered:** pairs in which each change alone breaks the rules but the two together restore them
(compensating changes). Section 1 makes these unlikely, since every transition is shared with the rules, but they
were not enumerated.

## 4. Related: the m7 subtree (item 2, already running)

`../champ12_subtree/m7/` (8 parts, `watch_champ.py m7 35` grading new holdouts hourly) had graded 156,060 holdouts
by 15:18. Its CHAMPION hits all start from 11 or 35 digits, and it printed no RECORD-LENGTH line. Its one R4-SOME
hit, `1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---`, is a different family:

- unit `010`, an additive R1 (`b → b+1`);
- R4 halts only at b = 1 and rebuilds for b = 2–5, and b never returns to 1 once it is ≥ 2;
- so it is very likely a non-halter.

## Reproduction (this folder; everything runs at Idle priority)

    python gen_nbrs.py 1 r1.tsv
    python grade_timeout.py r1.tsv r1_graded.tsv 4 30          # ~1.5 h on the shared PC
    python timeout_pass2.py infer r1_graded.tsv r1_timeouts2.tsv 3
    python usage_phases.py > usage_phases.txt
    python tmpl_scan.py singles singles.tsv 2                   # ~45 min
    python timeout_pass2.py fixed singles.tsv singles_timeouts2.tsv 2
    python tmpl_scan.py pairs singles.tsv pairs.tsv 3
    python r4grid.py r1_fitted_new.tsv 6 8; python r4grid.py rebuild_rest.tsv 6 8
