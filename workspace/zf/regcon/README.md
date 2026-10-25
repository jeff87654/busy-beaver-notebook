# Relative consistency of regularity, in the Coq Library of Undecidability Proofs' first-order ZF

```coq
Theorem regularity_relcon : ZFcReg ⊢TC ⊥ -> ZFc ⊢TC ⊥.      (* Main.v *)
(* Print Assumptions regularity_relcon:  Closed under the global context *)
```

and in the library's minimal signature (∈ and ≡ only, `FOL/Sets/minZF.v`), `MinZF.v`:

```coq
Theorem regularity_relcon_min : ZFclReg ⊢TC ⊥ -> ZFcl_min ⊢TC ⊥.
Corollary regularity_relcon_min' (T : form' -> Prop) :
  (forall phi, ZFcl_min phi -> T phi) -> (forall phi, T phi -> ZFcl_all phi) ->
  (fun phi => T phi \/ phi = ax_reg') ⊢TC ⊥ -> T ⊢TC ⊥.
(* also regularity_relcon_all, regularity_relcon_closed, and the bridge between signatures:
   bridge     : T ⊢TC ⊥ <-> ZFc ⊢TC ⊥
   bridge_reg : (T + ax_reg') ⊢TC ⊥ <-> ZFcReg ⊢TC ⊥
   for any T between ZFcl_min and ZFcl_all; all closed under the global context *)
```

Here `ZFcl_all = { forall_times n psi | minZFeq psi }` (any `n`). `ZFcl_min` is the finite list
`minZFeq'` plus the closed closures of the `ax_sep'`/`ax_rep'` instances. `ZFclReg = ZFcl_all + ax_reg'`.
The corollary covers every axiomatization between these two, for example the closed universal
closures of `minZFeq`. The transfer embeds into the function-symbol signature with the library's
`prv_embed`/`embed_ZF'`, applies `regularity_relcon`, and comes back with
`rm_const_prv`/`prv_to_min`/`minZF_sep`/`minZF_rep` from `PCPb_to_minZF` and `ZF_conservativity`.

For the shared target theory `Std_iface.ZFc` of zf-l1-logic (`../stdzf/coq/Std_iface.v`:
minZFeq with closed scheme instances), `Link.v` instantiates these:

```coq
Theorem regularity_relcon_std : (fun phi => Std_iface.ZFc phi \/ phi = ax_reg') ⊢TC ⊥ -> Std_iface.ZFc ⊢TC ⊥.
Theorem regularity_relcon_thm : Std_iface.thm (fun phi => Std_iface.ZFc phi \/ phi = ax_reg') ⊥ -> Std_iface.thm Std_iface.ZFc ⊥.
Theorem bridge_std            : Std_iface.ZFc ⊢TC ⊥ <-> ZFc ⊢TC ⊥.
Theorem bridge_reg_std        : (fun phi => Std_iface.ZFc phi \/ phi = ax_reg') ⊢TC ⊥ <-> ZFcReg ⊢TC ⊥.
```

`⊢TC` is the library's classical natural deduction from a theory (`tprv` in
`FOL/Deduction/FullND.v`): `T ⊢TC phi` means `A ⊢C phi` for some finite list `A` of axioms of `T`.
Everything is stated in the library's syntax: signature `ZF_func_sig`/`ZF_pred_sig`
(∈ and ≡ as predicates; ∅, pairing, ⋃, power set and ω as function symbols), de Bruijn formulas,
and the library's axioms.

## The theories

