# zf/m254tg/ac: AC on top of ZF + GU (Gödel's L with condensation)

## Status (2026-10-14): DONE, `python build.py` → CHECK PASS (all three headlines Closed)

The plan below held without statement changes; one fix was needed: `lim_above` got the hypothesis ω ∈ κ.
The actual size is 3.78k lines, against the naive estimate of 3.2k (calibrated 1.1–1.6k, which was
too low this time). By file: hull 951, coll 564, univ 458, cond 405, tup 402, gu 328, cwo 292,
main 126, rec 117, iso 115. Wired into e2e/E2E_TG.v as `tg296_halts_iff_ZFCGU` and
`tg296_halts_iff_ZFCRGU`, with literal statement checks in ../check.py.

## 0. Target

```coq
Theorem acgu_reg_relcon : T_ACGUR ⊢TC ⊥ -> T_GUR ⊢TC ⊥.                 (* AC_main.v *)
Theorem ZFCGU_equicons  : T_ACGU  ⊢TC ⊥ <-> T_GU ⊢TC ⊥.
Theorem ZFCRGU_equicons : T_ACGUR ⊢TC ⊥ <-> T_GU ⊢TC ⊥.
(* T_ACGU  phi := (ZFc phi \/ phi = ax_ac) \/ phi = GU
   T_ACGUR phi := ((ZFc phi \/ phi = ax_reg') \/ phi = ax_ac) \/ phi = GU
   ax_ac = zf/zfc Z_wo.ax_ac (Zermelo choice-set form, the one in ZFC_equicons) *)
```

E2E_TG.v adds

```coq
Theorem tg296_halts_iff_ZFCGU  : halts tm c0 <-> (fun phi => (ZFc phi \/ phi = ax_ac) \/ phi = GU) ⊢TC ⊥.
Theorem tg296_halts_iff_ZFCRGU : halts tm c0 <-> (fun phi => ((ZFc phi \/ phi = ax_reg') \/ phi = ax_ac) \/ phi = GU) ⊢TC ⊥.
```

Chain: halts ↔ T_GU ⊢⊥ (existing). T_GU ⊆ T_ACGU ⊆ T_ACGUR (monotone).
T_ACGUR ⊢⊥ → T_GUR ⊢⊥ (new, `acgu_reg_relcon`) → T_GU ⊢⊥ (`GU_reg_relcon`, SU_reg.v).

## 1. Route

zf/zfc's `ac_relcon` relativizes a derivation to `Lform` and proves every ZF+Reg axiom (`axL_ZFR`) and AC
(`acL_ex`) inside L. We add one axiom, GU, and prove inside ZF + Reg + GU that `rel Lform GU` holds.

**Witness.** Given x ∈ L at stage a, GU (in V) gives a universe U ∋ {a, ω}. Put κ := U ∩ On (`kappa_ex`,
SU_univ). κ is a limit > ω, and u := L_κ ∈ L contains x.

**Gru^L(L_κ).** Each clause is handled in the same way: the L-witness W exists because L ⊨ ZF.
The ZF theorems T_pow, T_pair and T_un ("∪ran f exists") are transferred to L as in Z_ac.rel_T. Their
relativized form is literally the relativized Gru clause. Then:
- W ⊆ L_κ: every element of W is a constructible subset of some L_e with e < κ (COND below).
- W ∈ U, from V-Gru(U): 𝒫x ∈ U, {x,y} ∈ U, ∪ran f ∈ U. For the last one, f's values are in L_κ ⊆ U.
- BND: W ∈ U and W ⊆ L_κ give W ⊆ L_c for some c < κ. The map w ↦ least stage is a set function
  W → κ (`fn_build`), and Gru's family-union clause bounds its sup below κ.
- COND applied to W itself gives W ∈ L_κ.

This is modelled on SU_reg.GU_WF.

**COND (condensation, the only new mathematics).** If y ∈ L and y ⊆ L_c with c < κ, then y ∈ L_e for
some e < κ.
1. c' := max(c, ω). A limit ζ with c' < ζ < κ comes from ω-recursion of successor plus Gru's family
   union. The index set I := L_ζ ∈ U is closed under ordered pairs.
