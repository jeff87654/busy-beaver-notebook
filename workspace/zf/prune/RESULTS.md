# Pruning the logical axioms of `prov`: results

Question: can any logical axiom scheme of `prov` (zf/v354/coq/Logic.v) be derived from the others (with
DET, GEN and all ZF axioms EXT, REP (every ph), POW, UNI, INF available), so that its clause could be
removed from the machine?

**Answer: no.** Each of B1, B2, B3, B4, B6a, B6b, B6c, B7, B8a, B8b, B8c is independent of the rest
of the system. The axiom set is irredundant, so no clause can be removed.

Method: for each scheme S, an interpretation in which every other axiom holds and DET/GEN preserve truth,
but an instance of S fails. Then prov without S cannot prove that instance.

## Table

| scheme | verdict | countermodel (short) | checked by |
|---|---|---|---|
| B1 | independent | 3-valued collapsed matrix M1 | `indep/verify_collapse.py`, Coq `coq/Indep_B1.v` |
| B2 | independent | 3-valued collapsed matrix M2 | `indep/verify_collapse.py`, Coq `coq/Indep_B2.v` |
| B3 | independent | 3-valued collapsed matrix M3 | `indep/verify_collapse.py`, Coq `coq/Indep_B3.v` |
| B4 | independent | Tarski semantics, but A. x -. (u e. v) := "-. (u e. v) is valid" | on paper (below) |
| B6a | independent | e. read through an automorphic copy selected by the value of v9 | on paper |
| B6b | independent | Kripke: accessibility for v9 reflexive and symmetric, not transitive | on paper |
| B6c | independent | two-stage Kripke model, stage 0 with empty e. | on paper |
| B7 | independent | v9 ranges over {0} only | on paper |
| B8a | independent | atom v7 = v7 means s(v7) = 0 | on paper |
| B8b | independent | u e. w is false when u is v7 | on paper |
| B8c | independent | u e. w is false when w is v7 | on paper |

The Coq files compile against a copy of Logic.v (`coqc -Q . ZF Indep_B1.v`, run from zf/prune/coq).
Each defines provX = prov without that scheme, proves `provX a -> des (ev a) = true`, and concludes
`~ provX (instance)`.

## Collapsed matrices (B1, B2, B3)

Atoms denote constants (e_eq for every x = y, e_el for every x e. y), A. x a := Q(a), -> and -. are
tables, and D is the designated set. Every axiom except the target is designated for all values in the
generated subalgebra, which is all of {0,1,2} here. That includes REP(ph) for every value of ph.
DET and GEN preserve designation. Format (Imp rows, Neg, Q, e_eq, e_el, D):

* M1 (B1 fails):  ([(0,1,1),(0,0,2),(0,0,0)], (2,0,1), (0,1,1), 0, 0, {0})
* M2 (B2 fails):  ([(0,1,1),(0,0,0),(0,0,0)], (2,0,1), (0,1,1), 0, 0, {0})
* M3 (B3 fails):  ([(0,0,2),(0,0,2),(0,0,0)], (0,2,0), (0,0,1), 0, 1, {0,1})

Found by `indep/collapse.py 3 ...`. The independent re-check `indep/verify_collapse.py` parses the ZF
axioms out of Logic.v. The refuted instances are in the Coq files.

## Infinite models (B4 .. B8c)

M is a model of ZF (exists if ZF is consistent), and assignments s : nat -> M. Validity means true under
every assignment. In the Kripke models below, validity also ranges over every world. Unless noted, = is
identity and e. is real membership. v7 and v9 are variables that occur in no ZF axiom. REP(ph) holds in
every model below for the same reason: the relation that ph defines there is first-order definable in M
from finitely many parameters, so replacement in M applies. In the B6b model, the assignments are
restricted to eventually-constant ones, so that the parameter is a finite set.

* **B4.** Standard semantics, except that a formula A. x -. (u e. v) (body exactly a negated e.-atom)
  is true iff -. (u e. v) is true under all assignments. This is a constant, at most the standard value.
  - GEN holds.
  - B6b holds, because A. y a is never such a body, and for such a body both sides are the same
    constant.
  - B6c holds: E. x A. x a = -. A. x -. A. x a is standard, since its body is a negated A., so it
    equals A. x a, which is at most a.
  - B7 holds, because it negates an =-atom.
  - The ZF axioms contain no A. x -. (u e. v).
  - B4 fails: take x = v9, p = (v0 e. v1 -> -. v0 e. v1), q = -. v0 e. v1, at an s with s(v0) not in
    s(v1). Then A. x (p -> q) and A. x p are true, and A. x q is false.
