# Neighbors of the digit-list counter: the last six

Parent: `1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---`, proved non-halting in
`proofs/BB8_76450_1RB1RA.v`.
Family: the six unresolved neighbors in `bb8_list/neighbors/remaining6.txt`. The generators had refused all six.
The other 22 of the 28 unresolved neighbors were already proved; see `neighbors_F1.md` and the `BB8_nbr_*` rows of
`proofs/README.md`.

## Verdict

**All six machines never halt. Confidence: proved (Coq PASS) for all six.**
- There is no halter. None of the six has a sigma, and none bears on the BB(8) record bar 2↑¹¹2↑¹¹3.
- **Key question: can a reset with k trailing zero digits meet the halting boundary, including after a rebuild? No,
  in every machine.**
  - Every reset that meets k ≥ 1 trailing zero digits has b ≥ k+1. The Coq lemmas `EX`/`IN` prove this for clearing
    any all-nonzero digit list.
  - The halting boundaries are k = b+1 (A0 machines), k = 2b−1 (machine 5) and k = 3b−1 (machine 6). All lie above
    k = b−1.
  - Every rebuild, including machine 5's irregular b = 1 rebuild, produces a list of nonzero digits. The generic
    clearing lemma `GEN` therefore restarts the same cycle.

| # | machine | changes (from parent) | family | halting boundary | verdict | confidence | proof file (`bb8_list/proofs/`) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `0RF1RA_0RC0RA_0LD1RC_0LA1LE_1LF0LG_1LB0RD_0LH1LF_1RF---` | A0:0RF D0:0LA | F-shape, WALK kind A1, b3 = 0 | k = b+1 | never halts | proved (Coq PASS) | `BB8_nbr_A0_0RF_D0_0LA.v` |
| 2 | `0RF1RA_0RC0RA_0LD1RC_1LB1LE_1LF0LG_1LB0RD_0LH1LF_1RF---` | A0:0RF D0:1LB | F-shape, WALK kind A0 | k = b+1 | never halts | proved (Coq PASS) | `BB8_nbr_A0_0RF_D0_1LB.v` |
| 3 | `0RF1RA_0RC0RA_0LD1RC_0LG1LE_1LF0LG_1LB0RD_0LH1LF_1RF---` | A0:0RF D0:0LG | F-shape, WALK kind A1, b3 = 1 | k = b+1 | never halts | proved (Coq PASS) | `BB8_nbr_A0_0RF_D0_0LG.v` |
| 4 | `0RF1RA_0RC0RA_0LD1RC_1RC1LE_1LF0LG_1LB0RD_0LH1LF_1RF---` | A0:0RF D0:1RC | F-shape, WALK kind A0 | k = b+1 | never halts | proved (Coq PASS) | `BB8_nbr_A0_0RF_D0_1RC.v` |
| 5 | `1RB1RA_0RC0RA_0LD1RC_0LG1LE_1LF0LG_1LB0RD_0LH1LF_1LA---` | D0:0LG H0:1LA | B-shape, m = 2, split rebuild | k = 2b−1 | never halts | proved (Coq PASS) | `BB8_nbr_D0_0LG_H0_1LA.v` |
| 6 | `1RB1RA_0RC0RA_0LD1RC_1LG1LE_1LF0LG_1LB0RD_0LH0RC_1RF---` | D0:1LG G1:0RC | B-shape, m = 3, offset h = 1 | k = 3b−1 | never halts | proved (Coq PASS) | `BB8_nbr_D0_1LG_G1_0RC.v` |

`check.py` output is in `neighbors_final6/check_py.out`; each line reads
`PASS <file>: <machine> never halts (machine-checked, no axioms)`. The files compile in 11-19 s each.

**Totals.** With these six, all 28 unresolved neighbors of the counter are proved non-halting in Coq.

## Rules (all read off by `kfit.py`, then proved for all parameters in Coq)

**A0 machines 1-4.** These use the F-shape family `Kf(ds; a; b) = 0^inf 1^d1 0 ... 1^dn 0 1^a 0 1^b 0 F> 0^inf`
(`kfit.py TM --grid --shape F,0`). kfit's grid gave 1,352 cases, 0 mismatches, including 9/9 predicted halts.

| rule | kind A1 (D0 = 0LA: b3 = 0; D0 = 0LG: b3 = 1) | kind A0 (D0 = 1LB, 1RC) |
| --- | --- | --- |
| R1 | K(ds; a+1; b) -> K(ds; a; b+3) | same |
| R2 | K(.., y+1; 0; b) -> K(.., y; b+2; b3) | K(.., y+1; 0; b) -> K(.., y; b+1; 3) |
| R3 (1 ≤ k ≤ b) | K(.., y+1, 0^k; 0; b) -> K(.., y, b+2−k, 1^(k−1); 1; b3) | same refill, then (a, b) = (0, 3) |
| halt | k = b+1 | k = b+1 |
| R4 | K(; 0; b) -> K(1^(b+1); 1; b3) | K(; 0; b) -> K(1^(b+1); 0; 3) |

