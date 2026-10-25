# bb9_symsim: symbolic macro simulator; re-grade of the M9-engine search (bb9_m9seed)

The lead writes this file from agent symsim's final message (2026-10-17), because the harness blocks subagents from writing .md reports. The detailed notes are progress_log.txt (copy: REPORT_notes.txt). The final binary is symsim_final6.exe (source symsim.cpp), the outputs are in final6/, and attention.txt lists the BUDGET machines.

## Result
- 144,277 holdouts: 144,268 CYCLE (certified), 9 BUDGET, 0 HALT, 0 UNDECIDED.
- 12,371 broken_mid mutants: 12,197 CYCLE, 174 BUDGET, 0 HALT.
- No halters, and no record candidates.

## Tool
- Run-length direction tape, with macro steps for chain sweeps, rotated sweeps and word steps.
- Counts are linear forms over symbols. Each symbol is a fixed integer with a proven lower bound and a residue mod MG (default 2520).
  - Sign tests use the bounds only; residue tests use only the known precision.
  - Anything else is UNDECIDED. Nothing is guessed.
- Exact jumps, applied only when the core is intact:
  - Ch (Coq CH_CA);
  - BLK: Ca j b (blk a z) -> Ca (j+1) (iter a (W j) b) z;
  - multi-BLK.
- Ligocki-style prover with shadow constraints. The certificates are:
  - LIN: an infinite linear rule;
  - GEN: inductive over all x satisfying the constraints, with suffixes -W (fresh W each loop), -AFF (a non-translational count map) and -X (runs left below the touched prefix and never read again);
  - ESCAPE: the head runs into blank tape forever;
  - BOUNDED: the head is trapped inside one short word.
- Residue law: W(j>=4, b) is 119 mod 720720 for even b and 2 for odd b. This was checked for MG = 36 through 720720, and the CRT periodicity is proved.

## Validation (final binary, 0 bad everywhere)
- All 308,302 m9s halting leaves give HALT, and 308,294 exact sigmas match. The top halters W(3,3)+7 and W(4,0)+6 were re-found.
- M9 c_init(1) gives sigma 23. The BB(5) champion gives 47,176,870 steps and sigma 4098.
- Literal cross-check against lit.cpp on about 13k machines (random 2-6-state TMs, M9 and free-slot mutants, holdouts on random tapes): every literal halter matched in status, sigma, final tape and steps. No machine that halts literally was ever given CYCLE.
- The HUGE harness compared symbolic runs with exact runs on about 19k machines: 0 conflicts, and about 8,000 symbolic sigma formulas evaluated to the exact sigma.
- Verdicts are identical at MG = 36, 2520 and 720720.

## Grading by class (holdouts)
| class | GEN-W-AFF | GEN-AFF | LIN / LIN-CH | ESCAPE | other | BUDGET |
|---|---|---|---|---|---|---|
| LINJ (14,226) | 14,212 | - | - | - | 10 GEN-W-AFF-X | 4 |
| NEARLINJ (605) | 602 | 3 | - | - | - | 0 |
| OTHER (127,198) | 113,693 | 13,495 | 5 / - | - | - | 5 |
| norep (2,248) | 20 | 92 | 1,788 / 180 | 146 | 20 GEN-AFF-X, 1 GEN-W-AFF-X, 1 BOUNDED | 0 |

broken_mid: 9,812 LIN, 2,298 GEN-AFF, 67 LIN-X, 17 GEN-AFF-X, 3 LINxK, 174 BUDGET.

## Needs attention
- **F1** = 1RB1RA_1LI1RC_0LD1LG_0RE1LD_---1RF_0LI0RA_1RA0LH_1LG1LH_{1LA,1LG,1LH,1RA}0LF (6 machine/start pairs).
  - The engine runs at f_w level (j = sums of W values). Beyond the engine sits a tail that grows like a counter: its gap sizes go (6) (2,3) (4,1) (2,1,1) (8) (2,5) (4,3) ...
  - It looks non-halting, but proving that needs a counter invariant (E0 must never read 0), which the tool cannot produce. This is the only family with record potential if it ever halted.
- **F2** (one big jump, sigma <= 10): not record-relevant.
- **broken_mid BUDGET (174):** 78 exponential growers, 45 Collatz-like, 59 exact counters. All are core-broken, with no f_w engine, so they are not record-relevant.

