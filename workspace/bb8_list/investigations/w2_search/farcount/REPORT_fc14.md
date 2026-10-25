# 14-state far-run attempt (route 1 at ns = 4 + L12f clone-splits): REPORT (2026-10-12)

Goal: test the far-run outer counter at 14 states. A hit needs a class-12 in-place restarter
whose leading far D2 count kD2 drops by a fixed delta at EVERY round start (rounds ~ K/delta,
K accumulator-sized), i.e. at least two successive drops in screening and K-dependent round
counts at two K values. This extends REPORT.md's 12-state structural negative.

## Verdict: NEGATIVE in the covered subtrees (screening)

264k enumeration nodes at 14 states plus a complete single-clone sweep around the L12f looper
at 13 states produced no machine that eats the far run more than once. Every eater takes a
K-independent constant delta exactly once, exactly as at 12 states.

## Baseline reproduced
- L12f (`..._1LK0LC_0LL0RA_1LL0LI`) from far_29 + [0 1^29|1|19] (farfol.py): round starts at
  stages 80, 97, 114, 131, 148, all c = 26 (class 12), kD2 = 10 constant, far rest
  4080 -> 4888 bits (+190/round), z += 82/round. Matches REPORT.md section 3.
- Scanner control: `fc14_scan.py` on the 12-state files (e12_ns2.tsv,
  old_e12_1LK_partial.tsv) reports all 18 old EAT/NOEND machines as single-drop (DROP1),
  none DROP2. Counting includes the initial K = 29 -> first-RS drop.

## Enumeration coverage (enum12.py --ns 4 --maxrs 5, K = 29, c = 40, z = 29, caps 120k, all stopped early)
| run | seed | nodes | EAT | NOEND | KEEP | note |
|---|---|---|---|---|---|---|
| fc14_0LKx | J0 = 0LK, K0 = 0RK (past the ns = 2 frontier) | 63.5k | 12 | 64 | 15 | one family K = 0RK0LL, L = 0LL0LM... |
| fc14_0RK | J0 = 0RK (never run at ns = 2) | 54k | 7 | 65 | 0 | class-12 loopers at kD2 = 20, prefix length 22 |
| fc14_1LK | J0 = 1LK | 30.5k | 0 | 0 | 0 | stopped, replaced by seeded runs |
| fc14_1RK | J0 = 1RK (never run at ns = 2) | 11.5k | 0 | 0 | 0 | stopped (slow, NORS-heavy) |
| fc14_1LKx | J0 = 1LK, K0 = 0LL (L12f's K0) | 81.5k | 0 | 3 | 0 | DFS still in K1 = 0L* subtrees, short of K1 = 0RA |
| fc14_1LKy | J0 = 1LK, K = 0LL0RA (L12f's K row) | 23.5k | 0 | 7 | 0 | DFS still in L0 = 0L*/0R* subtrees, short of L0 = 1LL |

Final scan (`fc14_scan.py`, output `fc14_scan_all.txt`): 158 single-drop rows, 0 double-drop
rows across all six files. Typical new eater: 29 -> 22 once (class 4, no second round start),
29 -> 1 then class-9 rounds forever, or 29 -> 20 then class-12 rounds with kD2 frozen.

## Validation at two far lengths (decisive for this route)
All 148 distinct EAT/NOEND machines from fc14_0LKx.tsv and fc14_0RK.tsv were re-followed with
`chk_eat.py` at K = 29 and K = 71, six round starts, generous limits (outputs
`fc14_chk_0LKx.txt`, `fc14_chk_0RK.txt`). Result: 0 of the 296 tracks drops kD2 twice.
Examples: `..._0RK0LC_0LK0LL_0LJ0LM_1RN0LM_0RM0RD:` 29 -> 20 and 71 -> 62 (delta 9), then
20/62 constant through six class-12 round starts at both K. So even where the enum12 stage
cut might have hidden a slow second round (NOEND), no second eat exists, and rounds-to-halt
cannot scale with K in any of them.

## Clone-split sweep around L12f (13 states, complete for its family)
`fc_clone.py`: for each of the 6 gadget slots J0, J1, K0, K1, L0, L1, redirect the slot's
target to a new state M copying that target's row, and vary one M entry over all 52
transitions to A-M plus halt: 636 variants, each tracked from the class-12 far start
(control reproduces L12f: kD2 29 -> 26, then 26 constant, six class-12 starts).
Result (`fc_clone.log`): 0 double drops. 201 variants keep six class-12 round starts with
exactly one drop (new kD2 plateaus 2..27 depending on variant, e.g. J0-clone M1 = 1LM gives
29 -> 2 then frozen); 3 variants (K1 clones) have six round starts with no drop at all.
So one extra state spent splitting any single gadget transition of the only known class-12
looper cannot turn its one-time eat into a per-round eat: the split state is entered
identically every round, while the per-round difference it would need to sense (old far vs
fresh deposits) is exactly what the rebuilt prefix hides.

## Reading
- REPORT.md's geometric obstruction survives two more states in every subtree reached: the
  prefix a restarter rebuilds becomes the buffer the next class-12 end consumes (borrow
  7 -> 4 in L12f clones), and no found gadget deletes a D2 from the old run on later rounds.
- Not excluded: the J0 = 1LK deep branches (both seeded runs stopped before DFS reached
  L12f's own slot values at ns = 4, so 14-state gadgets that extend L12f's exact path with
  M/N read only later are largely unexplored!), double clones L12f + M + N, and restarts
  needing more than the enum12 stage limits.
- Cheapest continuations: (1) `enum12.py --ns 4 --j0 1LK --fix K0=0LL,K1=0RA,L0=1LL,L1=0LI`
  does nothing new alone (no undefined slot is read); instead seed `--fix K0=0LL,K1=0RA,L0=1LM`
  style jumps or add a --fix-driven branch that forces one L/M slot to target M/N so DFS
  starts inside L12f's neighbourhood with the extra states live. (2) Double-clone sweep:
  apply fc_clone's construction twice (M then N) on the 201 looping single clones, restricted
  to slots disjoint from the first clone (about 201 x 424 = 85k tracks, a few core-hours).
  (3) Finish the six caps above (enum12 appends; reruns redo from scratch).

## Reproduction (in this dir)
    python enum12.py --out fc14_0LKx.tsv --ns 4 --maxrs 5 --maxnodes 120000 --j0 0LK --fix K0=0RK
    python enum12.py --out fc14_0RK.tsv  --ns 4 --maxrs 5 --maxnodes 120000 --j0 0RK
    python enum12.py --out fc14_1LKx.tsv --ns 4 --maxrs 5 --maxnodes 120000 --j0 1LK --fix K0=0LL
    python enum12.py --out fc14_1LKy.tsv --ns 4 --maxrs 5 --maxnodes 120000 --j0 1LK --fix K0=0LL,K1=0RA
    python fc14_scan.py fc14_0LKx.tsv fc14_0RK.tsv fc14_1LK.tsv fc14_1RK.tsv fc14_1LKx.tsv fc14_1LKy.tsv
    python chk_eat.py fc14_0LKx.tsv 29,71 ; python chk_eat.py fc14_0RK.tsv 29,71
    python fc_clone.py

Note: enum12.py's self-Idle ctypes call does not take effect under Start-Process on this
machine (processes showed Normal priority); set PriorityClass = Idle by PID after launch.
No processes from this attempt are running (enumerations stopped by PID from fc14_pids.txt,
clone and chk_eat runs finished; other python jobs on the machine predate it).