**Machine 5 (D0:0LG H0:1LA).** B-shape with m = 2: R1 b -> 2b+2; R2 a = 2b+1; R3 refill 2b+1−k; halt at k = 2b−1.
- The rebuild fits only for b ≥ 2: K(; 0; b) -> K(5, 1^(2b−3); 1; 1).
- For b = 1 the rebuild is K(; 0; 1) -> K(; 5; 1).
- Both cases are the same END4b output, `0^inf 1^5 (01)^i B>` with i = 2b. At i = 2 it parses with no digits and
  a = 5.

**Machine 6 (D0:1LG G1:0RC).** B-shape with m = 3: R1 b -> 3b+3; R2 a = 3b+2; R3 refill 3b+2−k; rebuild
(3, 1^(3b−2)); 1; 1.
- The halting boundary is k = 3b−1, not the template's 3b.
- The kfit grid had 0 mismatches (HALT 9/9, R3 96/96).

## Why each machine never halts (the key question)

**A0 machines 1-4.**
- R3 applies for 1 ≤ k ≤ b; k = b+1 halts.
- Clearing a digit list (1^j, w+1) from the post-R3 state (a3, b3) ends with b ≥ w + j + 2. The (a3, b3) are
  (1, 0), (1, 1) or (0, 3), and a3 + b3 ≥ 1 is all the base case needs.
- The refill b+2−k ≥ 2 keeps b growing. The Coq lemma `IN` needs only refill ≥ 1 plus the previous bound.
- So every reset meeting k zero digits has b ≥ k+1, R3 always applies, and k = b+1 is never met.
- **Kind A0 case.** R3 leaves a = 0, so a reset follows at once. When the last digit is a 1, R2 fires: a = b+1 and
  then R1 gives b = 3 + 3(b+1).
  - This is the case `neighbors_F1.md` flagged for re-checking. It is covered by `CH`, since R1iter from (b+1, 3)
    gives b' ≥ b+4.
  - `EX` starts from (a, b) = (0, 3).
- The rebuild (1^(b+1); a4; b4) has nonzero digits, so `GEN` applies.

**Machine 5.**
- The halting boundary is 2b−1 > b−1 ≥ k, and R3's Coq domain is k ≤ 2b−2.
- **After a rebuild.**
  - For b ≥ 2 the rebuild (5, 1^(2b−3)) has nonzero digits.
  - For b = 1 the rebuild K(;5;1) has no digits: five R1 steps give K(;0;B) with B ≥ 6, then the regular rebuild.
- Coq: `Top B` is the raw END4b tape. `TopZ` splits B = 0 (= Kc [] 5 1) from B = S B' (= Kc (1^(2B'+1) ++ [5]) 1 1),
  and both go through `GEN`.

**Machine 6.**
- **Mechanism.** D0 = 1LG together with G1 = 0RC changes the start of each LOOP.
  - From `1^n C> 0`: C0, D1, E1 (0LG), G1 (0RC), C0, D0 (1LG), G1 (0RC), C1, C0, D1, E0 (1LF).
  - This touches the last five cells before the parent's F crossing (F1 0RD, D1 1LE, E0 1LF) takes over.
  - Hence LOOP and FINAL need a run of at least 4 ones, not 3. A run of exactly 3 at FINAL is the halting reset:
    refill 3b+2−k = 3, i.e. k = 3b−1.
- **Proof.** R3 is proved for k ≤ 3b−2. Resets have k ≤ b−1 ≤ 3b−2, so the halt is never met.
- **After a rebuild.** The rebuild (3, 1^(3b−2)) has nonzero digits, so `GEN` restarts the cycle.

## What was changed in the generators (all in `neighbors_family_tools/`)

**1. A0 machines: F-shape WALK variant.**
- **Why the old generator refused.** These machines keep the parent's F1 = 0RD, unlike the A0 combination of
  `neighbors_F1.md`, which has F1 = 1LF. After the refill, A0 therefore walks right through the (10) pairs and leaves
  them unchanged.
  - One pair costs 8-16 steps: `A> 0 1 0 1 0 -> 0 1 A> 0 1 0`.
  - The old template moved a `0 1 1 0` block instead (`SHIFT`).
  - For D0 = 0LA/1LB/1RC the walker reads one cell of the next pair. planner8's fixed-context crossings cannot
    express that, so it is a hand-written Coq lemma, `WALK`: `WSTEP` by `execute`, then induction as in `SHIFT`.
- **New and changed files.**
  - `kphases_F0w.py` (new): phases FIN1 (to the walker start), E4A (rebuild, to the walker start) and FEND (the fixed
    tail). Targets come from the kind and b3.
  - `kcoq_template_F0w.v.in` (new): `WSTEP`/`WALK`; RES = ENTRY + LOOPS + FIN1 + WALK + FEND. The R2/R3/Top
    constants, `CH`'s R1iter start and `EX`'s start (a3, b3) are template variables. The refill S (S r) enters
    `EX`/`IN` as `S (B1 − S j)`.
  - `gen_kcoq_F0.py`: a fit equal to the old EXPECT takes the old path unchanged. A fit matching kind A1 or A0
    (`walk_kind`) goes to `gen_walk`; anything else is refused.
