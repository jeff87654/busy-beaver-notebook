# zf/m254tg/settheory: set-theory layer for the ZF + Grothendieck-universes machine

## Status (2026-10-14): DONE, `python build.py` → CHECK PASS (all three headlines Closed)

```coq
Theorem SU_equicons   : SUIR ⊢TC ⊥ <-> (fun phi => ZFc phi \/ phi = GU) ⊢TC ⊥.                  (* SU_main.v *)
Theorem SU_equicons_R : SUIR ⊢TC ⊥ <-> (fun phi => (ZFc phi \/ phi = ax_reg') \/ phi = GU) ⊢TC ⊥.
Theorem SU0_equicons  : SU0  ⊢TC ⊥ <-> (fun phi => ZFc phi \/ phi = GU) ⊢TC ⊥.
(* Print Assumptions: Closed under the global context (all three) *)
```

It is proved for the **proposed UG' interface** (section 1.2, `SU_def.ug`). The lead's original UG
is too weak (section 1.1). If the interface changes, only SU_def / SU_s0 / SU_quot / SU_gru /
SU_sound's `ug_core` need edits.

| file | content | lines |
|---|---|---|
| SU_gu.v | `Gru` (set.mm df-gru, transliterated clause by clause), `GU`, `T_GU`, `T_GUR` | 47 |
| SU_def.v | `ug` (UG'), `SU0`, `SUIR`, closedness | 68 |
| SU_s0.v | `S0_to_SU0`: every S0 axiom (CP, GIC) is SU0-derivable | 69 |
| SU_gru.v | `Gru0`, `GU0`; `gru0_gru : Gru0 u → Gru u` and `GU_of_GU0` in ZF | 182 |
| SU_quot.v | `SU_GU0 : SU0 ⊢TC qtS GU0` (raw w is a quotient weak universe) | 131 |
| SU_complete.v | `GU_to_SU0 : T_GU ⊢TC ⊥ -> SU0 ⊢TC ⊥` | 53 |
| SU_V.v | V_α by Z_trec (`VV`, `Vform`): existence, uniqueness, membership equation, monotonicity | 320 |
| SU_fn.v | `fn_build`: set functions from functional formulas (replacement) | 75 |
| SU_univ.v | universes: κ = U∩On ordinal, successor closure, V_β ∈ U (β ∈ U), V_κ ⊆ U | 192 |
| SU_sound.v | SUIR axioms in ⋃V_α inside ZF + Reg + GU (least-stage collection); `SU_to_TGUR` | 441 |
| SU_reg.v | `GU_reg_relcon : T_GUR ⊢TC ⊥ -> T_GU ⊢TC ⊥` (regcon's WF relativization + GU) | 430 |
| SU_main.v, Check.v | assembly, statement check | 48 |
| **total** | | **~2,060** |

The scoping text below is kept as written in phase 1 (the plan held; the actual size is 2.06k
lines, against the naive estimate of 2.83k).

---

## 0. Headline (target)

```coq
Theorem SU_equicons    : SUIR ⊢TC ⊥ <-> T_GU ⊢TC ⊥.          (* T_GU = ZFc + GU *)
Theorem SU_equicons_R  : SUIR ⊢TC ⊥ <-> T_GUR ⊢TC ⊥.         (* T_GUR = ZFc + Reg + GU *)
Theorem SU0_equicons   : SU0 ⊢TC ⊥ <-> T_GU ⊢TC ⊥.
(* all: Print Assumptions = Closed under the global context *)
```

`GU := ∀x ∃u (x ∈ u ∧ Gru u)`, with `Gru` transliterated from Metamath set.mm `df-gru`
(section 2). TG set theory includes foundation, so the `Reg` variant is the literal "ZF + every
set lies in a Grothendieck universe". `GU_reg_relcon : T_GUR ⊢ ⊥ → T_GU ⊢ ⊥` (section 4.4) proves
that the two headlines say the same thing.

## 1. The theory SU

### 1.1 Why the lead's UG_φ does not work

As specified, the schema is

    UG_φ := ∀p ∃w [ p∈w ∧ ∀x∈w ( x⊆w ∧ ∃W∈w ∀z (z⊆x → z∈W) )
                  ∧ ∀B∈w ∃C ( cov_φ(B,C) ∧ nx_φ(C) ∧ ( ∀a∈B ∃y (y∈w ∧ φ(a,y)) → C∈w ) ) ]

Here φ and its parameters are fixed outside `∀p ∃w`. Every instance is then a **ZF theorem**, by
reflection:

- Take `w := V_α` (or `L_α`, as `S_sound.v` already does for CP and GIC), with α a limit
  containing p and the parameters, and reflecting φ, `∃y φ(a,y)` and `χ(B) := ∃C (cov ∧ nx)`.
- χ(B) holds in V by collection. Reflection therefore puts such a C inside V_α, and cov and nx
  are absolute.
- So `C ∈ w` always holds, and the conditional clause has no strength.

`S_sound`'s argument would prove `SUIR ⊢ ⊥ → ZFc ⊢ ⊥` almost verbatim, so SUIR would be
equiconsistent with ZF. By Gödel's second theorem, `T_GU ⊢ ⊥ → SU0 ⊢ ⊥` would then be
unprovable unless ZF + GU is inconsistent.

**A second, independent gap.** Suppose the relation is quantified after w, and the clause is
"→ C ∈ w". Transitivity plus power containers plus image bounding still do not give `∪x ∈ w`.

- ZFC counterexample: κ a singular strong limit, λ = κ⁺, and
  `w = {x ∈ V_λ : every y ∈ TC({x}) has |y| < κ}`.
- w is transitive, closed under power containers and bounded images, and contains a cofinal
  ω-sequence S ⊆ κ. But `∪S = κ ∉ w`.
- That schema holds in V_θ for the least inaccessible θ, and it is even ZFC-provable.

So the fix must provide (a) a set quantified **after** w that φ may use, and (b) a union bound.

### 1.2 Proposed schema UG' (one designated inner variable f, union bound)

φ: `$0` = input a, `$1` = output y, `$2` = f (bound inside), `$(k+3)` = outer parameter k.

    UG'_φ := ∀p ∃w [ p∈w ∧ ∀x∈w ( x⊆w ∧ ∃W∈w ∀z (z⊆x → z∈W) )
               ∧ ∀f ∀B ( B∈w → ∃C ( ∀a∈B ∀y (φ(a,y,f) → ∃y' (φ(a,y',f) ∧ y'∈C))
                                  ∧ ∀y∈C ∃x φ(x,y,f)
                                  ∧ ( ∀a∈B ∃y (y∈w ∧ φ(a,y,f)) → ∃U (U∈w ∧ ∀y∈C ∀z∈y z∈U) ) ) ) ]

    SU0  = [ax_refl'; ax_sym'; ax_trans'; ax_eq_elem'] ∪ { forall_times n (ug φ) | closed }
    SUIR = SU0 + IR

An equivalent variant may be cheaper for the machine: keep "→ C∈w", and add a union container
`∃U∈w ∀t∈x ∀z∈t z∈U` to the per-x clause. Only S_def changes, and section 3 adapts in a few lines.

Coq (S_def style; de Bruijn indices worked out binder by binder):

```coq
Definition ug (phi : form) : form :=
  ∀ ∃ ($1 ∈' $0 ∧
       (∀ ($0 ∈' $1 → (∀ ($0 ∈' $1 → $0 ∈' $2)) ∧
                       ∃ ($0 ∈' $2 ∧ ∀ ((∀ ($0 ∈' $1 → $0 ∈' $3)) → $0 ∈' $1)))) ∧
       ∀ ∀ ($0 ∈' $2 → ∃ (
            (∀ ($0 ∈' $2 → ∀ (phi[$1 .: $0 .: $4 .: (fun k => $(7 + k))] →
                               ∃ (phi[$2 .: $0 .: $5 .: (fun k => $(8 + k))] ∧ $0 ∈' $3)))) ∧
            (∀ ($0 ∈' $1 → ∃ phi[$0 .: $1 .: $4 .: (fun k => $(7 + k))])) ∧
            ((∀ ($0 ∈' $2 → ∃ ($0 ∈' $5 ∧ phi[$1 .: $0 .: $4 .: (fun k => $(7 + k))]))) →
             ∃ ($0 ∈' $4 ∧ ∀ ($0 ∈' $2 → ∀ ($0 ∈' $1 → $0 ∈' $2))))))).
(* binders: ∀p ∃w | ∀f ∀B | ∃C | ∀a ∀y ∃y' / ∀y ∃x / ∀a ∃y / ∃U ∀y ∀z *)

Inductive SU0 : form -> Prop :=
  | SU0_base phi : In phi EqAx -> SU0 phi
  | SU0_ug phi n : closedf (forall_times n (ug phi)) -> SU0 (forall_times n (ug phi)).
Definition SUIR phi := SU0 phi \/ phi = ax_ir.
```

Facts that make the old toolkit carry over:

- `ug φ` gives CP (drop the rest).
- It gives GIC for any φ that ignores f: take p := B, and f := anything.
- So `SU0 ⊢TC a` holds for every S0 axiom a. All of `S_raw`, `S_quot` and `S_ax` apply verbatim,
  through a cut.

## 2. Gru and GU (vetted source: Metamath set.mm `df-gru`)

> df-gru: ⊢ Univ = {u ∣ (Tr u ∧ ∀x∈u (𝒫x ∈ u ∧ ∀y∈u {x,y} ∈ u ∧ ∀y∈(u ↑m x) ∪ran y ∈ u))}
> (set.mm; "A Grothendieck universe is a set that is closed with respect to all the operations
> that are common in set theory", after SGA4 Exposé I.)

Line-by-line transliteration. `A ∈ u` for a class term A is read by df-clel as ∃s (s = A ∧ s ∈ u).
`y ∈ (u ↑m x)` is `y : x ⟶ u` (df-map, df-f, df-fn, df-fun), which unfolds to
`Fun0 y ∧ Dom0 y x ∧ ran y ⊆ u`. The primitives come from `zf/zfc/Z_base.v` (OP0 = Kuratowski,
as in set.mm df-op).

```coq
Definition Gru (u : term) : form :=
  Trans0 u ∧                                                     (* Tr u *)
  ∀ ($0 ∈' u`[↑] →                                               (* ∀x∈u *)
     (∃ ($0 ∈' u`[↑]`[↑] ∧ ∀ ($0 ∈' $1 ↔ Sub0 $0 $2))) ∧          (* 𝒫x ∈ u *)
     (∀ ($0 ∈' u`[↑]`[↑] → ∃ ($0 ∈' u`[↑]`[↑]`[↑] ∧ Pair0 $2 $1 $0))) ∧   (* ∀y∈u {x,y} ∈ u *)
     ∀ ((Fun0 $0 ∧ Dom0 $0 $1 ∧ ∀ ∀ (App0 $2 $1 $0 → $0 ∈' u`[↑]`[↑]`[↑]`[↑])) →  (* y : x ⟶ u *)
        ∃ ($0 ∈' u`[↑]`[↑]`[↑] ∧                                  (* ∪ran y ∈ u *)
           ∀ ($0 ∈' $1 ↔ ∃ ((∃ App0 $4 $0 $1) ∧ $1 ∈' $0))))).
