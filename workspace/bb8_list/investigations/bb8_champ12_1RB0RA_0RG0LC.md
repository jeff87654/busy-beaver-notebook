# BB(8) champion-rule rebuild machines (BB(7)-champion 12-transition TNF subtree)

Primary : `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE`
Variant : `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE`
Source: holdouts of the 8-state TNF subtree below the BB(7) champion's first 12 transitions (`estimate_20260926/champion_neighborhood/holdouts_12.txt`).
Scratch dir: `bb8_list\investigations\bb8_champ12_1RB0RA_0RG0LC\`.

## Verdict (both machines)

**Never halts: strong evidence, NOT proved (no Coq PASS).** Both machines run the same counter from the blank tape and are
indistinguishable on every configuration probed. No halting transition (H0) is ever read. Not a record candidate: an unbounded
digit-list counter with a rebuild, Ackermann / f_omega-type growth, no sigma, nothing near 2^^11 2^^11 3.
Proof status: partial Coq files exist (`proofs\BB8_champ12_1RB0RA.v`, `..._v2.v`). Both compile. They contain only the doubling-pass lemma
and generated crossing lemmas and NO `nonhalt` theorem, so `check.py` would not PASS them. They are not in the README "Proved" table.

## Answers to the lead's questions

1. **Blank tape reaches the family: yes.** Literal run from the blank tape (own C++ simulator `blank.cpp`, family detector for the template
   R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001): the first family configuration is `K(2,0^10; 0; 0)` at step 2133. The run was continued to
   4*10^9 literal steps for both machines: 28 family configurations, identical trajectories for primary and variant
   (`blank_traj_v1.txt`, `blank_traj_v2.txt`; last `K(1^10,0; 1; 16382)` at step 3.2*10^9, still the first epoch). All 27 consecutive
   configuration pairs equal the rule-level successor (`chk_traj.py`, 0 mismatches).
2. **Where is H0 reached? Nowhere found.** G0 is used: G reads 0, goes to H, and H must read 1 (`1RE` for the primary, `1LE` for the variant).
   Over 10^8 literal steps from the blank tape (primary), G0 fires 9694 times and H always reads 1 (`hstat.cpp`: H0 count 0, H1 count 9694).
   With G0 made undefined, the family probes halt after 24 steps, so G0 is exercised in every rule. Halting needs H on a 0, i.e. a 0 right next to a
   G-on-0 position. That did not occur in any check below, but there is no machine-level proof that it cannot.

## Configuration family and rules (literal-checked for all tested parameters, NOT proved at machine level)

Head in state B on the blank right of the last cell, nothing to the right; tape word (left to right)
`11 (10)^(3 d_1+1) 1 (10)^(3 d_2+1) 1 ... (10)^(3 a+1) 1 (10)^(3 b+2) 111001`. `K(ds; a; b)`, ds farthest-first, zero digits kept.

| rule | statement |
| --- | --- |
| R1 (a >= 1) | K(ds; a; b) -> K(ds; a-1; 2b+2) |
| R2 (a = 0, last digit x+1 >= 1) | K(.., x+1; 0; b) -> K(.., x; 2b+2; 0) |
| R3 (a = 0, k >= 1 trailing zero digits) | K(.., y+1, 0^k; 0; b) -> K(.., y, 2b+2, 0^(k-1); 0; 0) |
| REBUILD (a = 0, all digits zero, n >= 0 of them, any b >= 0) | K(0^n; 0; b) -> K(2, 0^(12b+n+3); 0; 0) |

Step counts are polynomial: REBUILD with n = 0 takes 948, 2856, 5412, 8616 steps for b = 0..3 (about 324 b^2 + 1584 b + 948, plus n(112+48b));
R1 takes 800 steps for K(;1;2), 464 for K(;1;1), 200 for K(;1;0).

Verification (`probe2.exe` from `neighbors\`; wrappers `grid.py MACH`, `grid2.py MACH SEED`; both machines):
- `grid.py`: 3573 configurations (a <= 2, b <= 6, up to 3 digits 0-3, deep zero tails k <= 12 with b <= 8, all-zero lists n <= 13 with b <= 11):
  0 mismatches, 0 halts, 0 timeouts, for primary and variant.
- `grid2.py` (random lists up to 6 digits 0-5, a up to 5, b up to 14; all-zero lists n up to 63; k up to 30): 1662 configurations per seed,
  0 mismatches, 0 halts, both machines.
- REBUILD holds for b = 0 and n = 0 (empty list): `K(;0;0) -> K(2,0,0,0;0;0)`.

There is no halting case at all (unlike the champion, where K(0^n;0;b) halts at E0). **Abstract non-halting argument (paper):** if R1-R3 and
REBUILD hold for all parameters, every K(ds; a; b) has a successor, the family is closed, and the blank tape enters it, so the machine never
halts. No invariant on the parameters is needed. The open part is only the machine-level proof of the four rules.

## Why the Coq proof is not finished (precise gap)

Machine-level structure (from `trace2.py` and the planner):
- R1 is a quadratic doubling process. State F sits at the left end of the left run. One pass (called IT) consumes one `10` unit of the left run
  and grows the right run by 2 units: `(1 0 1 [0 1]^k l) F> 0 (10)^m CTX -->+ (1 [0 1]^k l) F> 0 (10)^(m+2) CTX` with CTX = `0101101`. It costs 40
  literal steps plus two crossings (G going right over the run, B going left over it). IT is proved in Coq (compiled, planner generated).
- After the first stage the right tail CTX is changed by the passes (it becomes `0101101101`, then `0101100101`), so IT occurs in several
  variants with different CTX. Between them the head shuttles the long run with A/B/D passes that shift it by one cell ("mode 2" crossings,
  below). Then the separator and prefix cells are met, 3 a-units are consumed, and the head returns to B.
- R2, R3 and REBUILD repeat this once per zero digit (R3 keeps k-1 zeros, REBUILD handles n zeros and a b-dependent run), so they are nested
  loops. My estimate is 25-40 planner phases plus 6-8 hand-written loop lemmas.

Tools built (reusable, in the scratch dir):
- `planner8.py` is the 884431 planner plus a new **mode 2 crossing** (`derive_crossing2`): the cells next to the head stay adjacent to it and the
  converted block is inserted behind them (`ctx l {{q}}> xs^^n *> r -->* ctx ys^^n *> l {{q}}> r`). The old planner failed on exactly these cases
  ("context changed"). `coqgen_util.py` generates their proofs; `cx_AR_01_01_c0` compiled.
- `phc.py` (configs to Coq statements, with extra equations for fresh counter variables), `genc.py` and `scr2coq.py` (lemma text),
  `matchers.py` (anytime matcher `m_LN1` for the pass loop; needs a hand-written loop lemma over IT, drafted in `hand1.v.in`),
  `t_r1*.py` (planner drives of R1; they run through ENTRY, two loop applications and many crossings).
- Convention: planner mode `>` with `R = [BLANK]` is the family; the b-run is `[0,1]^n` in the left stream (nearest first); SUF = `1,0,0,1,1,1`.
- Lessons: (1) do not match the pass loop on a run with a fixed CTX. CTX changes, and the first automatic attempt matched a spurious second
  loop on the transported run. Make CTX a parameter of IT, or prove a tail-independent core. (2) Use 3-unit blocks `[0;1;0;1;0;1]` or single
  units; a coefficient on a run count makes the planner emit the wrong number of `follow`s.

## Comparison with known machines

Same engine as the BB(7) champion (Ligocki's B(a; b1..bk) counter; the same template and rules R1-R3 that dlscan2 infers), with the champion's halt
at the exhausted list replaced by a **rebuild into a list about 12b+n+3 long** (E0 = 0RG instead of halting, G0 = 0LH / 0RH, new state H). Each
epoch reruns the champion's whole recurrence on a longer list, so growth is Ackermann / f_omega level and there is no halt. Compare
`bb8_884431_1RB1LG0RC0LB.md` (same idea, additive refill) and `bb9_champion_1RB1RA0LC0LF.md`.

## Reproduction (python = `third_party\venv311\Scripts\python.exe`; C++ tools need `C:\msys64\ucrt64\bin` on PATH)

- Blank tape: `g++ -O2 -std=c++17 -o blank.exe blank.cpp`, `blank.exe MACHINE 4000000000 > blank_traj.txt` (about 30 s), then `python chk_traj.py`.
- Rule grids: `python grid.py 1`, `python grid.py 2`, `python grid2.py 1 7`, `python grid2.py 2 8`.
- G0/H statistics: `g++ -O2 -o hstat.exe hstat.cpp`, `hstat.exe MACHINE 100000000`.
- Traces: `python trace2.py "[]" 1 2 800` (R1 on K(;1;2)), `python trace.py "[]" 1 0 80`.
- Partial proof: `python mkpartial.py 1 ..\..\proofs\BB8_champ12_1RB0RA.v`, then `python build.py BB8_champ12_1RB0RA.v` in `proofs` (16 s).

## Open questions (for an Opus continuation)

1. Machine-level proofs of R1, R2, R3 (all k) and REBUILD (all n, b) for the actual machines. Then the glue: every K has a successor, the
   blank tape reaches K(2,0^10;0;0) in 2133 literal steps, and `multistep_nonhalt` with `progress_nonhalt_cond`. Variant 2 should follow with the
   same generator (only the G0/H steps differ; IT has 5 ops instead of 7).
2. Make CTX a parameter of IT, then drive R1 (ENTRY, middle, exit), then R2 (single list digit), then the zero loops for R3 and REBUILD.
