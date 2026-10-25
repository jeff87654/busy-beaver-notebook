# Relative consistency of the axiom of choice, at the object level

```coq
Theorem ac_relcon :
  (fun phi => (Std_iface.ZFc phi \/ phi = MinZF.ax_reg') \/ phi = ax_ac) ⊢TC ⊥ ->
  (fun phi => Std_iface.ZFc phi \/ phi = MinZF.ax_reg') ⊢TC ⊥.          (* Z_main.v *)
(* Print Assumptions ac_relcon: Closed under the global context *)
```

Everything is stated in the Coq Library of Undecidability Proofs (Kirst & Hermes): its minimal ∈/≡
signature (`FOL/Sets/minZF.v`), its de Bruijn syntax, and its classical natural deduction `⊢TC`
(`tprv`, Peirce's rule). The theories are:

* `Std_iface.ZFc`: the library's `minZFeq` (equality axioms, extensionality, ∅, pairing, union, power
  set, infinity `ax_om'`), with every separation/replacement instance universally closed
  (`../stdzf/coq/Std_iface.v`).
* `MinZF.ax_reg'`: regularity, ∀x ((∃y. y∈x) → ∃y (y∈x ∧ ∀z (z∈y → ¬ z∈x))) (`../regcon/MinZF.v`).
* `ax_ac` (Z_wo.v): Zermelo's form of AC in plain ∈/≡ (no pairs):
  ∀x [ (∀y∈x ∃z. z∈y) → (∀y∈x ∀y'∈x (¬ y≡y' → ¬∃z (z∈y ∧ z∈y'))) →
       ∃c ∀y∈x ∃z (z∈y ∧ z∈c ∧ ∀w (w∈y → w∈c → w≡z)) ].

Combined with `regularity_relcon_std` (zf/regcon), Z_main.v also proves

```coq
Corollary ac_reg_relcon : (fun phi => (ZFc phi \/ phi = ax_reg') \/ phi = ax_ac) ⊢TC ⊥ -> ZFc ⊢TC ⊥.
Corollary zfc_relcon    : (fun phi => ZFc phi \/ phi = ax_ac) ⊢TC ⊥ -> ZFc ⊢TC ⊥.
```

(both closed under the global context). With `prov_iff_ZFc` (zf/stdzf), O'Rear's `prov (Wel v0 v0)` is
therefore equivalent to the inconsistency of ZFC (with or without regularity).

## Proof

The proof is Gödel's inner model L, done as a derivation translation. `RegCon.Rel.rel_prv` relativizes a
derivation from ZF+Reg+AC to the class formula `Lform`. Each axiom then has to be proved relativized to L
inside ZF+Reg. No semantics is involved. Schema instances get uniform derivations, built by Coq
recursion on the formula (the definability lemma and reflection).

| File | Content |
|---|---|
| Z_rel.v | `relS` (relativization to a set), syntactic Delta_0 / Sigma formulas, `D0_abs` (Delta_0 absoluteness for transitive classes), `Sg_up` (upward absoluteness of Sigma), `rel_ft`, `transfer` (ZF-theorems hold in M), boolean checkers `fbcomp`/`d0comp`/`sgcomp` |
| Z_base.v | Delta_0 primitives (ordered pairs, functions, ordinals, ω, ...) |
| Z_prim.v | their basic theory, and links to the stdzf toolkit |
| Z_ord.v | ordinals, ω, least-element / induction / collection schemas |
| Z_trec.v | transfinite recursion for a step formula |
| Z_cl.v | Def(A) := Cl(A ∪ {A}) ∩ P(A), where Cl is closure under 8 Delta_0 operations on finite environments. Definability lemma: every A-definable subset of A (any formula, any parameters in A) is in Def(A) |
| Z_L.v | L_α (L_0 = ∅, L_{α+1} = Def(L_α), unions at limits) and the class L, with basic facts (transitive, cumulative, L_α ∩ On = α) |
| Z_sg.v | `LL α Y` ("Y = L_α") and `Lform` are Sigma (checked by computation) |
| Z_refl.v | reflection principle for the L_α hierarchy (Tarski–Vaught closure, ordinal collection, ω-iteration) |
| Z_axL.v | every ZF+Reg axiom holds in L (separation and replacement via reflection + definability) |
| Z_wo.v | ZF ⊢ every x ∈ L_α has a choice set (canonical well-orders of the L_α built along the recursion) |
| Z_ac.v | AC holds in L. Transfer of Z_wo to L, with (L_α)^L = L_α from Sigma upward absoluteness plus uniqueness in V. V = L is not needed |
| Z_main.v | assembly. Check.v: statement check and `Print Assumptions` |

About 7,600 lines of Coq. There are no axioms, the meta level is constructive, and classical logic appears
only as the object-level Peirce rule.

## Building

The build needs the vendored library `../stdzf/vendor/theories` with its `FOL/Sets/minZF`,
`FOL/Deduction/FullNDFacts` compiled, and the compiled `../stdzf/coq` and `../regcon` developments.

```
python build.py          # rebuilds what is out of date, then Check.v; prints CHECK PASS
python build.py Z_L.v    # one file and its dependencies
```

`build.py` runs coqc at Idle priority and allows at most two coqc processes machine-wide (lock files in
`.locks/`). A clean build takes about 15 minutes (Z_wo.v ~5 min, Z_axL.v ~2 min).
