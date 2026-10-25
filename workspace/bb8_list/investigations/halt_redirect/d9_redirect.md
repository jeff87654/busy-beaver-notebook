# D9-counter machine: redirecting its final halt into a 10th state J (2026-10-08, Opus investigator)

Base (9 states): `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH` (gh0LH_fable.md).
Extensions: I0 := {0,1}{L,R}J, J0/J1 free with at least one undefined. Tools, logs and tables: `halt_redirect/d9/`.

## Verdict

**Nothing found here comes near f_(omega+1).** The selector machine n1 (f_(omega+1) class) dominates every possible outcome of this redirect.
The best this redirect could give is omega-level 2 on top of B, which is still below f_(omega+1).

**Start configuration.** The D9 verifier's final verdict (gh0LH_verify.md) says the real class ends in the I0 halt for every b = 6 mod 10 (B = 3366 mod 4200).
So the I0 redirect does start from the right endgame, and the rebuild alternative does not occur in the real class.

**2-adic caveat.** The verifier found stages that halve huge tokens, and tower accumulators are -6 mod 2^huge.
My representatives match mod 10080 at best, so 2-adic matching is only to mod 32.
This is a second, independent reason the follower-world halts below are unreliable.

**No verified omega-level-2 candidate.**
- The follower finds 33 extensions that halt after at least one "A-tainted" deep round.
  These are rounds whose list length grows with the huge final accumulator A of the base.
- None of these halts survives the size-ordering checks.
  - The shortest chain (9 machines, led by `1LJ0LH_---1LB`) depends on an unrealistic size ordering at one literal stage.
    A literal test shows that this stage takes a different path when the new accumulator R exceeds about 2^(1.2u), and in the real run R is far above that bound.
  - For most of the other 24, the halt changes when the standard accumulator representative 19 is replaced by 2539, or the run times out.
- Most extensions (about 75 of 141) instead keep re-entering the redirect and run new rounds whose lists are proportional to A.
  In the follower these show up as exact repeats or as runs still going after 8000 stages.
  They are probably non-halting "infinite rebuilders", but this rests on the follower too.
- The 12 halters without an A-tainted round stay at omega-level 1, essentially the base score plus small terms.

## 1. The literal start (exact)

The base's final halting tape, closed form checked against grid2 dumps for 6 (A, r) pairs (`d9/mkhalt.py`):

    (10)^A 1 (10)^7 1 1 0 1 0 1 [0] 0 1 1 (10)^(2r+5) 0 1 0 1 1 0 1 1 1 (10)^9 1 1 0 1 1 0 1 1 0 1      state I on [0]

Here A = 2R'+7 is the huge final accumulator and r = R'' is the last small jump.
R'' is a fixed tower, independent of B, so A >> R''.

**Residues.** The universal accumulator residue is tau = 19 mod 2520, 2539 mod 5040, 7579 mod 10080 and 17659 mod 40320 (numres.tau(1)).
Hence A = 2*tau + 7 = 45 mod 5040, 5085 mod 10080 and 35325 mod 40320.
- The follower's standard representative 19 is correct only mod 2520, so it is wrong mod 16.
- A = 2565 is also wrong mod 16. A = 5085 is the correct class mod 10080.

## 2. Enumeration and classes (`renum`, `d9f.py`, pools E2565 and F5085)

There are 4 x 81 = 324 extensions. Under TNF branching (only the first J slot actually read is branched), they reduce to 164 behaviourally distinct machines.

| Class | TNF machines | Notes |
|---|---|---|
| Immediate halt (J reads its undefined slot within 4 steps) | 23 | Plus the 160 non-TNF duplicates (first-read J slot undefined, other slot defined). sigma = base + 0..2 |
| Non-trivial | 141 | Followed below |

Classification of the 141 with the canonical representative A = 5085, r = 19, the lookahead policy (see section 3) and a cap of 8000 actual stages (pool F5085, `d9/taint_F.tsv`):

| Follower outcome | Count | Meaning |
|---|---|---|
| HALT, no A-tainted deep clearing | 12 | Omega-level 1. 0LJ0LH_ with J1 = 0LE, 0LI, 0RC, 0RD, 1LA, 1LI; 1LJ0LH_ with J1 = 0LA, 0LG, 0LI, 0RA, 0RD, 1LI |
| HALT after an A-tainted deep clearing | 33 | The follower-world candidates; see section 4 |
| REPCYCLE (exact repeat of a post-jump configuration) | 46 | Endless rounds in the representative world; probably non-halting |
| MAXSTAGES (8000 actual stages, still running A-tainted rounds) | 28 | Unresolved |
| T/W with no K-moment by stage 1 | 12 | Champion-like counting in a non-canonical frame, so the stage server never sees a K-moment; literal budget of 4e9 steps exceeded. Unresolved |
| T/W mid-run (step budget of one literal stage) | 10 | Unresolved |