Definition GU : form := ∀ ∃ ($1 ∈' $0 ∧ Gru $0).
Definition T_GU  phi := ZFc phi \/ phi = GU.
Definition T_GUR phi := (ZFc phi \/ phi = ax_reg') \/ phi = GU.
```

Search result: there is no universe or inaccessible definition in the vendored library,
zf/stdzf, zf/regcon, zf/zfc or zf/m254.

## 3. Completeness: T_GU ⊢ ⊥ → SU0 ⊢ ⊥

1. `ZFc + GU ⊢ ⊥ → ZF0 + INF_lib + GU0 ⊢ ⊥`, by `tprv_cut`, `inf_or_to_zf`, and the ZF lemma
   `gru0_gru : ZF0 ⊢ ∀u (Gru0 u → Gru u)`. Here
   `GU0 := ∀x ∃u (x∈u ∧ Gru0 u)` and

       Gru0 u := Tr u ∧ ∀x∈u ∃W∈u ∀z (z⊆x → z∈W)
               ∧ ∀f ∀B∈u ( ∀a∈B ∃y∈u App0 f a y →
                           ∃C ( ∀a∈B ∀y (App0 f a y → ∃y'(App0 f a y' ∧ y'∈C))
                                ∧ ∃U∈u ∀y∈C ∀z∈y z∈U ) )

   This is the w-clause of UG' read in ZF, with φ := `App0 f a y`.
2. `gru0_gru`, in ZF:
   - subsets of members are members (`s ⊆ x ⇒ s ∈ W_x ⇒ s ∈ u`);
   - 𝒫x ⊆ W_x;
   - `{x,y}`: f := {(∅,{x}), ({∅},{y})} over B := {∅,{∅}} ∈ u, so `{x,y} ⊆ U`;
   - `∪ran f`: B := x and the same f; `∪ran f` is separated from U.
3. The quotient. `qt_tprv` with `Eqv`/`Mem` from S_quot needs `SU0 ⊢TC qtS a` for each axiom:
   - ZF0 and INF_lib come from `S_ZF0inf` plus `SU0 ⊢ S0`, by cut;
   - `qtS GU0` uses one closed instance, `ug φ_U` with `φ_U := qtS (App0 $2 $0 $1)`.
   The raw w is the interpreted universe:
   - Tr: raw transitivity and `mem_r`.
   - Power containers: an interpreted subset is ≈ its raw trace (as in `S_power`), which lies in
     the raw W.
   - Family clause: the interpreted B is ≈ a raw B' ∈ w, and the interpreted y ∈ u is ≈ a raw
     y' ∈ w. φ_U is ≈-invariant (`qt_inv`). The raw `∪C ⊆ U` gives the interpreted one.
   IR is not used.

## 4. Soundness: SUIR ⊢ ⊥ → T_GUR ⊢ ⊥ → T_GU ⊢ ⊥

### 4.1 Route decision: cumulative hierarchy V_α, not L

- **L route (rejected).** It needs L_κ to be a universe in L: every constructible subset of
  x ∈ L_κ must appear before κ. Without condensation (GCH in L) we cannot even bound one
  subset's stage below κ. Condensation is a large new development.
- **V route (chosen).** Build `VV α Y` ("Y = V_α", with V_α = ⋃_{β<α} 𝒫(V_β)) with `Z_trec`,
  exactly as `Z_L` builds `LL` (Def replaced by 𝒫). Relativize the SUIR derivation to the class
  `Vform x := ∃α ∃Y (Ord0 α ∧ VV α Y ∧ x ∈ Y)` with `Z_rel.transfer`.
  - Relativizing (instead of proving V = ⋃V_α) avoids transitive closure and ∈-induction
    entirely.
  - Inside ZF + Reg the ordinal toolkit (`Z_ord`, `Z_trec`, `ord_collect_g`, `least_ord`) is
    already available.

### 4.2 The axioms in Vform (inside ZF + Reg + GU)

- **Equality axioms**: trivial.
- **IR**: `no_self_g`.
- **UG'**: given p ∈ V_α:
  - GU gives a universe U ∋ α. Let κ := U ∩ On (separation; an ordinal; a limit, since
    α+1 ⊆ 𝒫α ∈ U).
  - `V_β ∈ U` for β < κ (ordinal induction; limit stage = family union of β ↦ 𝒫V_γ), so
    `V_κ ⊆ U`.
  - w := V_κ, so p ∈ w. The CP clause holds with W := V_{β+1} ∈ V_κ.
  - Family clause: as `collect_L`, but over the V_δ. Take g := the **least** ordinal such that
    every a ∈ B with a Vform-witness has one in V_g. Then C := {y ∈ V_g | ∃a∈B φ^V(a,y,f)}, which
    gives cov and nx.
  - If every a ∈ B has a witness in V_κ: B ∈ U, and the least stages δ_a form a set function
    B → κ ⊆ U. Gru's family-union clause puts `sup δ_a ∈ U`, so g ≤ sup < κ. Then `∪C ⊆ V_g ∈ w`.

### 4.3 What is reused

`Z_trec.rec_ex/rec_agree` (via an `SV` step formula), `Z_ord`, `Z_rel.transfer/rel_ft`, the
`collect_L` proof pattern from `S_sound`, and `MinZF.collect`.

### 4.4 Regularity: `GU_reg_relcon : T_GUR ⊢TC ⊥ -> T_GU ⊢TC ⊥`

regcon's WF relativization (`regcon/Main.v`, function signature) is extended by the one axiom GU.
Steps:

- **(a)** `step1` with GU embedded (trivial; GU has no function symbols).
- **(b)** In regcon's proof of `regularity_relcon`, generalize ⊥ to the extra axiom: rel_prv
  gives `ZFc_fn + GU ⊢ ⊥` from `rel_axiom` plus `ZFc_fn + GU ⊢ relw (embed GU)`.
- **(c)** `relw (embed GU)`. Its proof in minZF:
  - w := {y ∈ U | WF y} ∈ WF;
  - Gru is Δ0 in u, x, f, so `Z_rel.D0_abs` applies for the transitive class WF;
  - power set, pair and ∪ran of WF sets are WF.
  It is then moved to the function signature by `prv_embed` (WF.v's `WF` is ∈-only, so
  `relw ∘ embed = embed ∘ rel WFm`).
  - The minZF facts about WFm (transitive class, closure lemma, closure under 𝒫, pairs and ∪)
    come from regcon's function-signature lemmas through `rm_const_prv`.
  - This needs one equivalence lemma, `rm_const_embed : minZFeq' ⊢ rm_const_fm (embed φ) ↔ φ`
    (induction on φ), which (d) also needs.
- **(d)** `step3` with GU: `rm_const_prv` plus `rm_const_embed`.

Fallback if (c)'s transfer gets ugly: prove the WFm facts directly in minZF, about 150 lines with
stdzf tactics.

### 4.5 AC (phase 2, scope only)

`Con(ZF+GU) → Con(ZFC+GU)` via L needs `(GU)^L`, that is, L_κ is a universe in L. This needs
the condensation lemma, which is a new, large development: Σ1-Skolem hulls of L_α, the Mostowski
collapse, and `L_α ∩ 𝒫(L_β) ⊆ L_{|β|⁺}`. The zf/zfc L infrastructure covers the hierarchy
and Def. It does not cover hulls or collapses. Estimate: 2–4k lines, high risk. Not in phase 1.

## 5. File plan

Calibrated estimate = naive ÷ 3.

| file | content | naive | calibrated |
|---|---|---|---|
| SU_def.v | `ug`, SU0, SUIR, `Gru`, `GU`, `Gru0`, `GU0`, T_GU, T_GUR; closedness | 150 | 60 |
| SU_s0.v | `SU0 ⊢TC a` for every S0 axiom (CP, GIC with shifted φ); `S0_to_SU0` cut | 150 | 60 |
| SU_gru.v | `gru0_gru` in ZF0 (subset closure, 𝒫, pairs, ∪ran) | 350 | 130 |
| SU_quot.v | `SU0 ⊢ qtS GU0` (raw w → interpreted universe) | 300 | 120 |
| SU_complete.v | `GU_to_SU0 : T_GU ⊢TC ⊥ -> SU0 ⊢TC ⊥` | 80 | 40 |
| SU_V.v | `SV`, `VV`, `Vform`; V_α transitive, monotone, `V_{β+1}=𝒫V_β`, existence/uniqueness | 450 | 180 |
| SU_univ.v | universe facts: κ = U∩On limit ordinal, V_β ∈ U for β<κ, V_κ ⊆ U, sup bound | 350 | 140 |
| SU_sound.v | SUIR axioms in Vform; `SU_to_ZFRGU : SUIR ⊢ ⊥ -> T_GUR ⊢ ⊥` | 450 | 180 |
| SU_reg.v | `GU_reg_relcon` (4.4) | 450 | 200 |
| SU_main.v, Check.v, build.py | assembly, statement check | 100 | 60 |
| **total** | | **2,830** | **~1,200** |

## 6. Risks

1. **The interface (blocking).** UG' or its variant must be accepted by the lead and the machine
   agent. Machine cost: one extra inner variable `f` plus `∃U∀∀`.
2. **SU_reg (4.4).** This is signature plumbing: the `rm_const`/`embed` equivalence and the WF facts
   in minZF. It is mechanical but fiddly. The fallback is a direct minZF WF development.
3. **De Bruijn bookkeeping in `ug`.** The schema has 3 φ-occurrences at different depths plus the
   `tot` one. Mitigation: a `ug_use` lemma (as `gic_use`) proved once with `form_subst_eq`.
4. **SU_univ's sup argument.** It needs the least-stage function B → κ as a set (replacement on
   `least` formulas) and Gru's family clause with Fun0/Dom0. These are standard `Z_trec`-style
   steps.
5. **Gru fidelity.** The transliteration uses the Z_base primitives, so a reviewer must also check
   OP0/Fun0/Dom0/App0 (they are Kuratowski and set.mm-standard).