* `ZFc` = the library's `ZFeq'` (equality axioms, extensionality, empty set, pairing, union,
  power set, the two infinity axioms) plus, for every formula `phi` and every `n` with
  `bounded n (ax_sep phi)` (resp. `ax_rep phi`), the universal closure
  `forall_times n (ax_sep phi)` (resp. `forall_times n (ax_rep phi)`). `ax_sep`, `ax_rep`,
  `bounded` and `forall_times` are the library's.
* `ZFcReg` = `ZFc` plus
  `ax_reg := ∀ (∃ $0 ∈ $1) → ∃ ($0 ∈ $1 ∧ ∀ ($0 ∈ $1 → ¬ ($0 ∈ $2)))`, i.e.
  ∀x ((∃y. y∈x) → ∃y (y∈x ∧ ∀z (z∈y → ¬ z∈x))).

Why `ZFc` and not the library's `ZFeq`:
1. The library's ZF has no regularity axiom at all, so "ZF − Reg" is the library's theory and
   "ZF" has to be defined by adding `ax_reg`.
2. The library's `ZFeq` contains the schema instances `ax_sep phi`, `ax_rep phi` as open formulas
   (the parameters of `phi` are free variables of the axiom). Natural deduction cannot generalize a
   variable that is free in a hypothesis, so `ZFeq` gives separation and replacement only for
   parameters fixed from outside; it does not obviously prove the closed instances
   ∀p ∀x ∃z ∀v (v∈z ↔ v∈x ∧ phi(v,p)). The relativization below needs parametric instances
   inside the proof (for example, to separate with a bound variable as parameter), so it is stated
   for the closures. `ZFeq_ZFc : ZFeq ⊢T phi -> ZFc ⊢T phi` (both classical and intuitionistic)
   is proved in `Main.v`; the converse is open.

## Proof

The standard inner-model argument with the class of well-founded sets:

    WF(x)  :<->  ∃t (t transitive ∧ every nonempty subset of t has an ∈-minimal element ∧ x ∈ t)

It uses no ordinals, ranks or transitive closures.

| File | Content |
|---|---|
| `Rel.v` | Generic relativization for any signature and any class `M` (a formula with free variable `$0`). `rel` bounds every quantifier by `M`. `rel_prv`: if `A ⊢ phi` then `Gamma ⊢ (rel phi)[sigma]` whenever `Gamma` proves `M` of every `sigma k` and the relativization of every hypothesis in `A` under `sigma`, provided `M` is closed under the function symbols. Proved by induction on derivations, including the classical rule. `rel_forall_times` relativizes universal closures. |
| `WF.v` | Formula builders (`transitive`, `wellf`, `WF`, ...) with substitution lemmas and introduction/elimination rules. Helpers for using separation and replacement instances. Canonical witnesses (the least transitive subset of a witness containing `y`), which make the replacement relation functional. **Closure lemma** `WF_closure`: a set all of whose elements are in WF is in WF (proof: collect the canonical witnesses with replacement, take their union plus `{x}`, and use classical case analysis for well-foundedness). Closure of WF under ∅, pairing, ⋃, power set and ω. |
| `Main.v` | Relativized axioms: equality and quantifier-free axioms, extensionality, union, power set, infinity, separation and replacement (closed instances), regularity. Assembly: `regularity_relcon` (rel_prv applied with `sigma := fun _ => ∅`; `rel ⊥ = ⊥`). Also `ZFeq_ZFc`. |
| `MinZF.v` | Transfer to the minimal signature (see above). |
| `Link.v` | Instantiation for `Std_iface.ZFc` (imports `../stdzf/coq` read-only as `ZF`). |
| `Check.v` | Statement check by type ascription, and `Print Assumptions`. |

The auxiliary axioms used by the WF construction (closed instances of separation and replacement,
list `Wax` in `WF.v`) are themselves `ZFc` axioms (`B0_ZFc`).

Size: about 1,600 lines of Coq. Building takes about 35 s.

## Building

Needs the vendored undecidability library at `../stdzf/vendor/theories` (identical to `../stdzf/ext/undec-8.20`, commit 70dfc56) and the compiled `../stdzf/coq/Std_iface.vo` with its dependencies. Its
`FOL/Sets/ZF`, `FOL/Deduction/FullNDFacts`, `FOL/Reductions/PCPb_to_ZFD` and
`FOL/Sets/Models/ZF_conservativity` must already be compiled; use `../stdzf/tools/undecbuild.py`. Then:

```
python build.py        # compiles Rel, WF, Main, MinZF, Link, Check at Idle priority; prints CHECK PASS
```

No axioms are used. The meta-level is constructive Coq. Classical logic appears only as the
object-level Peirce rule of the library's `⊢C`.
