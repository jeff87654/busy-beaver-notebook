# BB(8) holdout, subtask 76450: `1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC`

Source: holdout of BB(8) subtask 76450 (mxdys enumerator @ a41db6c). Pipeline growth at 2 / 10 / 40 CPU-s was
9,291 / 17,617 / 32,862 digits at 2,731 / 3,192 / 4,036 loops (3.40 -> 5.52 -> 8.14 digits per loop), still running
at the time limit. The undefined (halting) transition is G0.

## Verdict

**The machine never halts.** It is the same unary doubling counter with reset as the proved machine
`1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC` (`bb8_076450_1RB1LF1RC1RE.md`), from which it differs
only in D1 (`1LD` -> `1RB`) and H0 (`1RA` -> `0LC`). The recurrence is the same (j -> 2j+2 per digit, reset
m' = 6j+7), so the tape grows at a tetration rate (a tower of 2s). It has no sigma, so it is **not a BB(8) record
candidate** and is irrelevant to the 2↑¹¹2↑¹¹3 bar.

**Confidence: proved (Coq PASS).**
- `bb8_list/proofs/BB8_76450_1RB1LF_0RE1RB.v` proves `Theorem nonhalt : ~ halts tm c0.` (busycoq, Individual82,
  Coq 8.20.1, about 20 s to compile). `python check.py BB8_76450_1RB1LF_0RE1RB.v` prints (`check_py.out`):
  `PASS BB8_76450_1RB1LF_0RE1RB.v: 1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC never halts (machine-checked, no axioms)`.
- **H0 variant** `1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_1LD1LC`: the conclusion carries over (same
  family, same rules, same recurrence; only step counts differ). Also proved:
  `python check.py BB8_76450_1RB1LF_0RE1RB_H0_1LD.v` prints (`check_py_H0_1LD.out`):
  `PASS BB8_76450_1RB1LF_0RE1RB_H0_1LD.v: 1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_1LD1LC never halts (machine-checked, no axioms)`.
- Every rule is also checked by exact literal simulation for both machines (1,324 cases each, 0 failures), and the
  start of both trajectories by a literal run from the blank tape (see below).

## Does the 1RB1LF family and proof adapt?

Yes, after a shift. The old family `0^inf A>0 1^(6j+5) 0 1^m` occurs only once, at step 56 (`A>0 1^11`). Later,
A0 reaches the left end only inside rule R (`ST=0 ALL=1 node fam.js`). The new left-edge state is F, and the counter
length drops by one:

```
W(j, m) = 0^inf F>0 1^(6j+4) 0 1^m 0^inf        ones = 6j + 4 + m
```

The rules have the same shape (P, C, R) and give the same recurrence. The whole proof pipeline of the 1RB1LF
investigation carried over. The planner (`planner8.py`, only the default machine changed), the hand-written
`sweepC6` crawl (C0, D0, E1 are unchanged) and the proof generator (`gen_coq.py`, new phase statements and templates)
all worked. The three generated crossing lemmas are the same as before: A and F over 111111, and H over
111111 -> 001001. Both files compiled on the first attempt.

## Rules

Cell-level rules (r is an arbitrary right context that is never visited, unless stated otherwise). Steps are
given for the main machine / the H0 variant:

| rule | statement | steps (main / H0 var.) | literal check (each machine) | Coq |
| --- | --- | --- | --- | --- |
| P (n = 2p+1, p >= 1) | F>0 1^n 0 0 r -> F>0 1^(n+5) r | 4n+19 / 4n+21 | 447/447 | `P6` (n = 6i+5) |
| R (n = 2p, p >= 1) | F>0 1^n 0 0 r -> F>0 1^4 0 1^(n+3) r | 4n+34 / 4n+38 | 447/447 | `R6` (n = 6j+4, r = 0^inf) |
| C (n = 6j+4, j >= 0) | F>0 1^n 0 1 r -> F>0 1^5 (001)^(2j+1) 0 0 0 r | 4n+29 / 4n+33 | 150/150 | `C6` |

Family rules (checked by running from W(j,m) to the first later W configuration):

| rule | statement | steps (main; H0 variant) | literal check (each machine) | Coq |
| --- | --- | --- | --- | --- |
| Wstep (j, m >= 0) | W(j, m+1) -> W(2j+2, m) | (24j+45) + (2j+2)(24j+51); (24j+49) + (2j+2)(24j+53) | 240/240 (j < 40, m < 6) | `Wstep` (-->+) |
| Wreset (j >= 0) | W(j, 0) -> W(0, 6j+7) | 24j + 50; 24j + 54 | 40/40 (j < 40) | `Wreset` (-->+) |

- Wstep is C, then P once per (001) block (2j+1 times: 1^(6i+5) 0 0 1 -> 1^(6i+11)), then P once more on
  1^(12j+11) 0 0 0, which leaves 1^(12j+16) 0 = 1^(6(2j+2)+4) 0. Wreset is R with n = 6j+4.
- The literal checks (`check_rules.py`, outputs `check_rules_out.txt` / `check_rules_H0_1LD_out.txt` and the JSON
  files) run with no acceleration to the next left-edge F0 configuration, compare the exact tape, and require that
  no cell of r was visited (cell rules: 3 contexts each, empty and two random). `fit_steps.py` checks all 628
  recorded step counts per machine against the closed forms above: 0 mismatches (`fit_steps.out`).
- P with n = 1 gives F>0 1^4 0 r instead, so it is excluded (never used: P only acts on n = 6i+5).
- Other residues are not needed. From F>0 1^n 0 1 with n ≡ 0, 2, 3, 5 (mod 6) the machine halts at G0 (`probe.py`),
  and n ≡ 1 (mod 6) gives a different word. The counter length 6j+4 never has these residues, because P only
  ever acts on lengths 6i+5 and adds 6 per block, plus 5 at the end.

**Mechanism** (`trace.py`). Every rule starts with F0 G1 H0 C0 D0 E0 A0 B1 E1 C1 G1 H1 C0 D1 B0. This rebuilds the
left end and is the only place D1 is used. Then the C0 D0 E1 cycle crawls right, turning `C> 0 0 1` into `1 C> 0 0`,
and the turn at the end of the run decides the rule:
- `0 0` after an odd run (P): C0 D0 E0 A0 B1 E0, then the A1/F1 pair sweeps left and ends as F0 at the left end.
- `0 0` after an even run (R, here only at the tape end): the A1/F1 sweep ends as A0 instead. Then A0 B1 E1 C1 G1 H0 ...
  rebuilds the left end as `1^4 0` and ends as F0.
- `0 1` (C): the turn ends in the leftward H1 C1 G1 sweep, which rewrites every 111 as 001. For length 6j+4 it
  reaches the left end in state H, then H0 C0 D0 E0 A0 B1 E0 A1 F1 A1 ends as F0. For other residues, G reads a
  blank and halts.

**Why the H0 variant behaves the same.** H0 is only ever used at the left end, with a blank cell to its left.
There `H0 = 0LC` runs H0 C0 D0 into state E, one cell right of the H0 cell. With `H0 = 1LD`, H0 D0 E1 C0 D0 reaches
the same tape and state two steps later. This is why each variant rule count is +2 per H0 use: P +2, C +4, R +4.
The Coq proof of the variant does not rely on this argument; it is generated and checked independently.

## Recurrence

From W(0, M) the tail is consumed one cell per Wstep, and j follows j -> 2j+2, so j_t = 2^(t+1) − 2. After M steps
Wreset gives

```
W(0, M) ->* W(2^(M+1) − 2, 0) -> W(0, M'),    M' = 6(2^(M+1) − 2) + 7 = 12·2^M − 5.
```

The blank tape reaches W(0,9) at step 71 (H0 variant: step 75). So M0 = 9, M1 = 12·2^9 − 5 = 6139, and
M2 = 12·2^6139 − 5 ≈ 1.266·10^1849. Then M3 ≈ 10^(10^1848.6), M4 ≈ 10^10^10^1848.6, and so on: a tower of 2s
(`sizes.out`). Every W configuration has exactly one successor in the family, so the machine never halts. G0 is
never reached, and all 15 defined transitions are used (`usage_out.txt`, `usage_H0_1LD_out.txt`).

**Literal trajectories** (`node trajectory.js 5000000000`, no acceleration, `trajectory_blank.txt`; with
`TM=..._1LD1LC` for the variant, `trajectory_blank_H0_1LD.txt`). The script finds every W configuration and checks
that each is the predicted successor of the previous one, after exactly the predicted number of steps.
- Main: 24 W configurations in 5·10^9 steps, 0 mismatches. They run from W(0,9) at step 71 through the first reset
  (W(1022,0) at step 16,758,746 -> W(0,6139) at step 16,783,324) up to W(16382,6126) at step 4,311,455,563.
- H0 variant: 24 W configurations, 0 mismatches. They run from W(0,9) at step 75 through W(1022,0) at step 16,762,838
  -> W(0,6139) at step 16,787,420, up to W(16382,6126) at step 4,311,525,187.
- `h0check.js` (`h0check.out`): in the first 2·10^8 steps of each machine, all 9,252 uses of H0 happen at the left
  end of the word, as the variant argument above requires.

## Pipeline growth data

At 2000 loops Quick_Sim (`qs_prover2000.txt`, `--recursive --max-loops=2000 --verbose-prover`, 0.6 s) is at the
start of the phase that begins at W(0, M2). Its tail is `111111^(~10^^2.5)`, which has 1,850 digits, about M2/6
six-cell blocks. Its `Iterated Rule 13` is `111111^x ... 111111^y -> 111111^(64x+378) ... 111111^(y−1)`. That is
the same fused rule as in the 1RB1LF machine: six Wsteps (×2 each) become ×64, with a cap of 10·log10(64) ≈ 18
digits per loop. The observed 8.14 digits per loop is fused doubling, not super-exponential growth. The 32,862
digits at 40 CPU-s correspond to about 1.1·10^5 of the ≈1.3·10^1849 Wsteps in that phase (`sizes.out`).

## Record comparison

The machine never halts, so it has no score and cannot matter for 2↑¹¹2↑¹¹3. It is a close relative of the
proved `1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC`: same counter, same recurrence, with the
left-edge state and counter length shifted (F and 6j+4 instead of A and 6j+5) and M0 = 9 instead of 3. It is not a
trivial variant in the unused-transition sense, because D1 and H0 are both used in every rule. The H0 variant
`..._1LD1LC` is a trivial variant of this machine in the sense shown above: identical up to two extra steps per H0 use.

## Formal proof

`bb8_list/proofs/BB8_76450_1RB1LF_0RE1RB.v` and `BB8_76450_1RB1LF_0RE1RB_H0_1LD.v` (copies in `coq/`), generated by
`gen_coq.py` from `coq_head.v.in` and `coq_tail.v.in` (variant: `TM=<variant> python gen_coq.py <out>`):
- `sweepC6`: the hand-written rightward C0 D0 E1 crawl over (111111)^n (unchanged from 1RB1LF).
- Three generated crossing lemmas: A and F over 111111 (the A1/F1 sweep), and H over 111111 -> 001001.
- Phase lemmas `P6`, `C6` (-->+), `R6` (-->+), with planner scripts from `planner8.py` and the phase definitions
  in `explore.py`.
- Tape identities `six_S`, `zo2`, `ones6`, `ones_add`; `Piter` (P once per (001) block, by induction).
- `Wstep`, `Wreset`, `init_reach` (71 literal steps to W 0 9; the variant takes 75), and `nonhalt` via
  `multistep_nonhalt` and `progress_nonhalt_simple` on `Wc (j, m) = W j m`, with no side condition.

## Reproduction

In `bb8_list\investigations\bb8_076450_1RB1LF1RC1RE_0RE1RB` (`python` = `..\..\..\third_party\venv311\Scripts\python.exe`):
- `python check_rules.py --out check_rules.json` and
  `python check_rules.py --tm 1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_1LD1LC --out check_rules_H0_1LD.json`:
  literal rule checks.
- `python fit_steps.py check_rules.json`, `python fit_steps.py check_rules_H0_1LD.json`: step-count closed forms.
- `node trajectory.js 5000000000` (optionally with `TM=` the variant): literal trajectory from the blank tape.
  `node fam.js N` is the earlier exploratory version.
- `python sizes.py`: recurrence values and magnitudes. `python usage.py 300000`: transition usage.
- `python gen_coq.py coq\BB8_76450_1RB1LF_0RE1RB.v` (and with `TM=` the variant), then copy to `..\..\proofs\` and run
  `python check.py <File.v>` there. `coqc_scratch.py` compiles one file with the same load paths.
- `node h0check.js 200000000` (optionally with `TM=` the variant): H0 is only used at the left end.
- Exploration: `edges.py` (left-edge events), `probe.py` (rule discovery), `trace.py` (step traces),
  `explore.py P6 C6 R6` (planner runs).
- Quick_Sim: from `third_party\ligocki\Code`, `python Quick_Sim.py --recursive --max-loops=2000 --verbose-prover <TM>`
  (`qs_prover2000.txt`).

## Open questions

- None for the verdict, for either machine.
