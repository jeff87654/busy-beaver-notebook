# BB(8) holdout, job 193804 (dl2_hits.tsv line 22): `1RB0RH_1RC1LE_0LD0RF_---1RE_1LB0LB_1RA0RG_0LC1RF_0LG1LA`

## Verdict
**Never halts. Confidence: proved (Coq PASS).** Not a record candidate (it never halts).
- `bb8_list/proofs/BB8_193804_1RB0RH_1RC1LE.v`; `python check.py BB8_193804_1RB0RH_1RC1LE.v` prints
  `PASS ... never halts (machine-checked, no axioms)` (compile ~46 s; row added to the proofs README).
- The only undefined transition is D0. It is never reached: the family below is closed under its rules and no step of
  any rule reads D0.
- It is a **genuine counter, not a disguised cycler or bouncer**: a digit-list counter with an additive step and an
  Ackermann-style hierarchy, but with **no halting boundary** (the NOBOUNDARY label is correct). Tape width is only
  13,064 at 1e8 steps because the run sits in the first level of the hierarchy (bottom digit 52 -> 47 after 6e6 literal steps).

## Configuration family and rules
Head B at the left end, blank to the left. With W = [w1;...;wk] (digit value = block length - 1) and m >= 0:

`Cfg m W = 0^inf B> 0 0 1^(4m+1) 0 1^(w1+1) 0 1^(w2+1) ... 0 1^(wk+1) 0 1 0^inf`

Macro rules (each `c -->+ c'`, proved in Coq for ALL m, j, y, W; R1 costs 24m+37 literal steps, R3/R4 cost O(m*j)):

| rule | statement |
| --- | --- |
| R1 | `Cfg m (S w :: W) -->+ Cfg (S m) (w :: W)` (b -> b+4 per unit of the first digit) |
| R3 | `Cfg m (0^(j+1) ++ S y :: W) -->+ Cfg 0 (0^j ++ (4m+4) :: y :: W)` (the last zero before the first nonzero digit gets 4m+4, that digit is decremented, m resets to 0) |
| R4 | `Cfg m (0^(k+1)) -->+ Cfg 0 (0^(k+1) ++ [4m+4])` (used-up list: a new bottom digit 4m+4 is appended) |
| R4e | `Cfg m [] -->+ Cfg 0 [4m+4]` |

Every (m, W) falls under exactly one rule (`split_zeros`), so `step_total : forall m W, exists m' W', Cfg m W -->+ Cfg m' W'`.
Digits stay >= 0 (R3 decrements a successor, the new digit is 4m+4 >= 4), so no zero-length block (the only thing that makes
D0 readable; e.g. literal probes with a block of length 0 do halt) ever appears. The start-up is literal: `c0 -->* Cfg 2 []`
in 98 steps (X(9; []) at step 98).

Structure of the hierarchy (by inspection of the rules, not formalised): after the first digit w1 is used up, R3 with one
zero maps w1 -> 4*w1+4 per unit of w2 (exponential); with two zeros the digit w2 := 4m+4 with m ~ the previous w1
(tower per unit of w3); R4 adds a new level at the bottom. Hence Ackermann-type growth, but R4 always rebuilds, so
(unlike the BB(7) champion and the 1RB1RA parent) the list never halts.

## Machine-level lemmas (planner8.drive, symbolic runs; Coq checks every one)
Crossing lemmas `cr_GR_1111_0101`, `cr_EL_0101_1111`, `cr_EL_1010_1111`, `cr_FR_1111_1010`, `cr_BL_1010_1111` (a block of
four 1s/0s rewritten while the head crosses it) and pipeline lemmas `pp_BL_11_01_c0101`, `pp_BL_1010_1111_c1111`
(reservoir `1 (11)^c` left of the head unwound to `(01)^c`).
- R1m (37 literal steps), ENT3/ENT4 (17), EMP4 (71).
- Zero-skipping cycles: the head carries a reservoir `1 (11)^c` on its left; `CYC3`/`CYC4` (28 steps) do one double sweep
  over the 1^(4m+3) block and consume one `(01)` zero block: `OddT c m (S i) T -->+ OddT (S c) m i T`, iterated by `iter`;
  `FIN3` (22) / `FIN4` (56) unwind the reservoir and write the 4m+4 block. T = tail `0 1 1 1^y 0 r` (R3) or `0 1 0^inf` (R4).
- Glue (hand-written, `head_dl.v.in`): `enc`, `Cfg`, `enc_zeros`, `ones4`, R1/R3/R4/R4e, `step_total`, `nonhalt`
  (`progress_nonhalt_simple` over `nat * list nat`).

## Verification
- Rule fit from literal probes of random family members: `rules.py` compares R1/R3/R4 with the literal successor of 1,364
  configurations (beta = 0,4,8,12; lists up to length 4 with digits 0..3): 0 mismatches (`fam.py` = probe tool).
- Literal run from the blank tape: `orbit_check.py` (6e6 steps, 1,078 round starts): every round start parses into the
  family and equals the abstract successor, 0 mismatches.
- Coq: all machine-level lemmas, the induction over zero blocks, the closure and the start-up are proved; `Print Assumptions`
  closed (check.py).

## Reproduction (`python` = `third_party\venv311\Scripts\python.exe`, in this folder, run at Idle priority)
- `python gen_dl.py OUT.v` regenerates the proof (planner8.py, pipe.py, coqgen_util.py are copies of the neighbors_family_tools
  and bb8_193804_1RB0RH0LC1LF versions); copy to `proofs\BB8_193804_1RB0RH_1RC1LE.v`; `python check.py BB8_193804_1RB0RH_1RC1LE.v`.
- `python rules.py`, `python orbit_check.py 6000000`, `python abstract.py N` (abstract orbit), `node fastsim.js 100000000`.
- `fam8*.py` are the planner family definitions (X, Odd, final targets); `generated_BB8_193804_1RB0RH_1RC1LE.v` is the generated file.

## Notes for the pipeline
- The dlscan2 fit (`d=1d+0, b=2b+1`, R1 `1b+2`) is in a different parametrisation (units of the `10` separator); the real
  structure is above. The row is a true digit-list family (additive step, zero-run borrowing, bottom rebuild), but of the
  "R4 always rebuilds" kind, which the proof shows can never reach D0. Other NOBOUNDARY rows of this shape
  (`R4 KKKKK` in dlscan2 = rebuilds for every grid point) can use `gen_dl.py` with different constants.
