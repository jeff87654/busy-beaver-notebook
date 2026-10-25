# 14-state borrow attempt (class-12 tape, ns = 4): REPORT (2026-10-12)

Goal: extend the borrow route to 14 states (n1 + J0 gadget states K, L, M, N), looking for a
gadget that keeps the borrowed prefix digit d-3 as the nearest digit of the next round while
building the new counter from the accumulator U (the missing piece (a)+(b) of REPORT.md).

## Verdict: NEGATIVE in the covered subtrees (screening)

No kept-digit gadget found. 116k enumeration nodes, 163 restart candidates, all verified
strictly at three digit values: 0 keep d, 0 slope-1. The only d-dependent family is the known
re-roll-into-counter family, and it does not survive a second round.

## Method
- Start tape: `st_c12_k21.txt` (class-12 clean borrow, k = 21 = 9 mod 12, prefix digit d = 31),
  with verification starts `st_c12_k21_d37.txt` / `_d43.txt`.
- Enumeration: `benum.py --ns 4 --S 6` (lazy TNF, branch only on gadget slots read), three seeded
  subtrees chosen outside the ns = 3 coverage of REPORT.md, node caps 150k, stopped early
  (see coverage). Two Idle processes at a time.
- Filter: `bfilter2.py` (first restart whose last prefix digit >= 3 has only tokens < 3 after it).
- Strict verify: `try14_verify.py` — first restart from d = 31, 37, 43 must have identical
  prefix shape and identical counter, with the nearest digit equal to d-3 (KEEP) or increasing
  by 6 per step (SLOPE1). This rejects gadget constants (e.g. 28 = 2U-10 at U = 19) and the
  irregular increasing cases of the ns <= 3 runs, both re-checked as controls (2/2 irreg).
- Round survival: `try14_rounds.py` follows a machine printing every round start.

## Coverage (all stopped before their 150k caps; benum has no resume, reruns redo work)
| run | seed | nodes | RS leaves | result |
|---|---|---|---|---|
| try14_a | J0 = 1RK, K0 = 0LL | 48.5k | 162 | one degenerate family (K = 0LL0LM, L = 0LD0LK): tiny counters 6-28, nearest digits 3/5/6/40/42, all gadget constants |
| try14_b | J0 = 0LK, K0 = 1LA | 38k | 0 | no restart and no halt within 6 stages anywhere in the subtree |
| try14_c | J0 = 1RK, K0 = 0LK | 29.5k | 1 | constant |

Filters/verifies: 163 `bfilter2` candidates in total (`try14_cands_all.txt`), each run through
`try14_verify.py` at the three d values (`try14_verify2/3/4.txt` plus the first batch in the
session log): const or no-restart-at-other-d for all but two machines.

## The only d-dependent machines (known family, new variant)
`..._1RK0LC_0LL0LM_0LD0LK_0RN0LM_0RM0RK` and `..._0RN0RM_0RM0RK` (14 states, from try14_a):
first restart P = [x], counter c = d-1, with x = 2U - (d-3)/2 (std: d = 31/37/43 gives
x = 24/21/18, c = 30/36/42). This is the marks-re-rolled-into-the-counter family of REPORT.md:
the counter is built from d, not from U, and the nearest digit is a fresh U-derived one.
Followed from the class-12 tape (std, 200 stages, `try14_rounds.py`) it makes exactly one
round start (P = [24], c = 30) and never restarts again, like its ns = 3 predecessors.

## Reading
- The covered 14-state subtrees behave like the 12/13-state ones: restarts are either degenerate
  (constant small counters), gadget-constant digits, or the re-roll-into-counter family.
  Nothing re-rolls the marks into a digit while moving U into the counter.
- This does not close 14 states: three seeded subtrees at S = 6 is a small fraction of the
  J0 x K0 space (prior ns = 2 completeness needed 366k nodes for ALL J0 at 12 states; ns = 4
  subtrees are far larger), and gadgets needing more than 6 stages to their first restart are
  invisible here, as before.
- Cheapest continuations, in order: finish the try14_a / try14_c caps (same commands, higher
  --maxnodes); sweep the remaining K0 seeds for J0 = 1RK and J0 = 0LK at ns = 4; try S = 10-14
  on the K0 = 0LK subtree, where the ns = 3 run needed S = 14 for part of the class-7 tape.

## Reproduction (in this dir)
    python benum.py --start st_c12_k21.txt --ns 4 --j0 1RK --fix K0=0LL --S 6 --maxnodes 150000 --out try14_a.tsv
    python benum.py --start st_c12_k21.txt --ns 4 --j0 0LK --fix K0=1LA --S 6 --maxnodes 150000 --out try14_b.tsv
    python benum.py --start st_c12_k21.txt --ns 4 --j0 1RK --fix K0=0LK --S 6 --maxnodes 150000 --out try14_c.tsv
    python bfilter2.py try14_a.tsv try14_b.tsv try14_c.tsv | Out-File -Encoding ascii try14_cands_all.txt   (PowerShell)
    python try14_verify.py try14_cands_all.txt
    python try14_rounds.py <machine> --stages 200

Note: plain `>` redirection in PowerShell 5.1 writes UTF-16 and corrupts machine strings for
the next Python step; use `Out-File -Encoding ascii` for candidate files.
No processes from this attempt are running (stopped by the PIDs in try14_pids.txt; the other
python jobs on the machine predate it).