* **B6a.** u e. w is read as pi(s(u)) e. pi(s(w)) when s(v9) = 0, and as s(u) e. s(w) otherwise. Here
  pi swaps 0 and {0}. Each reading is an isomorphic copy of M, so ZF and B8 hold.
  - The e.-half fails: 0 e. {0} holds, but not A. v9 (0 e. {0}).
  - The =-half is also independent (it is not a separate clause): read v7 = v7 (same variable twice)
    as "some other variable has the value s(v7)". This model validates B7 and B8, but not
    v7 = v7 -> A. z v7 = v7.
* **B6b.** Worlds are eventually-constant assignments. A. v9 moves s(v9) to any c in C(s), where R(s)
  is the set of values of the other variables:
  - C(s) = M if s(v9) is in R(s);
  - C(s) = R(s) ∪ {s(v9)} otherwise.

  This accessibility relation is reflexive and symmetric, so B6c holds. It reaches every s(y), so B7
  holds. It changes only v9, so B6a holds. It is not transitive. Instance that fails: A. v9 A. y a ->
  A. y A. v9 a with a = (y is empty -> v9 is empty \/ v9 = u), at the s with s(v9) = 0 and all other
  variables = b != 0.
* **B6c.** Two copies of the assignment space (stages 0 and 1). From stage 0, A. x moves to stage-0 or
  stage-1 assignments that differ at x. Stage 1 is standard. At stage 0, e. is empty and = is identity.
  - A universal true at stage 0 is true at stage 1, and an existential true at stage 1 is true at
    stage 0. So EXT, POW, UNI, INF and REP hold at stage 0.
  - B6b holds (the relations commute), and B6a, B7 and B8 hold.
  - E. v9 A. v9 (v0 e. v1) -> v0 e. v1 fails at stage 0 when s(v0) e. s(v1).
* **B7.** v9 ranges over {0}, so E. v9 v9 = v0 fails when s(v0) != 0.
* **B8a.** v7 = v7 (same variable twice) means s(v7) = 0. Every other atom is standard. This breaks
  only the instance x = v7 -> (x = v7 -> v7 = v7) of B8a, i.e. reflexivity at v7.
* **B8b / B8c.** u e. w is false when the left variable (B8b) or the right variable (B8c) is v7, and
  real membership otherwise. The ZF axioms only use v0..v3, and B8c (resp. B8b) keeps the same left
  (right) variable on both sides.

Notes:
* B6b remains independent even with S5 axioms 4/5 added (so "B6c + 5" cannot replace B6b+B6c).
  Countermodel: worlds are (assignment, colour in {0,1}). R = R(s) is the set of values of the other
  variables, and X = {0}. Over each fixed assignment of the other variables, A. v9 has two equivalence
  classes:
  - class 1 = {(r,0) : r in R} ∪ {(c,h) : c in X \ R};
  - class 2 = {(r,1) : r in R} ∪ {(c,h) : c not in X ∪ R}.

  Every class reaches all of R, so B7 holds. The classes change when y changes R, so A. v9 and A. y do
  not commute.
* Derivations may use the ZF axioms. Every countermodel above validates all of them.

## Replacement search (two clauses -> one scheme), bounded; stopped at the lead's request

