# Neighbors of the digit-list counter: the F1 family (F1: 0RD -> 1LF)

Parent: `1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---`, proved non-halting in
`proofs/BB8_76450_1RB1RA.v` (report `bb8_076450_1RB1RA0RC0RA.md`).
Family: the 12 unresolved one- and two-transition neighbors listed in `bb8_list/neighbors/family_F1.txt`.
Each has F1 = 1LF, plus possibly one change in E0, D0, A0 or H0.

## Verdict

**All 12 machines never halt. Confidence: proved (Coq PASS) for all 12.** None of them halts, so none has a sigma and
none bears on the BB(8) record bar 2↑¹¹2↑¹¹3.

- The 11 machines with A0 = 1RB keep the parent's configuration family and rule shapes. The only new parameter is a
  **transfer factor m** ∈ {4, 3, 2}, the number of 1s that each 1 of b becomes (the parent has m = 4).
- The A0 combination `0RF1RA_...` is the same kind of counter in a mirrored shape: the configurations end in state F,
  and b grows additively (b -> b+3).
- **Key question (can the halting transition be reached, especially after a rebuild?): no.**
  - In every machine, each reset with k ≥ 1 trailing zero digits has b ≥ k+1.
  - Halting needs k = mb + m − 3 (at least 2b+1), or k = b+1 in the A0 case.
  - A rebuild always produces a list of nonzero digits. Clearing any such list keeps b ≥ k+1 (Coq lemmas `GEN`/`CLR`),
    so the rebuild restarts the same cycle.