- **Pitfall.** `rewrite (align_lpow 1 [0] <explicit ys> n)` found no match even though the goal printed identically.
  `rewrite (align_lpow 1 [0] _ n)` works.

**2. Machine 5: split rebuild (`gen_kcoq.py`).**
- If kfit's R4 has no fit, `fit_r4_split` fits R4 on b = 2..6 and records the literal b = 1 rebuild.
- The template then takes `Top B` = the END4b output with i = B·m + 2m − 2 − h, `R4` ends with `finish_norm`, and
  `TopZ` does the B = 0 / B = S B' split.
- The generator checks that the b = 1 rebuild has nonzero digits and b ≥ 1.

**3. Machine 6: halting-boundary offset h = (m − 3) − ch.**
- h ∈ {0, 1} is allowed (plus 2m − 4 − h ≥ 0). With h = 1:
  - `kphases.py` (`phases(m, h)`, `coq_stmt(name, m, h)`, CLI `--h`) puts h extra concrete 1s in LOOP and FINAL.
  - `fit_end4` probes from `1^(2+h) C>`, and END4b starts there.
  - The template gets `ones4`. The LOOPS/LOOPS_blank run offsets, R1's FINAL argument and RES/R2/R3's constant
    2m−4−h shift, as do the R3 digit S³⁺ʰ r, the R4 LOOPS_blank count and the `EX`/`IN` witnesses.
- All h-dependent text is a template variable whose h = 0 value is the old text.

**Backward compatibility.**
- `neighbors_final6/regen_check.sh` regenerates the 22 earlier neighbor proofs with the patched generators and
  compares them byte for byte with `proofs/`.
- 21 are identical. The 22nd, `BB8_nbr_D0_0RF.v`, differs only in its title line, because it was generated with a
  different `--title`.
- Regenerated scratch copies of `BB8_nbr_D0_1LF.v` (B-shape path) and `BB8_nbr_A0_0RF_D0_0LE.v` (old F0 path) PASS
  `check.py` (`neighbors_final6/check_py_regen.out`).
- Pre-patch copies are kept as `neighbors_final6/*.orig.*` for diffing.

## Orbits (no sigma, for orientation only)

| # | first K configuration | early history |
| --- | --- | --- |
| 1 (0LA) | K(1; 1; 0) at step 48 | -> K(;5;0) -> ... -> K(;1;12) -> rebuild K(1^16; 1; 0) at step 1,234 |
| 2 (1LB) | K(1; 0; 3) at step 56 | -> K(;4;3) -> ... -> K(;0;15) -> rebuild K(1^16; 0; 3) at step 1,206 |
| 3 (0LG) | K(1; 1; 1) at step 45 | -> K(;6;1) -> ... -> K(;1;16) -> rebuild K(1^20; 1; 1) at step 1,581 |
| 4 (1RC) | K(1; 0; 3) at step 52 | -> K(;4;3) -> ... -> rebuild K(1^16; 0; 3) at step 1,166 |
| 5 (D0:0LG H0:1LA) | K(5,1; 1; 1) at step 143 | -> K(5,0; 9; 1) -> K(5,0; 1; 766) at step 790,537 (b doubles per R1) |
| 6 (D0:1LG G1:0RC) | K(3,1^7; 1; 1) at step 477 | -> K(3,1^6,0; 20; 1) -> K(3,1^6,0; 14; 1821) at step 2,504,887 |

All six are Ackermann-type digit-list counters like the parent. This does not matter here, since none halts.

## Reproduction

`python` means `..\..\third_party\venv311\Scripts\python.exe` below; run from the folder named.

In `bb8_list\investigations\neighbors_family_tools`:
- Fits:
  - `python kfit.py <TM> --grid --shape F,0` for machines 1-4;
  - `python kfit.py <TM> --grid` for machine 6;
  - `python kfit.py <TM>` for machine 5, whose R4 shows "no fit" with the raw rebuilds.
- Phases:
  - `python kphases_F0w.py <TM> A1 <b3>` or `... A0 3` for machines 1-4;
  - `python kphases.py <TM> 3 --h 1` for machine 6.

In `bb8_list\investigations\neighbors_final6`:
- `sh gen_all.sh` regenerates the six proofs into `coq\`. It is deterministic: the output is identical to
  `proofs\`.
- `sh regen_check.sh` runs the backward-compatibility check.
- `trace.py` and `trace2.py` print literal traces (run-length and raw bits) from a K configuration.

In `bb8_list\proofs`:
- `python check.py BB8_nbr_A0_0RF_D0_0LA.v BB8_nbr_A0_0RF_D0_1LB.v BB8_nbr_A0_0RF_D0_0LG.v BB8_nbr_A0_0RF_D0_1RC.v
  BB8_nbr_D0_0LG_H0_1LA.v BB8_nbr_D0_1LG_G1_0RC.v`

## Open questions

- None for the six verdicts.
- The R3big region (k > halting boundary) and machine 6's LOOP with a run of exactly 3 are provably never reached.
  They were not characterized.
