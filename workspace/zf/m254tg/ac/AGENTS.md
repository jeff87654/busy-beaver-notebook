# zf/m254tg/ac: working notes for proof agents

Goal: `AC_main.acgu_reg_relcon : (ZFc + Reg + AC + GU) ⊢TC ⊥ -> (ZFc + Reg + GU) ⊢TC ⊥`, by relativizing to
Gödel's L (zf/zfc does ZF + Reg + AC; we add GU). Read DESIGN.md (route) and the header comment of your
file. The assembly (AC_main.v) is already proved from the statements of the other files. The work left
is to prove the `Admitted` lemmas.

## Files (dependency order)

| file | content |
|---|---|
| AC_rec.v | ω-recursion (any ordinal domain) for a closed total functional step `phG` (Z_cl.Scl pattern) |
| AC_univ.v | U universe, κ = U∩On (`Kap`), `InLk`, L_c ∈ U, `bnd`, `surj`, `lim_above`, `LL_op`, `LL_num` |
| AC_cwo.v | canonical well-order `CWO` of L_{ξ+1} (Z_wo's Sout recursion), canonical witness `CanW` |
| AC_tup.v | tuples `TupF`, decoded pieces, tagged formula `cps`, `ps_PH` (→ Z_refl.PH) |
| AC_hull.v | indexed Skolem hull `hull_ex` |
| AC_iso.v | `iso_relS`, `D0_absS`, `Sg_upS` |
| AC_coll.v | Mostowski collapse `coll_ex` etc. |
| AC_cond.v | condensation `cond` |
| AC_gu.v | `guL : rel Lform GU`; ZF theorems T_pow/T_pair/T_un |
| AC_main.v, Check.v | assembly (done) |

## Conventions (as in zf/zfc; read zf/zfc/AGENTS.md too)

- Contexts are an abstract `G : list form` with `incl ZF0base G`, `In ax_reg' G`, `In ax_om' G`,
  `incl Ax_wo G` (zf/zfc Z_wo; contains Ax_L ⊇ Ax_cl ⊇ Ax_ord ⊇ Ax_prim), and the file's own instance
  list. Instance lists are lists of closed separation/replacement instances (`forall_times n (ax_sep' φ)`
  with `fb (S n) φ`, `forall_times n (ax_rep' φ)` with `fb (S (S n)) φ`, `least_inst`, `oc_insts`,
  `rec_insts S`, `SU_fn.fnR` instances for `fn_build`), with an `_ok` lemma proving every member `ZFR`
  (`ZFR_sep`/`ZFR_rep` + `fbcomp`). **You may extend your own file's instance list(s) and must keep the
  `_ok` lemma proved.** Lists of generic files take the formula as parameter (`Ax_hull c`).
- Predicates are HOAS functions `term -> ... -> form`, `Arguments ... : simpl never`, with a
  substitution lemma in the rewrite database `fsub` (`psubst Name` proves most; for definitions with a
  formula parameter c, it is read through `Std_setrec.Rel2 c v x`, which commutes with substitution:
  `Std_setrec.Rel2_subst`). `simp`/`simp_in` normalize substitutions.
- PITFALL: `∧` and `∨` are LEFT associative. `a ∧ b ∧ c` = `(a ∧ b) ∧ c`. `→` is right associative,
  `¬ A` = `A → ⊥`. Parenthesize `↔` against `∨`.
- PITFALL: write `∀ (∀ (...))`, never `∀ ∀ ...`.
- PITFALL: keep big definitions opaque: never `cbn`/`unfold` LL, Lform, Def0, Cl, cps, CanW, ...
  unless you mean it; use the existing access lemmas. Never unfold hypotheses that hold explicit ND
  context lists.
- Use fully qualified names (`Std_setrec.Rel2`, `Std_setrec.GTot`) where busycoq/stdzf names clash.
- Proof style: zf/stdzf/coq/Std_setnd.v tactics (fintro, fall, fex, finst, fexists, fsplit, fdestr,
  fleft, fright, fcases, fapply, fmp, fabsurd, fcontra, fassert, fhave, fobtain), Std_setbase.v
  (feq, fmem, frew, frew_in, sep_use, rep_use, leib, leib_gen, elem_cong, ext_rule), worked examples
  in zf/zfc (Z_cl.v, Z_L.v, Z_wo.v, Z_refl.v, Z_axL.v, Z_ac.v) and zf/m254tg/settheory (SU_univ.v,
  SU_fn.v, SU_reg.v GU_WF, SU_sound.v).
- Classical object-level reasoning: `XM_rule`, `DN_rule`, `fcontra`. The meta level stays constructive.
- No `Admitted`/`admit`/`Axiom`/`Parameter` in the end. No axioms through imports.

## Rules

1. Edit ONLY your own file(s). Do not change existing statements or definitions (other agents use them),
   except your instance lists (`Ax_*`) and `_ok` lemmas. You may add helper definitions and lemmas
   freely. If a statement is wrong or unprovable, do not silently change it: add a corrected variant
   next to it, prove what you can, and explain the problem precisely in your report (and message the
   lead `m254tg-ac` with SendMessage as soon as you find it, since other agents build on it).
2. BUILD only with `python C:/Users/jeffr/Downloads/bb8/zf/m254tg/ac/build.py File.v` (Idle priority, at
   most 4 coqc machine-wide via .locks). Never run coqc directly; no other CPU-heavy processes.
3. Other agents build against your file AT THE SAME TIME, so your real file must ALWAYS compile. Develop
   in a copy `AC_X_wip.v` (it imports the real upstream files), and copy compiling progress into the
   real file (unproved lemmas stay `Admitted` there), building it once to confirm. Delete the wip file at
   the end.
4. Do not touch frozen dirs: zf/zfc, zf/stdzf*, zf/regcon, zf/m254, zf/m254tg/{machine,tm,prog,logic,
   settheory}. Import or copy from them.
5. Final report: which lemmas are proved, what is still Admitted and why, your instance lists, statement
   problems, and the `Print Assumptions` of your main lemmas (only upstream Admitted lemmas allowed).