| machine | changes | 10 s score | class | verdict | confidence | proof file (`bb8_list/proofs/`) |
| --- | --- | --- | --- | --- | --- | --- |
| `1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB1LF_0LH1LF_1RF---` | F1:1LF (core) | 15,213 | m = 4 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF.v` |
| `1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB1LF_0LH1LF_1LA---` | F1:1LF H0:1LA (H0 twin) | 15,177 | m = 4 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_H0_1LA.v` |
| `1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LG0LG_1LB1LF_0LH1LF_1RF---` | E0:1LG F1:1LF | 15,803 | m = 4 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_E0_1LG.v` |
| `1RB1RA_0RC0RA_0LD1RC_1RE1LE_0LG0LG_1LB1LF_0LH1LF_1RF---` | E0:0LG F1:1LF | 13,984 | m = 3 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_E0_0LG.v` |
| `1RB1RA_0RC0RA_0LD1RC_1RE1LE_0LF0LG_1LB1LF_0LH1LF_1RF---` | E0:0LF F1:1LF | 13,393 | m = 3 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_E0_0LF.v` |
| `1RB1RA_0RC0RA_0LD1RC_1RE1LE_0LE0LG_1LB1LF_0LH1LF_1RF---` | E0:0LE F1:1LF | 11,478 | m = 2 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_E0_0LE.v` |
| `1RB1RA_0RC0RA_0LD1RC_0RF1LE_1LF0LG_1LB1LF_0LH1LF_1RF---` | D0:0RF F1:1LF | 15,599 | m = 4 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_D0_0RF.v` |
| `1RB1RA_0RC0RA_0LD1RC_1LG1LE_1LF0LG_1LB1LF_0LH1LF_1RF---` | D0:1LG F1:1LF | 13,545 | m = 3 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_D0_1LG.v` |
| `1RB1RA_0RC0RA_0LD1RC_1LF1LE_1LF0LG_1LB1LF_0LH1LF_1RF---` | D0:1LF F1:1LF | 12,992 | m = 3 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_D0_1LF.v` |
| `1RB1RA_0RC0RA_0LD1RC_0LG1LE_1LF0LG_1LB1LF_0LH1LF_1RF---` | D0:0LG F1:1LF | 10,749 | m = 2 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_D0_0LG.v` |
| `1RB1RA_0RC0RA_0LD1RC_0LF1LE_1LF0LG_1LB1LF_0LH1LF_1RF---` | D0:0LF F1:1LF | 10,611 | m = 2 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_D0_0LF.v` |
| `0RF1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB1LF_0LH1LF_1RF---` | A0:0RF F1:1LF | 13,641 | F-shape, +3 | never halts | proved (Coq PASS) | `BB8_nbr_F1_1LF_A0_0RF.v` |

The `check.py` output for all 12 files is in `neighbors_F1/check_py.out`:
`PASS <file>: <machine> never halts (machine-checked, no axioms)`. Each file compiles in 13-17 s.

## What F1 = 1LF changes (the core machine)

In the parent, F1 = 0RD is used in one place only: F moving left over a run of 1s.
- The parent does this in three steps per cell: F1 0RD, D1 1LE, E0 1LF.
- With F1 = 1LF, F crosses the run in one step per cell (`cr_FL_1_1`), with the same net effect on the tape.
- The planner re-derives every parent phase (TR1, TR2, ENTRY, LOOP, FINAL, END4b) with **identical statements**.
  Only the F crossing lemma and the literal step counts change.

The consequences for the core machine:
- **R1-R4 are exactly the parent's**, including:
  - the halting boundary k = 4b+1;
  - the unreachable k ≥ 4b+2 form;
  - the rebuild K(;0;b) -> K(2, 1^(4b); 1; 1).
- Starting from the blank tape, it reaches the parent's start K(2;1;1) at step 46 (the parent: step 52), and its whole
  configuration sequence is the parent's.
- Only the step counts change: R1 costs about 4b² steps instead of about 8b². For example, K(1;28;38228) is reached at
  step 389,911,799, against 779,708,699 for the parent.
- D1, E1 and G1 are now used only in resets: 11, 11 and 10 times in the first 2·10⁶ steps, against 498,699 uses of D1
  in the parent (`neighbors_family_tools/usage.py`).

**Why E0 and D0 changes now matter: the transfer factor m.** Because F no longer needs D1/E0 to cross, D0 and E0 are
each used exactly once per transferred 1 (in TR1/TR2), and each can change the number of 1s written.
- The transfer `l 1 0 1^r A> 0^inf -> l 0 1^(r+m) A> 0^inf` goes A0 B0 C0 D0 E0, then F crosses left, then F0 B1, then A
  crosses right.
- Each of A0, D0 and E0 writes one new 1 at the right end, and F0 fills the gap while B1 erases a 1 of b. Hence m = 4.
- The changes:

| change | effect on the right end | m |
| --- | --- | --- |
| E0 = 1LG (then G1 1LF) | the same three 1s | 4 |
| D0 = 0RF | a detour (F0 1LB, B0, C1, C0, D1, E0) still leaves three 1s | 4 |
| E0 = 0LG or 0LF | E writes 0 | 3 |
| D0 = 1LG or 1LF | D writes 1 and skips E | 3 |
| E0 = 0LE | E writes 0, then E1 0LG erases the D cell | 2 |
| D0 = 0LG or 0LF | D writes 0 and skips E | 2 |

In the parent (F1 = 0RD), E0 is part of every F crossing, so E0 changes break the crossing. That is why such
neighbors are not simple rule variants there.

## Configuration family and rules (the 11 machines with A0 = 1RB)

The configuration family is the parent's:

`K(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 1 B> 0^inf`

In Coq it is `Kc ds a b`, with the digits stored last-first. With transfer factor m (b ≥ 1, k = number of trailing zero
digits), the rules are:

| rule | statement |
| --- | --- |
| R1 (a ≥ 1) | K(ds; a; b) -> K(ds; a−1; mb + m) |
| R2 (k = 0) | K(.., x+1; 0; b) -> K(.., x; mb + m − 1; 1) |
| R3 (1 ≤ k ≤ mb + m − 4) | K(.., y+1, 0^k; 0; b) -> K(.., y, mb + m − 1 − k, 1^(k−1); 1; 1) |
| halt (k = mb + m − 3) | E1 G0 H1, as in the parent |
| R4 (no digits) | K(; 0; b) -> K(P, 1^(mb + c4); 1; 1) |

The rebuild prefix P and the constant c4 are:
- m = 4: (2) and c4 = 0; the H0 twin has (5) and c4 = −1, like the parent's `0LH1LF_1LA---` variant.
- m = 3: (2) and c4 = −1.
- m = 2: (2) and c4 = −2.

The halting boundaries are therefore 4b+1, 3b and 2b−1.

**Verification by exact literal simulation.**
- `neighbors_family_tools/kfit.py` reads every constant off literal probes, fitted on b = 1, 2 and confirmed for
  b = 3..5.
- It then compares the fitted rules with the literal successor of each of 1,352 configurations: up to 3 digits (values
  0-3), a = 0-3, b = 1-5, and zero blocks with k up to 4b+4, beyond the halting boundary.
- Result: **0 mismatches for every machine**, including the predicted halts (`neighbors_F1/kfit_all.txt`).
- Literal blank-tape runs of 10⁹ steps per machine (`ktraj.js`) matched the predicted successor at every family
  configuration: 10-38 configurations per machine, **0 mismatches** (`neighbors_F1/traj_all.txt`).

**Why they never halt (general m ≥ 2).** This is the parent's argument with m in place of 4. The Coq lemmas are
`R1iter`, `CH`, `EX`, `IN`, plus two new generic ones, `CLR` and `GEN`.
- **Counting down.** R1 (b -> mb + m) raises b by at least 1. After R2, the refill a = mb + m − 1 ≥ b gives B ≥ b+1.
- **Clearing a block.** Clearing the last j+1 digits (1,…,1,w+1) from a = b = 1 ends with b ≥ w + j + 2 (`EX`). Hence
  every reset that meets k = j+1 zero digits has b ≥ k+1.
- **R3 always applies.** It needs k ≤ mb + m − 4, and b ≥ k+1 gives this for m ≥ 2. Its refill mb + m − 1 − k ≥ b+1
  keeps b growing.
- **No halt.** The halting boundary mb + m − 3 ≥ 2b + 1 is never met.
- **After a rebuild.** `GEN` says that any configuration whose digits are all nonzero, with any a and b ≥ 1, reaches an
  all-zero list, and R4 then rebuilds.
  - The rebuilt list (P, 1^n) and the first configuration from the blank tape both have all digits nonzero.
  - So the cycle `Top B -->+ Top B'` repeats forever. `GEN` replaces the parent's variant-specific `TopZ` and init
    proofs.

## The A0 combination `0RF1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB1LF_0LH1LF_1RF---`

The family is Kf(ds; a; b) = `0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 F> 0^inf` (kfam shape `('F','0')`). The rules,
verified the same way (1,352 grid cases and a 10⁹-step run, 30,132 configurations, 0 mismatches):

| rule | statement |
| --- | --- |
| R1 | K(ds; a+1; b) -> K(ds; a; b+3) |
| R2 | K(.., x+1; 0; b) -> K(.., x; b+1; 2) |
| R3 (1 ≤ k ≤ b) | K(.., y+1, 0^k; 0; b) -> K(.., y, b+1−k, 1^(k−1); 1; 2) |
| halt (k = b+1) | the machine halts: FINAL meets a run of 2, then G0 H1 |
| R4 | K(; 0; b) -> K(1^b; 1; 2) |

- Each unit of the last digit still roughly triples b: R2 sets a = b+1, and then b ends at 3b+5.
- **It never halts.** Clearing (1^j, w+1) from (a, b) = (1, 2) ends with b ≥ w + j + 2, so every reset has b ≥ k+1,
  while halting needs k = b+1.
- The start is K(;1;2) at step 41. R1 gives K(;0;5), and R4 gives K(1^5; 1; 2) at step 207.
- **Mechanism.**
  - The phases are ADD, ENTRY, LOOP (the parent's statement), FINAL1 and END4, all found by the planner.
  - FINAL1 and END4 leave a block `0 1 1 0` left of the head that must walk right through (10) pairs. The planner's
    fixed-context crossings cannot express this, so the hand-written Coq lemma `SHIFT` does it (proved by induction,
    peeling the last pair).
- The proof generator is `gen_kcoq_F0.py`.

## Orbits (no sigma, for orientation only)

- **m = 4 (core, E0:1LG, D0:0RF).** The configuration sequence is identical to the parent's:
  - K(2;1;1) -> K(2;0;8) -> K(1;35;1) -> … -> first rebuild at log10 B ≈ 6.6·10²¹;
  - the first rebuild then has about 10^(6.6·10²¹) digits.
- **H0 twin.** K(;5;1) at step 56 -> K(;0;2388) -> rebuild K(5, 1^9551; 1; 1) at step 115,749,537.
- **m = 3.** K(;2;1) at step 33 (E0 changes) or 31 (D0 changes) -> K(;0;21) -> rebuild K(2, 1^62; 1; 1) at step
  6,667 (E0:0LG).
- **m = 2.** K(2,1,1;1;1) at step 121/129.
- **A0 combination.** K(1^5;1;2) at step 207.

All are Ackermann-type, like the parent: roughly f_(ω+1) in the fast-growing hierarchy. This is irrelevant, since none
halts.

**Pipeline scores.** The 10 s growth scores are ordered by m:
- m = 4: 15.2-15.8k digits;
- m = 3: 13.0-14.0k;
- A0: 13.6k;
- m = 2: 10.6-11.5k.

This is what fused ×m R1 steps give (log10 m digits per step). It is not a sign of halting.

## Reproduction

`python` means `..\..\third_party\venv311\Scripts\python.exe` below; run from the folder named.

In `bb8_list\investigations\neighbors_family_tools`:
- `python kfit.py <TM> --grid` (add `--shape F,0` for the A0 machine) fits the rules and runs the 1,352-case literal
  check, in about 1 s per machine.
- `python kfit.py <TM> --params` prints the fitted rules as JSON (`../neighbors_F1/params.tsv`).
- `node ktraj.js <TM> '<params JSON>' 1000000000 [F 0]` runs the literal blank-tape trajectory with rule checks.
  `../neighbors_F1/run_traj.ps1` runs all 12 at Idle priority (about 2 min, output `traj_all.txt`).
- `python kphases.py <TM> <m>` and `python kphases_F0.py <TM>` show the planner's phase derivations.

In `bb8_list\investigations\neighbors_F1`:
- `sh gen_all.sh` regenerates all 12 proofs into `coq/`. It is deterministic: the output is identical to the files in
  `proofs/`.
- Then copy the files to `bb8_list\proofs\` and run `python check.py <file>` there (`check_py.out`).
- `python ..\neighbors_family_tools\coqc_scratch.py coq\<file>` compiles one file in place.

## Tools written (`bb8_list/investigations/neighbors_family_tools/`)

| file | purpose |
| --- | --- |
| `tmlit.py` | generic exact literal simulator and tape display |
| `kfam.py` | K-family word builder, parser and successor finder, with a switchable shape (`set_shape('F','0')`) |
| `kfit.py` | **fit-then-verify**: reads R1-R4 and the halting boundary from literal probes, prints them, flags the parent's safety conditions, and runs the 1,352-case grid (`--grid`); `--params` gives JSON |
| `kcheck.py` | grid check against the parent's rules with only R4 fitted (superseded by `kfit.py --grid`) |
| `ktraj.js` | fast literal blank-tape trajectory, checking every family configuration against the fitted rules |
| `usage.py` | transition usage counts, with the first and last step of each use |
| `planner8.py`, `coqgen_util.py` | copied unchanged from the parent investigation |
| `kphases.py`, `kphases_F0.py` | planner phase definitions (B-shape with any m; F-shape) with their Coq statements |
| `gen_kcoq.py` + `kcoq_template.v.in` | **Coq proof generator for B-shape machines with any transfer factor m ≥ 2** |
| `gen_kcoq_F0.py` + `kcoq_template_F0.v.in` | the same for F-shape machines with the A0-combination constants |
| `coqc_scratch.py` | compiles one .v file with the project load paths |

- `gen_kcoq.py` checks that the fitted rules are the m-template and fits END4b and the start automatically; the rest
  (`Top`, init, `GEN`/`CLR`) is generic.
- `gen_kcoq_F0.py` refuses machines whose constants differ from the A0 combination's.

## Open questions

- None for the 12 verdicts.
- (Curiosity only.) The k ≥ halting-boundary+1 outcome of R3 exists but is provably never reached.

## Lessons for the D0/A0 families

**Run `kfit.py` first.** It reads the whole rule set off literal probes in about 1 s and grid-checks it.
- I already ran it on the 16 non-F1 unresolved neighbors (`neighbors_F1/kfit_others.txt`,
  `neighbors_F1/kfit_A0_shapeF0.txt`); these are fits only, not proofs.
- **The D0 family (F1 = 0RD) is the same m-template.** D0 is not in the parent's F crossing, so D0 changes only change
  m:
  - D0:0RF gives m = 4. The `..._1RF---` machine has exactly the parent's rules; the `..._1LA---` machine has
    (5, 1^(4b−1)).
  - D0:1LF and D0:1LG give m = 3 (rebuild (2, 1^(3b−1)), or (5, 1^(3b−2)) with H0:1LA, or (4, 1^(3b−2)) with G0:1LH).
  - D0:0LG gives m = 2.
  - Try `gen_kcoq.py <TM> out.v` on each. Where it refuses, the reason is printed. Two known exceptions:
    - `1RB1RA_0RC0RA_0LD1RC_1LG1LE_1LF0LG_1LB0RD_0LH0RC_1RF---` has halting boundary k = 3b−1, not 3b. The template
      requires ch = m−3, but the safety argument still works (resets have k ≤ b−1).
    - `1RB1RA_0RC0RA_0LD1RC_0LG1LE_1LF0LG_1LB0RD_0LH1LF_1LA---` has a rebuild that fits (5, 1^(2b−3)) only for
      b ≥ 2 (K(;0;1) -> K(;5;1)). It needs a small template change, for example R4 for b ≥ 2 only, after checking
      that every rebuild it meets has b ≥ 2.
  - The phases (TR1, TR2, ENTRY, LOOP, FINAL) should re-derive in the planner. If one fails, `kphases.py <TM> <m>`
    shows where.
- **The A0 family is all F-shape (`--shape F,0`).** In all six machines R1 is b -> b+3 and the halting boundary is
  k = b+1. The constants differ:
  - `0RF1RA_0RC0RA_0LD1RC_0LE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---` has exactly the A0 combination's rules, so
    `gen_kcoq_F0.py` should apply directly.
  - The others differ in their constants:
    - `0LG1LE`: R2 gives a = b+2, b = 1; R3 refills b+2−k with a = b = 1; R4 gives (1^(b+1); 1; 1).
    - `0LA1LE`: R2 gives a = b+2, b = 0; R3 refills b+2−k with a = 1, b = 0; R4 gives (1^(b+1); 1; 0).
    - `1LB1LE` and `1RC1LE`: R2 gives a = b+1, b = 3; R3 refills b+2−k with a = 0, b = 3; R4 gives
      (1^(b+1); 0; 3).
  - For them, edit the constants in `kcoq_template_F0.v.in`: the `R2`/`R3`/`Top` statements and the start (a, b) of
    `EX`. The phases FINAL1/END4 and `SHIFT` may need new targets; the planner prints where it gets stuck.
  - When R3 leaves a = 0 (the b = 3 variants), a reset follows immediately. Re-check that b ≥ k+1 still holds before
    writing Coq.
- **What to skip.**
  - Do not hand-trace rules: `kfit.py` plus the grid is faster and exact.
  - Do not re-run Quick_Sim: the pipeline scores just reflect m.
  - Do not write variant-specific clearing proofs: `GEN`/`CLR` in the templates cover any all-nonzero digit list.
- **Pitfalls.**
  - The K-shape parser needs everything right of the head to be blank. The version in `kfam.py` checks this; an
    earlier version that checked only the visited range missed configurations.
  - The planner cannot express "a fixed block walks through a run" (see `SHIFT`); write such lemmas by hand, in the
    order: induction, `lpow_shift'`, `follow IHn`, `execute`.
  - Probe END4-type phases from the exact start `0^inf 1 1 C> 0 (10)^i`, not from a padded word.
