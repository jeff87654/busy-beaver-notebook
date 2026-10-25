# Scratch: Coq proof for the BB(9) record candidate 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---

Report: ../bb9_record_1RB0RA_1LI0LC_coq.md.  Final files: ../../proofs/BB9_record_1RB0RA.v (halting),
../../proofs/BB9_record_bound.v (exact score, lower bounds), ../../proofs/BB9_record_twin_1RB0RA.v (twin, halting),
../../proofs/BB9_record_vs_champion.v (hand-written: exact score above the BB(9) champion's exact score).

## Generators (all deterministic; run from this directory)
- `python gen_final.py OUT.v [TWIN]` -> the halting proof (machine-level lemmas explored and proved by mexp.py,
  abstract part abstract.v.in).  `python gen_bound.py OUT.v` -> the bound file (template bound.v.in).
- `mexp.py`: symbolic executor with "transfer" loops (stack carried as a run: X(v,i) -> X(0,i+v)), absorption of
  concrete copies into the loop run, multi-insertion matching (with split insertions), nested loops; Coq output
  (stage, round, loop lemmas and use-site corollaries `_z`).  Built on bb8_list/autoproof (planner8, engine, coqgen).
- `gen_rules.py` (R1-R3), `gen_rebuild.py` (REBUILD), `gen_d2.py` (D2STAGE, HALTRUN), `shapes.py` (family shapes).
- `endcheck.py`: fast Coq check that every exploration's final configuration equals its target (finish_norm).
- `gen_abs_test.py`: DEV ONLY (stubs the big lemmas with Admitted) to test abstract.v.in quickly; never a proof.

## Literal tools (tm.py simulator)
- `tchain2.py "toks" r j N MAX`: successive family configurations (tokens = D-lengths farthest first, a-token last;
  r = accumulator run; j = number of tail blocks 11111100).  TWIN=1 for #12.
- `kgrid.py "P" K0 K1 RLIST J MAX`: the D2 stage [P,2,1^k|1] for a range of k.  `d2halt.py`: D2 stage to the halt.
- `ngrid.py`, `rgen.py`, `micro.py`, `tprobe.py`, `turns.py`, `turnsw.py`, `bigturns.py`: probes and traces.
- `dbg_*.py`: stage-by-stage exploration traces used while building the generators.
