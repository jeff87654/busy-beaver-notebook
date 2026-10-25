# 14-state borrow attempt, continuation: fresh K0 subtrees + slow-gadget slice (2026-10-12)

Continues REPORT_try14.md (same goal, tape `st_c12_k21.txt`, verifier `try14_verify.py` at
d = 31, 37, 43 requiring the nearest digit to track d-3 with identical prefix shape and
counter). Also resolves a farcount cross-check left open there.

## Verdict: NEGATIVE in the newly covered subtrees (screening)

119k further enumeration nodes at 14 states, 535 restart candidates, every one verified:
0 keep d, 0 slope-1, 0 d-dependent at all. The fresh subtrees do not even reproduce the
re-roll-into-counter family; most of their restarts only work at the exact screening sizes.

## Runs (benum.py --ns 4, caps 150k, all stopped early)
| run | seed | stages S | nodes | RS leaves | verified outcome |
|---|---|---|---|---|---|
| try14_d | J0 = 1RK, K0 = 0RK | 6 | 42.5k | 523 | const/none only |
| try14_e | J0 = 0LK, K0 = 0RK | 6 | 48.5k (stopped for a core swap) | 0 | no restart in the whole covered part |
| try14_f | J0 = 1RK, K0 = 0LK | 12 | 27.5k | 1 | none (fails at other d) |

- K0 seeds targeting base states collapse: `--j0 1RK --fix K0=0RA` finishes in 1 node
  (the gadget enters the base machine and never reads another gadget slot within S stages).
  Fresh coverage therefore used K0 values targeting new states (0RK), which sit after the
  0LA..0LK range already covered at 13 states and were untouched at 14.
- Verification tallies, in harvest order: 8 + 58 + 64 + 257 + 148 = 535 distinct candidates
  (`try14_cands_def_all.txt`; outputs in the session log and `try14_verify_df2/3/4.txt`,
  `try14_verify5.txt`). Tags: const or none throughout, with 'none' (no restart at another
  d within 8 stages) dominating the deeper try14_d region (227/257 and 118/148 in the last
  two batches). No 'dec' family member appeared in these subtrees, unlike K0 = 0LL in
  REPORT_try14.md.
- The S = 12 slice (try14_f, the productive K0 = 0LK zone with twice the stages to a first
  restart) reached only 1 RS leaf in 27.5k nodes at about 14 nodes/s, so the slow-gadget
  question is barely scratched; its single candidate restarts only at the screening digit.

## Cross-checks folded in from the farcount side (same session)
- All EAT/NOEND machines from the far 14-state runs fc14_1LKx / fc14_1LKy (left unvalidated
  in farcount/REPORT_fc14.md) were re-followed at K = 29, 71: no second far eat anywhere
  (`../farcount/fc14_chk_1LKx.txt`, `fc14_chk_1LKy.txt`).
- The class-11 borrow (c mod 42 = 25, d -> d-9 in farcount's no-far btable) was not pursued:
  the base table here (prefix digit with a far region present, the geometry a real cycle
  has) shows class 11 leaves d intact, and at true sizes the only borrowing end that reaches
  J0 is class 12 with k = 9 mod 12 (NOTES.md correction). A class-11 tape would screen a
  setup that cannot occur in a cycle.

## Reading
Combined with REPORT_try14.md, the class-12 borrow route at 14 states has now been sampled
in six seeded subtrees (K0 = 0LL, 1LA under 0LK, 0LK, 0RK under both J0 values, 0LK at
S = 12) totalling about 235k nodes and 698 verified candidates, with the single known
d-dependent family (marks re-rolled into the counter) as the only structure that ever
responds to d, and it still does not survive a second round. Remaining openings are the
same kind as before, only thinner: finish the 150k caps, the K0 = 1LK/1LL/1RK/1RL seed
groups, and a much deeper S = 12 run.

## Reproduction (in this dir)
    python benum.py --start st_c12_k21.txt --ns 4 --j0 1RK --fix K0=0RK --S 6  --maxnodes 150000 --out try14_d.tsv
    python benum.py --start st_c12_k21.txt --ns 4 --j0 0LK --fix K0=0RK --S 6  --maxnodes 150000 --out try14_e.tsv
    python benum.py --start st_c12_k21.txt --ns 4 --j0 1RK --fix K0=0LK --S 12 --maxnodes 150000 --out try14_f.tsv
    python bfilter2.py try14_d.tsv try14_e.tsv try14_f.tsv | Out-File -Encoding ascii try14_cands_def_all.txt
    python try14_verify.py try14_cands_def_all.txt

No processes from this continuation are running (stopped by the PIDs in try14_def_pids.txt).