2. **Hull.** X ⊆ L contains L_{c'} ∪ {y} and is closed under ordered pairs and under *canonical
   witnesses* for one formula c_ps. Canonical witness: the least ξ with a witness in L_{ξ+1}, then the
   least witness in Z_wo's canonical well-order of L_{ξ+1}. No choice is needed.
   X = ran H, where H = ⋃_n H_n is an *indexed* family. H_{n+1} = H_n ∪ {((1,(s,t)), (H s, H t))} ∪
   {((2,s), sk(H s))}, with base entries ((0,a), a), built by ω-recursion. dom H ⊆ I, so the hull is
   "small" (a set function from a member of U) without any cardinal arithmetic.
3. **Tarski–Vaught.** c_ps is the tagged disjunction of the pieces of `Lform` and of
   ψ_ext = ∃z ¬(z∈a ↔ z∈b): piece i gets numeral tag i, and K-tuples of parameters are coded as nested
   ordered pairs. X is closed under pairs and contains the numerals, so every piece is witness-closed.
   Z_refl.TV (reused as is) then gives rel Lform φ ↔ relS X φ for φ = Lform[y], ψ_ext.
4. **Collapse.** By ψ_ext, X is extensional. The Mostowski collapse π : X ≅ M (M transitive) is built
   by Z_trec recursion along L-stages: π restricted to X ∩ L_{ξ+1}, from π on X ∩ L_ξ. Regularity gives
   that π is injective and fixes L_{c'} pointwise, hence also fixes y.
5. **Transfer.** In L, y ∈ L holds: rel Lform T1 gives (L_a)^L = L_a, as in Z_ac. TV gives relS X (InL y).
   The isomorphism lemma gives relS M (InL y). So there are a, Y' ∈ M with relS M (Ord0 a ∧ LL a Y' ∧
   y ∈ Y'). Σ-upward absoluteness for the transitive *set* M (Sg_upS, a relS copy of Z_rel.Sg_up) gives
   LL a Y' and y ∈ Y'.
6. **Smallness.** succ(a) ⊆ M is covered by i ↦ π(H(i)), whose domain is ⊆ I ∈ U. SURJ: a set function
   from a member of U covering an ordinal d forces d < κ. If not, restrict it to the preimage of κ; its
   range union is κ ∈ U, a contradiction. So a < κ.

This needs no fine structure, no Löwenheim–Skolem with choice, and no "V = L is absolute for transitive
models of a fragment". Absoluteness of L_a comes from LL being Σ (Z_sg) plus uniqueness of L_a in V,
exactly as in Z_ac.

**Why not cheaper.** L_κ is the only natural u. Any u = L_λ needs P^L(L_α) ⊆ L_λ for α < λ, plus
regularity of λ for constructible f. Closure points of α ↦ stage(P^L(L_α)) have cofinality ω in L,
unless λ is a universe ordinal, and for λ = κ the closure is exactly COND. Alternatives were checked
and rejected:
- HOD: Gru^HOD(V_κ ∩ HOD) is trivial, but HOD ⊨ ZF+AC is a redevelopment the size of zf/zfc.
- L[K]: has the same condensation issue.
- "U ≺_Σ1 V" (Lévy): needs a hull and a collapse anyway.

## 2. Files (namespace M254TGA, dir zf/m254tg/ac; imports ZFC = zf/zfc, M254TG = settheory)

| file | content | key statements |
|---|---|---|
| AC_rec.v | generic ω-recursion for a closed total functional step (Scl pattern) | `omrec_ex`, `omrec_zero`, `omrec_succ` |
| AC_univ.v | κ = U∩On: limit, κ∉U, L_c ∈ U, BND, SURJ, limit above c, L_ζ closed under OP | `kap_lim`, `LL_inU`, `bnd`, `surj`, `lim_above`, `LL_op` |
| AC_cwo.v | canonical well-order CWO ξ W of L_{ξ+1}; canonical witness CanW c x w | `cwo_ex/unique/wo`, `canw_ex/unique/L/sat` |
| AC_hull.v | indexed hull: `hull_ex` (H, X with HullP) | `hull_ex` |
| AC_tup.v | tuples TupF, decoded pieces, tagged formula `cps`, `ps_PH` (hull closure → Z_refl.PH) | `ps_PH` |
| AC_coll.v | Mostowski collapse of an extensional X ⊆ L | `coll_ex`, `coll_inj`, `coll_iso`, `coll_fix` |
| AC_iso.v | relS transfer along an isomorphism; D0_absS / Sg_upS for transitive sets | `iso_relS`, `Sg_upS` |
| AC_cond.v | COND | `cond` |
| AC_gu.v | T_pow/T_pair/T_un; (GU)^L | `guL` |
| AC_main.v, Check.v | assembly (Z_main pattern + MinZF.collect), corollaries | `acgu_reg_relcon`, equicons |

Instance lists follow zfc's convention: `Ax_X` lists of closed sep/rep instances with `Ax_X_ok : ZFR`;
generic files take `Ax_X c` for a formula parameter c.

## 3. Estimate

Naive ~3.2k lines: rec 120, univ 350, cwo 250, hull 600, tup 350, coll 550, iso 200, cond 300, gu 300,
main 150. Calibrated (÷3 rule, mine historically run 3–10x high): **~1.1–1.6k lines**. With 5–6
parallel Opus agents, about one working day.

## 4. Risks

1. **Hull bookkeeping (AC_hull).** The functionality invariant on the indexed family, and set
   existence of the next stage (replacement over F and F×F). This is mechanical.
2. **Formula size.** c_ps contains every quantified subformula of rel Lform (LL ...), several hundred
   pieces. Everything is generic in ps; only `fbcomp` (vm_compute) touches the concrete formula. The
   mitigation is to keep cps/LL/Lform Opaque and never cbn them.
3. **De Bruijn in AC_tup** (K-tuple decoding). Mitigation: mirror Z_cl's EnvF (same shape with OP0).
4. **Collapse recursion (AC_coll).** It needs X ⊆ L_δ (`L_bound`, Z_axL) and the stage
   decomposition L_ξ = ⋃_{e<ξ} L_{e+1}.
