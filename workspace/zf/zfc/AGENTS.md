# zf/zfc: working notes for proof agents

Goal: the relative consistency of AC with ZF+Reg, stated at the object level:
`(ZFc + ax_reg' + ax_ac) ⊢TC ⊥ -> (ZFc + ax_reg') ⊢TC ⊥` (Z_main.ac_relcon). It is stated in the Coq Library of
Undecidability Proofs' minimal ∈/≡ signature, with classical natural deduction `⊢C`. Method: Gödel's L as
an inner model. Every derivation is relativized to the class formula `Lform` (RegCon.Rel.rel_prv, via
Z_rel.transfer), and each axiom is shown to hold in L.

The top-level assembly (Z_main.v) is already proved from the statements below. The work left is to prove
the `Admitted` lemmas.

## Files (dependency order)

| file | content | status |
|---|---|---|
| Z_rel.v | `relS Y φ` (relativize to a set), D0/Sg formulas, `D0_abs`, `Sg_up`, `rel_ft`, `transfer`, `fbcomp`/`d0comp`/`sgcomp` (fast checkers) | done |
| Z_base.v | Delta_0 primitives: Sing0 Pair0 OP0 Emp0 Sub0 Trans0 Ord0 Succ0 Lim0 Om0 Union0 App0 PairsAll IsRel0 Fun0 Dom0 | done |
| Z_prim.v | ZFR (the target theory), equivalences with Std_setbase, existence/uniqueness, pairs, functions | to prove |
| Z_ord.v | ordinals, ω, schemas least_ord / ord_ind / ord_collect | to prove |
| Z_trec.v | transfinite recursion for a step formula S (rec_ex, rec_agree) | to prove |
| Z_cl.v | 8 Delta_0 operations, Step, closure Cl, Def0 = Cl(A∪{A}) ∩ P(A), definability lemma | to prove |
| Z_L.v | LL α Y (Y = L_α), the class Lform / InL, basic facts | to prove |
| Z_sg.v | LL, Lform, Def0 are Sigma; Ord0 is Delta_0 (by computation) | done |
| Z_refl.v | reflection: ∀α ∃β>α, L_β reflects φ^L | to prove |
| Z_axL.v | every ZFR axiom holds relativized to L; axL_ZFR packaging | to prove |
| Z_wo.v | AC formula (ACmat, ax_ac); ZF ⊢ every x ∈ L_α has a choice set | to prove |
| Z_ac.v | acL_ex: AC holds in L | to prove |
| Z_main.v, Check.v | final theorem (proved from the above), statement check | done |

## Conventions

- Contexts: lemmas are about an abstract `G : list form`, with `incl ZF0base G` (equality, ext, ∅, pair,
  union, power), `In ax_reg' G`, `In ax_om' G`, and `incl Ax_X G` for a fixed list `Ax_X` of closed
  separation/replacement instances (`forall_times n (ax_sep' φ)` with `fb (S n) φ`, `forall_times n (ax_rep' φ)`
  with `fb (S (S n)) φ`). Every list comes with a proof `Ax_X_ok : In a Ax_X -> ZFR a` (use ZFR_sep/ZFR_rep and
  `fbcomp` for the fb side conditions). Schema lemmas take the instance(s) for their formula explicitly.
  Lists grow along the file order: Ax_prim ⊆ Ax_ord ⊆ Ax_cl ⊆ Ax_L ⊆ Ax_wo.
- Predicates are HOAS functions `term -> ... -> form`, `simpl never`, with a substitution lemma in the rewrite
  database `fsub` (prove it with `psubst Name`). The tactic `simp`/`simp_in` normalizes substitutions.
- PITFALL: `∧` is LEFT associative (level 41, no associativity declared). `a ∧ b ∧ c` = `(a ∧ b) ∧ c`. For a
  bounded existential with several conjuncts, write `∃ ($0 ∈' X ∧ (A ∧ B))`, or the formula is not D0.
  `→` is right associative. `¬ A` is `A → ⊥`.
- `∀ ∀ φ` can be misparsed as Coq's binder. Write `∀ (∀ (...))`.
- Delta_0 / Sigma: `D0 φ` and `Sg φ` (Z_rel) are syntactic. Check concrete formulas with `d0comp` / `sgcomp`, and
  closedness with `fbcomp` (all by vm_compute). Definitions that enter `LL` must stay Sigma: only positive
  ∃, ∧, ∨, bounded ∀ (`∀ ($0 ∈' $(S k) → φ)`), and `D0 → Sg`.
- Proof style: see zf/stdzf/coq/Std_setnd.v (fintro, fall, fex, finst, fexists, fsplit, fdestr, fleft,
  fright, fcases, fapply, fmp, fabsurd, fcontra, fassert, fhave, fobtain), Std_setbase.v (feq, fmem, frew,
  frew_in, sep_use, rep_use, ...), Std_setrec.v (long worked example). Z_rel.v redefines `weaken_facts` so
  that the fact tactics also weaken hypotheses `forall k, G ⊢C _`.
- Classical object-level reasoning: `XM_rule`, `DN_rule`, `fcontra`. The meta level stays constructive.

## Rules for agents

1. Edit ONLY your own file(s). Do not change existing statements or definitions of lemmas in your file
   (they are used by other agents), except the instance lists (`Ax_X`, `*_insts`) and their `_ok` lemmas,
   which you fill. You may add helper definitions and lemmas freely. If a statement is wrong or
   unprovable, do not silently change it. Add a corrected variant next to it, prove what you can, and
   explain the problem precisely in your report. If you need a fact that belongs upstream and is missing,
   prove it locally in your file from the upstream lemmas. If it cannot be proved from them, state it as a
   local lemma marked `(* UPSTREAM-NEEDED *)` with `Admitted`, and report it.
2. No `Admitted`/`admit`/`Axiom`/`Parameter` in the end, except UPSTREAM-NEEDED ones. No axioms through
   imports (no FunctionalExtensionality, Classical, ProofIrrelevance, ...). `Print Assumptions` of your main
   lemmas should show only Admitted upstream lemmas (from files that are still in progress), nothing else.
3. Upstream lemmas may still be Admitted while you work. That is fine: build against their statements.
4. BUILD only with `python C:/Users/jeffr/Downloads/bb8/zf/zfc/build.py File.v`. It runs coqc at Idle
   priority under a machine-wide 2-process lock (the machine is shared). Never run coqc directly. Never start
   other CPU-heavy processes. The script rebuilds out-of-date dependencies itself.
5. Other agents build against your file AT THE SAME TIME, so your real file must ALWAYS compile. Develop in a
   copy `Z_X_wip.v` (import the real upstream files). After each batch of progress that compiles, copy the
   wip content into the real file (lemmas still unproved stay `Admitted` there), and build it once to
   confirm. Delete your wip file at the end.
6. Report at the end (your final message): which lemmas are proved, what is still Admitted and why, the
   contents of your instance lists, and any statement problems or UPSTREAM-NEEDED facts.