"A-tainted" means the A token was consumed before the deep clearing, either borrowed as a counter by a champion jump or unpacked literally into a list.
A deep clearing is a borrow at depth >= 300 in the representative world (`d9/taint.py`).
Deep rounds built only from R'' give f_(c R'')(small), which is negligible against A, because R'' is a fixed tower and K = 4.8B is far larger.

**Cross-check with A = 2565** (wrong mod 16; pool E2565, `d9/taint_E.tsv`).
- 28 of the 33 A-tainted halters also halt with A = 2565.
- 12 of them take a different path.
- Several REPCYCLE and MAXSTAGES outcomes swap.
- So the outcome depends on A mod 16, which is why the canonical table uses A = 5085.

## 3. Follower and tools (all in d9/)

- **mkhalt.py**: literal start tape. **renum.exe**: TNF enumeration (ren_*.tsv). **sim.exe, snap.exe**: literal runs and snapshots.
- **d9f.py**: the follower. It uses the stage35g server (family GH) and follow2.jump, starting from the halting tape in state I.
  - It reports which stages use the I0 and J slots.
  - Policies: std (all huge accumulators get representative 19), look, and allbig.
  - look: an accumulator that the next literal stage turns into a list gets the representative 859 (19 mod 840) instead of 19, so rebuilt rounds have u >= 40 and avoid Fable's small-u artefacts.
  - allbig: every huge accumulator gets the large representative.
  - `--mm 5040/10080` puts the standard representatives in the tau class mod 5040 or 10080 (2539 or 7579).
  - Exact-repeat detection (REPCYCLE). Optional stage cap through d9f_cfg.json.
- **accel.py**: affine-period accelerator. It compresses token lists into motif runs and skips k periods when four snapshots at spacing p have equal structure and constant count deltas.
  It reproduces Fable's phase-A period (11 stages, 6 zeros) and phase-C period (22 stages, 8 D9) and skips them.
- **analyze.py, taint.py, cmpv.py**: per-log summaries, A-taint detection, and comparison across representative systems.
- **collapse_test.py, collapse_small.py**: literal tests of the round-2 "collapse" stage (section 4).

## 4. The candidates and why they are not verified

### 4a. The shortest chain: `1LJ0LH_---1LB` (twin ---1LH; same collapse stage in 0LJ0LH_---1RF, 1LJ0LH_---0LF, ---0RB, ---0RG, ---1RH)

Full machine: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1LJ0LH_---1LB`.
Follower chain, A = 5085, standard representatives mod 10080 (`d9/cand/1LB_mm10080.log`):
1. Halt, then J1, then about 14 stages of R''-only work.
2. Stage 7 (literal): A is unpacked into a zero list `1^(2A-27)`.
3. Stage 15 (literal rebuild): `7 1^L 0 1^3 | 1 | r` becomes `4 (2r+5) 9^((L-15)/5) 5 14 0^2 9 1^((2L+5)/5)`, a D9 round with u = 2023 and m = 4053.
4. Stages 15 to 25: one phase-A period of deep clearings at depth about 0.8A. These are genuinely omega-level 2.
5. Stage 25 to 26: the "collapse".
   At `9^u 1 3 4 0 1 2 1^Z | 1 | R`, the literal stage walks into the D9 region and builds a halving cascade R, R/2, ... in the far bits.
   It returns the K-moment `0 X 0 4 1^(X-2) 0 3 0 7` with X near 0.475A.
6. One stage later: `X' 8 1^z 0 1 3 0 5 1^2`, the base endgame with z near 0.47A.
7. The final stage halts.

What is literally checked:
- **Final stage.** It halts on J0 for every z >= 4 tested: 4 to 29, 100 to 105, 1199 and 2400, with X in {45, 5085} and r in {19, 2539}.
  z = 3 continues, which is exactly round 1's redirect.
- **Collapse, R < 2^(1.2u).** The same output structure for 21 values of R from 19 to 44485, including R outside the tau class, at u = 2023.

**Why it fails.** The collapse output is X = c - log2(R), with c about 1.2u (2420 at R = 19, 2409 at R = 44485).
The representative world always has R < 2^(1.2u). In the real run R = f_(0.8A)(...) is far above 2^(1.2u).

Literal tests with R > 2^(1.5u), which is possible only for small u (`collapse_small.py`), show a different stage:
- R stays a token (2R+c).
- The zero list becomes a cascade 2^k, 2^(k-1)+1, ..., 9 with k about 2Z/3, or another u-dependent structure (u = 3, 5, 8, 12 all differ). One case halts outright (u = 8, R = 100).

