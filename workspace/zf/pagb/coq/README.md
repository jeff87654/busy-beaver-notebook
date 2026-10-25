# zf/pagb/coq — logic layer for a TM that halts iff PA ⊢ Goldbach

Coq 8.20, no axioms. Library: the Coq Library of Undecidability Proofs, unmodified subset in
`../vendor` (copied by `tools/vendor.py` from `zf/stdzf/ext/undec-8.20`, commit 70dfc56).
Build: `python -I build.py`; full check: `python -I check.py` (clean rebuild, prints CHECK PASS).

## Statements

| file | statement |
|---|---|
| Spec.v | `GC_form` (library PA syntax), `Goldbach_nat`, `GC_adequate : rho ⊨ GC_form <-> Goldbach_nat`, `PA_proves_GC := PAeq ⊢TC GC_form`, `PA_GC_refutation : PA_proves_GC <-> (PAeq ⋄ ¬GC_form) ⊢TC ⊥` |
| PA_Comp.v | `pprov_NG_iff_PA_GC : pprov (eq NGw) Fw <-> PA_proves_GC` |

`PAeq` is the library's PA with equality axioms (the library's `PA` has none, so under ⊢ its `==` is
uninterpreted).  `⊢TC` is classical natural deduction from finitely many axioms.

## Reference calculus (PALogic.v)

`pprov X`: named-variable Tarski–Megill Hilbert system over terms 0, S, +, × with equality as the only
predicate; rows B1–B3, B4, B6a (atom vacuity, z ∉ t,s), B6b, B6c, B7 (∃x x=t, x ∉ t), E8 and the
congruences ES/EPl/EPr/EMl/EMr (arbitrary terms), six Q axioms, and the substitution-free induction
schema `IND x c a` (c ≠ x, c ∉ a).  `NGw = ¬ tr(GC_form)`, `Fw = ¬(0=0)`.

## Proof structure

* soundness (pprov → PAeq): PA_dB (named → de Bruijn), PA_F (`pprov_Fvalid`; parametric induction
  instances are derived from one parameter-free library instance, `nd_IND_closed`), PA_Frag
  (∧ ∨ ∃ ↔ their {→,⊥,∀} definitions), PA_Sound (`pprov_NG_GC`).
* completeness (PAeq → pprov): PA_LProp (propositional, from stdzf), PA_LMeta (deduction theorem,
  vacuity, term congruence, term Leibniz, specialization to terms), PA_tr (de Bruijn → named, exact
  under all substitutions), PA_H/PA_ND (`nd_sound`: library ND → named Hilbert), PA_Comp (each PAeq
  axiom's translation is derivable; induction via `ind_core`).

Next layers (machine dependent): code-level calculus of the machine ↔ `pprov`, enumerator (L1),
register-machine program and TM.
