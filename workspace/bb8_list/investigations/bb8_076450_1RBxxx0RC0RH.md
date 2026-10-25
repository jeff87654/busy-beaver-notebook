# BB(8) holdout, subtask 76450: `1RB---_0RC0RH_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LA1LF_1RB1RH`

Source: holdout of BB(8) subtask 76450 (mxdys enumerator @ a41db6c); the mxdys NG/RWL/CPS pre-filter could not
decide it. Pipeline growth at 2 / 10 / 40 CPU-s was 6,905 / 14,684 / 26,701 digits at 1,885 / 2,531 / 3,529 loops
(3.66 -> 5.80 -> 7.57 digits per loop), stopped at the time limit. The undefined (halting) transition is A1.

## Verdict

**The machine never halts. It is an already-proved machine with two state names swapped, not a new halter.**

Swap the state names A and H:
- This machine becomes `1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LH1LF_1RB---` exactly.
- That machine is the G0/H0 variant `1LH1LF_1RB---` of `1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---`.
  It was already proved non-halting (`proofs/BB8_76450_1RB1RA_G0_1LH_H0_1RB.v`, investigation
  `bb8_076450_1RB1RA0RC0RA.md`).

After the swap, the only remaining difference is the start state. This machine starts in its A, which is the
variant's H. The variant starts in its own A. Both states have the 0-transition `1RB`, so both machines write 1,
move right and enter B on the first step. From then on the two runs are identical, step for step.

Consequences:
- The "different" halting transition A1 is the variant's H1 under the swap, so the halting condition is the same.
  - The machine halts only if a reset finds exactly k = 4b+1 trailing zero digits: phases E1, G0 (`1LA`), then A
    reads 1.
  - Lemma `EX` excludes this, because b > k at every reset.
- This is not an Ackermann-level halter. It has no sigma and is irrelevant to the 2↑¹¹2↑¹¹3 bar.

**Confidence: proved (Coq PASS).**
- `bb8_list/proofs/BB8_76450_1RBxxx_0RC0RH.v` proves `Theorem nonhalt : ~ halts tm c0.` (busycoq, Individual82,
  Coq 8.20.1, compiles in about 21 s).
- `python check.py BB8_76450_1RBxxx_0RC0RH.v` gives (`bb8_076450_1RBxxx0RC0RH/check_py.out`):
  `PASS BB8_76450_1RBxxx_0RC0RH.v: 1RB---_0RC0RH_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LA1LF_1RB1RH never halts (machine-checked, no axioms)`.
- The proof is self-contained: Coq re-checks every lemma against this machine's own `tm` table, including the 50
  literal steps from the blank tape. It does not import the variant's proof.

## Evidence for the relabeling

| check | result | file |
| --- | --- | --- |
| text: swapping A and H in the machine string gives the variant string | equal | `lockstep_out.txt` |
| lockstep literal run of both machines from the blank tape: symbol written, move, (relabeled) state at each step | 10⁹ steps, 0 mismatches | `lockstep_out.txt` |
| Quick_Sim `--recursive --max-loops=1500` on both machines | identical output (13 rules, same step counts, same final tape) | `qs1500_M.txt`, `qs1500_V.txt` |
| family successor check on this machine's own literal run (`trajectory.js` with `TM=` this machine) | 10 family configurations in 3·10⁹ steps, 0 mismatches | `trajectory_blank.txt` |

Transition usage in the first 10⁹ steps:
- A1 is never used.
- A0 is used twice: the first step, and once after G0 during the initial segment.
- The bulk is D1, E0, F1 and H1: about 2.5·10⁸ each.

## Configuration family and rules (inherited, proved in the Coq file)

`K(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 1 B> 0^inf`; in Coq, `Kc` stores the digits last-first. The
phase lemmas are the variant's, with transfer state A renamed H: TR1, TR2, ENTRY, LOOP, FINAL, END4b.

| rule | statement |
| --- | --- |
| R1 (a ≥ 1) | K(ds; a; b) -> K(ds; a-1; 4b+4) |
| R2 (k = 0 trailing zero digits) | K(.., x+1; 0; b) -> K(.., x; 4b+3; 1) |
| R3 (1 ≤ k ≤ 4b) | K(.., y+1, 0^k; 0; b) -> K(.., y, 4b+3-k, 1^(k-1); 1; 1) |
| R4 (no digits) | K(; 0; b) -> K(1^(4b+2); 1; 1) |
| halt (k = 4b+1) | reaches A1 (never happens: `EX` gives b > k at every reset) |

Literal checks: the earlier investigation checked each rule on the variant `1LH1LF_1RB---` by exact simulation
(`bb8_076450_1RB1RA0RC0RA/check_rules_1LH1LF_1RB.json`). Under the swap those checks transfer to this machine, and
the lockstep run confirms the swap literally.

## Orbit (for completeness)

The steps below are exact, from `trajectory_blank.txt`:
- step 50: K(1,1; 1; 1)
- step 130: K(1,1; 0; 8)
- step 1,139: K(1,0; 35; 1)
- step 779,708,697: K(1,0; 28; 38228)

After that, symbolically:
- K(1,0; 0; b35), with b35 = (7·4^35−4)/3 = 2,754,713,781,673,959,707,988.
- R3 gives K(D; 1; 1), with D = 4·b35+2 ≈ 1.1·10²².
- Then K(D−2; a0; 1), with a0 = 4·b35+3.

Quick_Sim at 1,500 loops shows the digit run 1^(D−2) and the a-run a0 − 3,767. So Quick_Sim is still counting down
a0 ≈ 1.1·10²². The 3.7 -> 7.6 digits per loop come from fused ×4 R1 steps, not from halting.

## Record comparison

The machine never halts, so it has no score. It is a trivial variant of a known machine: a relabeling of the proved
`1RB1RA_..._1LH1LF_1RB---`, with an equivalent start state.

## Reproduction

In `bb8_list\investigations\bb8_076450_1RBxxx0RC0RH` (`python` = `..\..\..\third_party\venv311\Scripts\python.exe`):
- `node lockstep.js 1000000000`: relabeling check plus lockstep literal run (about 4 min; `lockstep_out.txt`).
- `TM=1RB---_0RC0RH_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LA1LF_1RB1RH node ../bb8_076450_1RB1RA0RC0RA/trajectory.js 3000000000`
  writes `trajectory_blank.txt`.
- `python make_proof.py`: writes `..\..\proofs\BB8_76450_1RBxxx_0RC0RH.v` from `BB8_76450_1RB1RA_G0_1LH_H0_1RB.v`.
  It installs the new `tm` table, renames `{{A}}` to `{{H}}` and `cr_AR_1_1` to `cr_HR_1_1`, and updates the
  comments.
- Then, in `..\..\proofs`: `python check.py BB8_76450_1RBxxx_0RC0RH.v` (`check_py.out`).
- Quick_Sim, from `third_party\ligocki\Code`: `python Quick_Sim.py --recursive --max-loops=1500 <TM>`
  (`qs1500_M.txt` / `qs1500_V.txt`).

## Open questions

- None for the verdict.
- Pipeline suggestion (out of scope here): add a dedup step that catches this kind of duplicate.
  - For each state X whose 0-transition equals A0, swap A and X, then compare the result with the machines already
    decided.
  - Such a machine has the same run from the blank tape.
  - Among the other proved variants of `1RB1RA_...`, only `1LH1LF_1RB---` has H0 = A0, so it is the only one with a
    duplicate of this kind.
