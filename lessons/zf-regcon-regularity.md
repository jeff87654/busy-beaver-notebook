---
name: zf-regcon-regularity
description: "Con(ZF-Reg)->Con(ZF) formalized in undecidability-library FOL syntax (zf/regcon, 2026-10-10); library ZFeq has open schema instances (pitfall)"
metadata:
  node_type: memory
  type: project
  originSessionId: 7b95bc12-778b-4d66-a6e9-e51940c89aa8
  modified: 2026-10-11T00:45:09.407Z
---

zf/regcon (Coq 8.20, prefix RegCon, deps only zf/stdzf/ext/undec-8.20 read-only): `regularity_relcon : ZFcReg ⊢TC ⊥ -> ZFc ⊢TC ⊥`, closed under Print Assumptions (done 2026-10-10, ~1300 lines, `python build.py` -> CHECK PASS).

- Library ZF has NO regularity axiom; ax_reg defined in Main.v.
- minZF version (lead's target) in MinZF.v: regularity_relcon_min' works for any T with ZFcl_min ⊆ T ⊆ ZFcl_all (closures of minZFeq); transfer via library prv_embed/embed_ZF' and rm_const_prv/minZF_sep/minZF_rep.
- Pitfall: library ZFeq includes ax_sep/ax_rep as OPEN formulas (params free); ND cannot generalize them, so ZFeq likely does not prove closed parametric instances. Hence ZFc := ZFeq' + forall_times closures. `ZFeq_ZFc` (easy direction) proved; converse open.
- Proof tools that worked: AllI_named/ExE_named "forall term" style, builders with `Arguments ... : simpl never` + subst lemmas in a rewrite DB, `bounded_comp_eq; compute; repeat split; lia` for boundedness.

**Why:** closes the last step of the "TM halts iff ZF inconsistent" chain (see [[bb8-champion-subtree-lead]] for the busy-beaver context).
**How to apply:** chain must target ZFc, not raw ZFeq, unless someone proves ZFeq ⊢ closures.