## Follow-up (agent f1-look, bb9_f1/)
- **F1: PROVED non-halting** (on paper, checked literally for 3e6 steps on each pair).
  - E is entered only by D0 = 0RE, and C only by B1 = 1RC.
  - Invariant: in state C, the cell left of the head is 1; in state D, the head cell or the cell to its right is 1.
  - So E always reads 1, and the halt E0 is unreachable. The counter tail plays no part.
- **Backward reachability** (backref_s.py, depth 30) on all 183 attention rows:
  - 164 have the halt slot UNREACHABLE (dying at depth 1-7), including F2;
  - 19 I0 rows are undecided (bb9_f1/attention_undecided.txt).
- None of the remaining 19 is record-relevant.

## Scaled HUGE harness (symsim, final)
- Original six hugetests: 18,000 configurations, 0 conflicts, 5 UNDECIDED; about 8,000 symbolic sigma formulas matched the exact sigma.
- Scaled run, weighted toward OTHER, norep and broken: 17,248 more configurations, 0 conflicts, 539 UNDECIDED (3.1%, all refusals, e.g. a symbol known only to be >= 21 compared with about 40).
  - It used EXMAX 20/50 (j and b symbolic well below the old representative size of 40-76) and (10)^N blocks with N about 10^6.
  - 714 sigma formulas were checked in the block runs (298 broken + 188 norep + 228 OTHER), 0 mismatches.

## (B) template-fitted regrade, complete (symsim, 2026-10-18)
| slice | RULED | UNRULED | SKIP | HALT | CYCLE | BUDGET | UNDECIDED |
|---|---|---|---|---|---|---|---|
| c7m12 (787) | 773 | 0 | 14 | 517 | 8 | 262 | 0 |
| n1f0 (178) | 130 | 48 | 0 | 95 | 0 | 79 | 4 |
| roots9 (594) | 555 | 33 | 6 | 186 | 0 | 408 | 0 |
- All 796 halts that come after jumps end after exactly one clear:
  - C(10,2,0): 592 rows, sigma 6X0+31..35 or 24X0+48..107;
  - C(34,2,0): 201 rows, sigma up to 24X0+107;
  - C(2,2,0): 3 rows.
  - All are far below fw2.
- The 4 UNDECIDED rows hit the 3 GB memory cap. They are UNRULED n1f0 rows with affine chains.
- Backref: 106 single slots are UNREACHABLE, but 0 machines have every undefined slot unreachable. kgval: BAD 0.
- M1 is a known LOOPER (bb9_c7m12_loopers/groups.tsv; clear depth grows by +78 per round). Closed.
- Triage2 (3 chained rounds, X := residue mod 2520) on the 602 RULED BUDGET rows is about 40% done.
  - Most rows show a new clear in every round, the unbounded-looper shape.
  - Two families halt with fixed depth, so both are far below fw2:
    - H1 = 1RB0RA_1LC1LF_1RD0LB_1RA0LI_---0LC_1RG1LD_1LC0RH_1RG1LF_1LE1RI (+1 sibling): about f_35 iterates.
    - About 10 roots9 rows: about f_34(X0).

## Triage2 final (symsim, 2026-10-18)
Method: on all 602 RULED BUDGET rows with at least one jump, continue each machine past its clear with X := X mod 2520 for 3 rounds. Evidence only, not a proof. No record.
- 413 rows show a new clear every round: unbounded f_w-iterator loopers, closed (c7m12 116, n1f0 13, roots9 284).
- 14 rows halt in the substituted run, in 3 families; all clear depths are fixed, so all are far below fw2 (post/t2_halters.txt):
  - 10 roots9 rows: about f_34(X0);
  - 3 H1-type roots9 rows: about f_35 iterates;
  - 1 c7m12 row: about f_10(X0).
- 168 rows stay BUDGET with no further clear (c7m12 133, roots9 35): a non-champion post-clear engine, or a bouncer symsim doesn't accelerate. No halts in literal small-n runs.
- 6 roots9 rows have no jump to continue from, and 1 roots9 row is UNDECIDED.
- Slices c7m12 / n1f0 / roots9 under symsim: CLOSED, no G candidate and no fw2-beater.

## Correction (outer-counter, 2026-10-18)
Triage2's substitution X := 6 is unfaithful: it flips L1's post-clear branch, while X = 6 + 2520t matches the
symbolic run. So the "413 loopers closed" and "168 BUDGET" labels are not reliable. A faithful regrade
(bb9_outer/tools/ffg.py) of the 602 rows gives 0 HALT, 10 L1-type loopers, and 591 unresolved. See bb9_outer/REPORT.txt
and OPEN_CANDIDATES.txt.