Cost model: a clause costs one select element, so a merged scheme pays only if its token string is about
as long as the two it replaces, or shorter. All runs were at Idle priority with the zfp/ILS tools copied
into `build/` (B354 base) and `build_r3/` (zf-axtext's R3s336 base). New clause texts are in
`build*/extra_spec.json`, which a small loader added to the copied zfp.py reads.

### (a) Propositional: B2 + B3 -> one scheme BY (B1 kept)
* Filter (`basis/cands.py`): BY must be a tautology, and no MP-closed 3-valued matrix may validate
  B1 + BY while refuting B2 or B3. No formula with at most 6 connectives passes. With 7 connectives
  (13 tokens, against 12 for B2+B3) several pass, e.g. CpCCNqCCqrNpq and CpCCCNpqCNrrr. The k=7 run was
  interrupted, so the survivor list is partial.
* Condensed detachment (`basis/cd.py`): {B1, CpCCNqCCqrNpq} derives B2 and B3, and so does
  {B1, CpCCCNpqCNrrr}. BY = CpCCNqCCqrNpq means p -> ((-.q -> ((q -> r) -> -.p)) -> q). It is a
  tautology, so B1-B3 derive it.
* Measured. On B354: 351 (`build/B354Y1_351.*`, 30 min ILS) against 354. On R3s336: **335**
  (`build_r3/R3Y1_335.*`, 30 min ILS). A control ILS of R3s336 itself over the same time stayed at 336.
  The gain is 1 state.
* Clause table of R3Y1_335 (order): INF B6b B4 B8a B6c B8c BY B8b B1 B7 EXT DET REPsb0 GEN B6a. BY's
  spec is `a b wn b c wim a wn wim wim b wim wim` with perm [3,2,1]. B2 and B3 are removed.
* **Validated and formalized (2026-10-11).** Files `R3Y1_335.{json,tm,val,enum.txt}` (also in
  `build_r3/`) passed all checks: dag stats, crosscheck (2001 ops, 0 mismatches, min IP-space margin 4),
  symrm selftest (0 mismatches), semtest (2000 trials, 0 mismatches; BY selected 125 times, with a FORM
  written from the Polish formula) and ipbound (prefix 240 ops, min margin 1, max depth 109).
* **Coq** (`coqR3/`, built against copies of zf/axtext/coq/R3 Logic.v, L1_LDef.v, L1_LProp.v and
  L1_LMeta.v):
  - `PropBasis.v` (generated by `basis/gen_prop_coq.py`): for any P closed under DET, B1 and BY give
    B2 and B3. These are explicit condensed-detachment terms (`y_B2`, `y_B3`).
  - `EquivY.v`: `lprov_BY` (BY from B1-B3), `lprovY_lprov : lprovY a <-> lprov a` and
    `provY_prov : provY a <-> prov a`, where provY/lprovY are the R3 systems with B2, B3 replaced by
    BY. So everything verified for R3 transfers.
  - Build: `coqc -Q . ZF` on Logic, L1_LDef, L1_LProp, L1_LMeta, PropBasis, EquivY.

### (b) B6b + B6c -> one scheme
* Negative evidence: "B6c + S5 axiom 4/5" does not give B6b (colour model, above). Any scheme whose
  conclusion starts with a quantifier cannot give B6c: in a two-stage model where stage 0 sees only
  stage 1, every quantified formula has its stage-1 value, but B6c fails.
* Best candidate: X6(x,y,a) = E. y E. x A. y A. x a -> a (11 tokens, against 18). It is valid in FOL,
  including y = x. Proven on paper:
  - X6 + B4 + B7 give B6c for all vacuous a, i.e. if a -> A. y a then E. y a -> a. That covers every
    use of B6c in L1_LMeta.
  - X6 + full B6c give B6b.
* **OPEN (closed for now, 2026-10-11).** Does X6 + rest derive full B6c, and hence B6b? Hand-off for a
  fresh agent:
  - *Available in prov_X6 (paper proofs).*
    - VE: if a -> A. y a, then E. y a -> a. Proof: c := A. y A. y a; then a -> c and c -> A. y c, and
      c -> E. y c (from c -> A. y c, K, and B7 via -. A. y F). Chain E. y a -> E. y c -> E. y E. y c ->
      a, using X6(y,y,a).
    - Hence lneg_vac, leq_refl, lspec's last step, leib (it only needs vacuity of = atoms) and every
      B6c use in L1_LMeta go through.
    - X6 + full B6c -> B6b. X6 in B-form gives p -> A. w A. u E. w E. u p. Then E. u E. w p ->
      E. u E. w A. w A. u E. w E. u p -> (B6c twice) E. w E. u p.
  - *Where it is stuck: the Wal case of lvac*, i.e. A. z a -> A. y A. z a for y not in a, given
    a -> A. y a (and VE for a).
    - Frame proof: t R_y v R_z m with -.a(m). X6(y,z) gives m R_y m' R_z t'. Then -.a(m') by
      y-invariance. X6(z,y) at m' needs an R_z;R_y path to a world satisfying A. z A. y a. That path
      needs t' R_y t' (reflexivity, i.e. T for the formula A. z A. y a, which is equivalent to A. z a),
      or y-invariance of A. z A. y a. Both are the Wal case again, for a formula at least as big.
    - Every syntactic route found has the same shape: E-introduction (d -> E. y d) or T for a
      quantified d of size >= |A. z a|. So induction on size does not close.
    - Likewise B6c(x,a) for quantified a needs lvac(w, ...) of a quantified formula (via X6(x,w) with
      fresh w, or via lspec + leib).
  - *No countermodel either.* Every model family tried collapses to standard semantics when X6 holds
    for all variable pairs, together with B7 (reach every s(y)), B6a, VE and the free choice of other
    variables. The families: assignment-based Kripke frames with variable-dependent accessibility,
    stage models, per-variable hidden tags (bisimulation collapse), varying/increasing domains, and
    eventually-constant tails. The one structure not yet ruled out: hidden state coupled per pair of
    variables (each atom x e. y reading its own pair-tag h_xy, changed only by R_x and R_y).
  - Suggested next steps: a completeness proof for prov_X6 (Henkin, where X6 replaces B5/B6b/B6c);
    or a countermodel with pair-coupled hidden state. `x6/frames.py` (finite modal frames, X6
    conditions) is written but has not been run.
* Measured: B354 with B6b+B6c -> X6 gives 348 (`build/B354X6_348.*`, 1 h ILS). It was not searched on
  R3s336 (337 unsearched there). Do not use X6 unless the open question is settled.
