# m254tg logic layer (zf/m254tg/logic/coq, root M254TGL)

**Status 2026-10-14: CLOSED.** `python coq/build.py` builds everything at Idle priority, one coqc at a
time (clean build ~1m40s). Every top theorem prints "Closed under the global context".

```coq
Theorem L1_TG         : enum_tg_halts <-> thm_tg 1.                                     (* L1_TG.v *)
Theorem bridge_tg     : thm_tg 1 <-> SUIR ⊢TC ⊥.                                        (* BridgeTG.v *)
Theorem enum_tg_SUIR  : enum_tg_halts <-> SUIR ⊢TC ⊥.
Theorem enum_tg_GU    : enum_tg_halts <-> T_GU  ⊢TC ⊥.     (* Logic_GU_TG.v, with settheory SU_equicons *)
Theorem enum_tg_GUR   : enum_tg_halts <-> T_GUR ⊢TC ⊥.
```
SUIR, ug, T_GU (= Std_iface.ZFc + GU) are m254tg-settheory's (`zf/m254tg/settheory`, root M254TG).
What is still needed for the TM statement: L2 (`rm_halts <DAG of m254tg_wade.tm> <-> enum_tg_halts`,
m254tg-prog) and the TM layer.

| file | content |
|---|---|
| CodesTG.v | re-exports zf/m254 `Codes254` (P, unP, wim.., rows: the same constants); the new `bundle_tg` (w = `S c`, f = 0) and `bundle_tg_flat` (= the term generated from the validated RPN AST, by reflexivity) |
| EnumTG.v | **FROZEN interface** (sha256 794a6ce1…65e4): Enum254 with `gate` using `bundle_tg`; `enum_tg_halts` |
| ThmTG.v, L1_SoundTG.v, L1_CompTG.v, L1_TG.v | mechanical ports (macros unchanged) |
| CDTG.v, Comp_PropTG.v | ports; B6a is now the right conjunct of the bundle directly (V= ∧ V∈) |
| BundleTG.v | named bundle `BW a b c phi`; `D_bundle_tg : c<>a -> c<>b -> D (bundle_tg a b c) = BW a b c (D c)` |
| SoundBWTG.v | `V_BW : c<>a -> c<>b -> fr c phi = false -> fr (S c) phi = false -> Fvalid SUIR (BW a b c phi)`; cases b = S c (IR guard), a = b (empty C from UG'(⊥), U := p), general (instance UG'(thetaW3), matrix map a↦$0, b↦$1, 0↦$2, v↦$(3+v)), with the c+1 = a weakening H'→H via transitivity |
| SoundTG.v | `thm_V`, `thm_to_SUIR` (rows as in Sound254; `D_fr_Sself : fr (S c) (D c) = false`) |
| Comp_BundleTG.v | `SUIR_to_thm`: TB = closures of tau-theorems; EqAx, IR; every `forall_times n (ug th)` from the closure of `BW 1 3 c (Wal q (tr etaU th))`, etaU: in↦1, out↦3, f↦0, k↦2k+5 |
| BridgeTG.v, Logic_GU_TG.v | assembly |

Dependencies (read-only): zf/m254/logic/coq (M254L: Codes254, Wff254, Bundle254 side lemmas),
zf/m254/settheory (M254S: `ax_ir`), zf/stdzf, zf/regcon, zf/zfc.
