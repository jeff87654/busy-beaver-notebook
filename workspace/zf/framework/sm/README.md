# SM B1: abstract string-stack machine, ZF program, decision DAG

Deliverable B1 of `../SM_SPEC.md`. Everything runs with `python -I`; nothing outside this directory
is modified. TMBuilder is imported read-only from `zf/ext/turing_machine_explorer`.

| file | content |
|---|---|
| `sm_abstract.py` | `class SM`: abstract state (A, B, c', N), the primitives (`prim`), the DAG interpreter with Wade's IP path semantics (`step`, `run_candidate`), `run_enumeration`, wff checks |
| `sm_prog.py` | axioms (prefix templates + macros), dispatch trie, `SMBuilder(TMBuilder)`: the program as nested lists → hash-consed cons cells (same pipeline and same count method as Wade's 324) |
| `sm_config.py` | the chosen prefix code, param reading orders and GEN style (output of `sm_search.py`) |
| `sm_ref.py` | independent reference semantics over the bit string (decode / apply / encode) |
| `sm_build.py` | writes `sm_dag.json` (the DAG for the integrator) and `sm_dag_cells.txt` (cell count + attribution) |
| `sm_test.py` | T0 templates vs zf2.py, T1 DAG vs reference, T2 exhaustive enumeration, T3 planted proofs |
| `sm_search.py` | simulated annealing over code tree, axiom→leaf assignment, param orders |

## Semantics decisions (where SM_SPEC is silent or had to change)

* **RB polarity**: bit 1 = advance, bit 0 = zero branch (IP break 1), like `decnz`. END (N exhausted):
  B erased, c' = 0, IP := [] (restart main). Candidate order = SM_SPEC 5's binary counter: read-order
  bits are LSB first, so every non-empty candidate ends with a 1.
* **Typed wff reader** (spec fix): the spec's token code with `v=1111` in operand position allows
  garbage (`e -> ...`, `-> v0 ...`). Here a wff token is read with `e=0 ==10 ->=110 ~=1110 A=1111`
  and the variables after `e`/`=` (two) and after `A` (one) are read as unary `1^i 0` directly.
  c' = pending wffs - 1: `->` INCC; `e`/`=` DECC whose zero branch ends the param.
  The tokens are produced incrementally (PUSH e, then APP1 per further 1-bit: e→=→->→~→A).
* **Never-empty theorem stack** (spec gap): GEN on an empty stack would COMMIT the non-wff `A x`.
  Boot pushes `BOOT_THEOREM = ~ A v0 ~ = v0 v0` (B7 instance); DET with fewer than 2 theorems is a
  no-op. So A is never empty and DUPT is always defined (the B2 TM DET must implement the m=1 no-op).
* **18 axiom codes**, not 20 (zf2.py lists B6b and B8b twice).
* **CHECK after every step**: `main = [label d: TREE, CHECK]`; every leaf body ends with `break d`.
* **Dispatch trie with prefix factoring**: at an internal node the longest common prefix of the
  group's bodies (param reads, NEWT, template ops) is emitted before the decision bit, so code bits
  and param reads interleave in the encoding (decodable; `sm_ref.decode` follows the same trie).
* `DUP k` copies the k-th entry of B (a param, k ≤ 3) to the end of the last wff; params are read
  in the order of `sm_config.CONFIG['param_orders']` (default: the order in `sm_prog.AXIOMS`).

## TMBuilder notes (reused, subclassed; not modified)

* `label()` only handles 2-element lists along the label path (asserts otherwise) → generalised.
* `breakout_common_subsequences()` has a latent bug (`self.reachable` without call in the
  duplicate-sequence branch, never hit by zf2) → fixed in the subclass; more importantly it may
  extract a middle subsequence containing a two-outcome op or a break/continue into a car-entered
  nested sequence, which changes where the zero branch / break lands. The subclass only extracts
  subsequences whose elements are all *closed* (every exit = normal advance, computed by an exit
  analysis). Equivalence is tested op-trace by op-trace against the DAG without breakout (T1).
* `label()` has a typo `self_sequences` in a branch not used here.

## Results (config in sm_config.py)

* **228 DAG cells** (Wade zf2: 324 with the same counting). Hash-consing only: 360; without trie
  prefix factoring: 238; plain balanced code without factoring: 247. Max car-edge run 4, depth 31.
* Attribution (sm_dag_cells.txt): code tree 34, readers 21 (READW 17, VAR 3, READV 1), main/DET/GEN
  glue 5, template-exclusive 106, shared between templates 62.
* Tests (sm_test_out.txt, sm_test_k18.txt): templates == zf2.py (17; B6a = spec distinctor form);
  DAG == reference decoder and breakout == no-breakout op-trace for 1500 random candidates; all
  candidates < 2^14 (and < 2^18) never halt, full well-formedness check after every op, stack ==
  reference after every candidate; planted proofs (single-axiom targets halt first exactly at
  their encoding; B7;B3;DET derivation halts right after the DET, 35 bits; DET mismatch /
  invalid / underflow and GEN behave as specified).

## Running

    python -I sm_build.py        # -> sm_dag.json, sm_dag_cells.txt
    python -I sm_test.py 14      # all tests, exhaustive up to 14 bits

## Interface for the integrator

`sm_dag.json`: `{"root": name, "cells": n, "nodes": {name: [car, cdr]}, "code": ..., ...}`; an entry
is a node name or a leaf `["op", OP, args]` (`RB`, `DECC` two-outcome; `PUSH [v]`, `APP1`, `NEWP`,
`NEWT`, `INCC`, `DUP [k]`, `DUPT`, `DET`, `COMMIT`, `CHECK`), `["break", k]` or `["continue", k]`
(P includes the leaf's own edge bit: break k = inc(strip k zeros), continue k = strip k ones).
`SM(nodes, root).run_candidate(bits)` replays it on the abstract machine.