A scaled-down run in the realistic ordering (A = 45, so u = 7, which is in A's u-class mod 168, with accumulators 7579) leaves the follower's path at this stage.
It reaches no endgame and times out at stage 78 (`cand/1LB_A45_mm10080.log`).
This is the M3 trap: a literal stage compares log2(R) with a list proportional to A.
**Status: refuted as a follower-world chain. The real behaviour is unknown.**

### 4b. The other 24 A-tainted halters (pool F5085)

These follow longer chains: an A-tainted rebuild of a D9 round with u near 0.4R or 0.8A, full phases A, B and C, often several rounds, then a halt on J0.
The 0LB/0LH/1RE family halts after 3461 stages with 186 deep borrows.
Sensitivity (`runs/M5040_*`, `runs/S45_*`, `runs/V*_*`):

| Machine (J1) | A = 2565 | A = 5085 | Accumulators 2539 (mod 5040) | Scaled-down, accumulators 7579 |
|---|---|---|---|---|
| 0LJ0LH_ 0RB / 0RH, 1LJ0LH_ 0LC | HALT 1140 | HALT 2358 | REPCYCLE 654 | MAXSTAGES |
| 0LJ0LH_ 1LB / 1LH | HALT 576 | HALT 576 | HALT 657 | MAXSTAGES (slow 2-stage count-down) |
| 0LJ0LH_ 1LC / 1LE, 1LJ0LH_ 0RC / 0RI | HALT 1360 | HALT 2408 | T (budget) | HALT 2507 by a different, shallow path |
| 0LJ0LH_ 0LB / 0LH / 1RE, 1LJ0LH_ 0LE | HALT 3461 / 1906 | same | T (budget) | T |
| 0LJ0LH_ 1RA / 1RG / 1RC | HALT | HALT | T or not run | T |

Only `0LJ0LH_---1LB` (twin ---1LH) halts in all three standard systems, by the same final shape `X 1 0 1^2 Y Z | 1 | 1`, then literal, then I0, then J0.
- Its last stages mix tokens of list size proportional to the rebuild accumulator R1 (e.g. 1309) with deep-round accumulators (e.g. 2284).
- In reality the second kind is far above 2^(first), and no run can realise that ordering. The scaled-down run took another path.
- **Status: follower-world only, not size-verified.**

### 4c. REPCYCLE and MAXSTAGES (74 machines)

These machines read I0 again and again, typically every round.
They rebuild lists proportional to the current accumulator, so the depth grows with every round.
In the representative world the configuration repeats exactly; in reality the round sizes grow with each repeat.
If the round structure is residue-determined, as the follower assumes, these never halt (the f_(omega+1)-shape rebuilders already seen for ---0RB at 9 states).
This is not proved.

## 5. Score comparison (conditional)

- **A-tainted halter (any of 4a/4b if real).** Its deep round clears lists of length c*A with A = 2R'+7, where A is roughly f_(K+3)(9B) and K = (24B+191)/5:
  sigma >= f_(cA)(2) >= f_omega(A), roughly f_omega(f_(K+3)(9B)).
  That beats:
  - the D9 base, f_(K+3)(9B);
  - the three-cycle sibling, about f_(K+42)(small);
  - M3, sigma > 2^(8B+56 arrows) 4, about f_(8B+51)^4, index about 8B;
  - the BB(10) champion, about 2^(N')(2N') with N' < 2^(25) 49 (score_comparison.md section 6), index N' far below A.
  This would be omega-level 2 on top of the record's B. **No such halter is verified.**
- **The 12 untainted halters.** sigma is about 2A + O(R''-terms) (e.g. 0LJ0LH_---0RC: an R''-derived round with 93 deep borrows, then a halt during that round's phase-A to phase-B transition; A untouched).
  That is omega-level 1, slightly above the D9 base, and below the three-cycle sibling and M3.

## 6. What would settle it

1. A size-faithful treatment of the collapse-type stages. Either:
   - prove a macro rule for `9^u 1 3 4 0 1 2 1^Z | 1 | R` with R > 2^(cu), from small-u literal data plus induction on u, then follow the cascade regime; or
   - extend the follower with a symbolic "R >> 2^(lists)" accumulator that literal stages may not unpack.
2. The same audit for the 0LJ0LH_---1LB ending and the 0LB family's last round.
3. The 12 no-K-moment T/W machines need a follower family with a non-canonical tail (snap.exe shows champion-like counting, e.g. 1RJ0LH_1LH---).

## Process notes

- The lead killed pools B5085, C2565 and D2565 under the CPU cap. Their logs in d9/runs/ are partial.
- At wrap-up I stopped the remaining pools M5040 and S45 and all their d9f.py workers.
  None of my processes are running now.
- M5040 finished 14 of 20 runs and S45 finished 10 of 29. The sensitivity table in section 4b uses what finished.
- Complete pools: A5085 (stop at second I0, superseded), E2565, F5085 (canonical), V2/V3/V4 and W859.
