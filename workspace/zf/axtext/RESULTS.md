# zf-axtext: shorter ZF axiom texts (results)

## R3s336: REP with a bounded-fiber hypothesis (adopted)

REP's hypothesis `A. v1 ph -> v2 = v1` ("each w has at most one image") is replaced by
`A. v1 ph -> ( -. A. v0 ( v0 e. v2 -> v0 e. v1 ) -> v2 e. v1 )` ("the images of w lie in y u P(y)").
POW and UNI are instances of the new REP, so both clauses are dropped. EXT and INF are unchanged up to
flips and renaming. Result: 336 states (`search/cand/R3s336.*`), validated by crosscheck, symrm and semtest.

Coq (`coq/R3`, `python build.py Check.v`): `prov (Wel v0 v0) <-> ZFc ⊢TC ⊥`, closed. `L1_R3s.v`
relates the machine texts to `Logic.v`. The Reg / function-symbol variants are in `regcon/MainR3s.v`
(build `coq/R3` first). zf-prune's BY (B2+B3 -> one scheme) on top of this gives 335 (`zf/prune`).

## Round 2: no further gain

All measurements at Idle with one process.
* **Outliner** (`search/outl*.py`), on the fixed R3s336 clause set.
  * The cell model is exact: DAG states = distinct reachable suffixes of length >= 2 after outlining.
  * Wade's longest-first greedy (269 cells -> 336) could not be beaten:
    * 200 random tie-break seeds: 336-341;
    * exact-gain greedy: 271 cells;
    * 1107 randomized restarts: best 270 cells, 342 states;
    * a grammar ILS (inline + re-outline), 74k iterations: 336.
  * Cause: 76 of 151 sequences carry escaping break/continue paths and 63 more sit under such parents, so
    only 12 macros can be restructured freely.
* **Axiom-text variants** (`search/ils2.py`), on R3Y1_335. The search can switch between 12 REP fiber-bound
  forms, EXT vs. split EXT, and INF vs. INF2. Result after 1 h: 335.

## B6a: side-condition-free replacements (rejected)

All counts on top of R3Y1_335 (335), after a 40 min ILS where a start -> end is given.

| replaces B6a | sound | states |
|---|---|---|
| B6a body with NO distinctness check (cost probe), params zeroed in main | no | 328 unsearched |
| plain-check B6a without b6aD | yes | 344 unsearched |
| B6aM: `-. A. z z = x -> -. A. z z = y -> (B6a body)` (Megill distinctors, both halves) | yes | 343 -> 335 |
| C9 + C14 (set.mm ax-c9 / ax-c14 as two clauses) | yes | 340 unsearched |
| B6aMe: distinctor form, e.-half only | yes | 334 -> 329 |
| B6aE: e.-half only, normal check | yes | 332 -> 331 |
| B6a /\ parametric EXT sharing the check (EXT clause dropped) | yes | 344 unsearched (at most 1-2 states) |
| any of the above with `lastD` (destructive last parameter read instead of b6aD) | | worse in every case |

Why none is adopted:

1. **The check is cheap.** It costs about 7 states net (328 vs 335), and b6aD is itself worth 9 states.
   Distinctor premises add 12 tokens, about 6 states, so the complete form B6aM ends at 335. Splitting
   B6a's halves does not help, since each half still needs both tests (z != x, z != y).
2. **The >= 5-state candidates drop the =-half `x = y -> A. z x = y`, and it cannot be recovered.**
   * In L1_LMeta, `leq_refl` (x = x) is proved from `LB6a x x z`, and `leib`'s A. case needs `h -> A. z h`
     for `h = (x = y)`. Specialization (`lspec`) and alpha-renaming go through `leib`, so the whole
     metatheory rests on =-vacuity.
   * Recovering it from EXT needs `x = y -> A. w (w e. x <-> w e. y)` for ARBITRARY x, y, i.e. Leibniz
     under a quantifier, which is =-vacuity again. Moving the closed EXT (fixed v0..v2) to other
     variables needs specialization: a circle.
   * A parametric axiom breaks the circle only with its own distinctness check. The cheapest complete
     version, `(x e. y -> A. z x e. y) /\ (A. z (z e. x <-> z e. y) <-> x = y)` with z != x, y, is about
     11 tokens longer than B6a + EXT.
   * B6aMe also needs `-. A. z z = x` from the ZF axioms. That is true semantically (no 1-element model
     satisfies REP + INF), but the derivation hits the same specialization circle.
   * An equiconsistency proof would need an interpretation or a new Megill-style completeness argument:
     research-scale.
3. **No vacuous-generalization scheme avoids it.** Every side-condition-free valid scheme tried (e.g.
   `a -> A. z E. z a`) needs the dual vacuity `E. z a -> a` for atoms, which is B6a again. zf-prune
   reached the same conclusion for its X6 scheme: X6 never makes an atom vacuous, and both halves of B6a
   are independent.

Specs (B6aM, B6aMe, C9, C14, B6aE, B6aX, BXE, B6aNC) and the `lastD` option are in `search/zfp.py`.
Logs: `search/runs/M_B6a*.log`.
