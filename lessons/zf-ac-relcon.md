---
name: zf-ac-relcon
description: "zf/zfc — object-level Con(ZF)->Con(ZFC) via L in the Kirst-Hermes Coq library, DONE 2026-10-11 (CHECK PASS, closed); design + pitfalls"
metadata:
  node_type: memory
  type: project
  originSessionId: 7b95bc12-778b-4d66-a6e9-e51940c89aa8
  modified: 2026-10-11T19:29:14.846Z
---

zf/zfc (2026-10-11): `ac_relcon : (ZFc+Reg+AC) ⊢TC ⊥ -> (ZFc+Reg) ⊢TC ⊥`, plus `ac_reg_relcon` / `zfc_relcon` (composed with regcon's Link). Print Assumptions closed. `python build.py` prints CHECK PASS. About 7.6k lines, clean build ~15 min. Integrated into the release package zf/stdzf_r3_repo, which becomes ZF/stdzf_r3/ in PR #13. It adds zfc/, and E2E335 gains zf335_halts_iff_ZFC / _ZFC_reg (halts <-> (ZFc+AC) resp. (ZFc+Reg+AC) ⊢TC ⊥) via ZFC_equicons / ZFCReg_equicons. Final fresh check PASS in 3002 s (stdzf 6, zfc 5, 335 6, 336 4). Built in roughly one session: I wrote the skeleton with all statements Admitted, validated end-to-end, then 8 parallel Opus agents filled the files.

Design: Def(A) = Cl(A∪{A}) ∩ P(A), where Cl is closure under 8 Delta_0 ops on finite environments. This avoids codes/Sat, and only "definable ⊆ Def" is needed. Absoluteness of L_α comes only from LL being syntactically Sigma (checked by vm_compute, `sgcomp`), Sg_up, and uniqueness in V. V=L is not needed.

**How to apply / pitfalls:** the library's `∧` is LEFT associative, so a bounded ∃ with several conjuncts needs parentheses. Write `∀ (∀ (...))`, never `∀ ∀`. As a teammate I can only spawn synchronous subagents, so launch them in one batch. Their handbacks come back empty, so read the files to see the result. Related: [[bb8-hunt-working-style]].
