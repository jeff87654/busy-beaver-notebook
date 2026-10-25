---
name: zfc254-logic-scoping
description: "zfc_254 (third-party 254-state ZFC machine) program/logic-layer scoping 2026-10-13 - coding differs from Wade, spec validated, quotient interpretation is the crux"
metadata:
  node_type: memory
  type: project
  originSessionId: a872c5f9-7ee6-45a6-89ec-58594d6fffa6
  modified: 2026-10-14T02:58:23.454Z
---

zf/m254/logic/ (DESIGN.md + tools) scoped the program and logic layers of the third party's zfc_254.tm (2026-10-13).

- Their coding is NOT Wade's: 4*P(x,y)+tag with dual Cantor P = tri(x+y)+y, no primitive negation (¬A = A→F, F = code 1 = Rel(0,0) = v0∈v0). Halts in NIP when the cache (param2) = 1.
- Their CONTROL_GRAPH.json source_graph is exactly bisimilar to the Wade-TMBuilder compilation of source.py; the final graph equals it up to commuted incs (flatten.py).
- spec.py enum_step validated (validate.py ALL OK); compiler.py macros validated; AX pushes old current, GEN of cache, rho8..rho1, gated bundle (CP container + GIC + atomic vacuity).
- IR (∀x ¬x∈x) needed for soundness of rho1/rho6 (F read as v0∈v0) and bundle collisions.
- Crux/risk: completeness needs the bisimulation-quotient interpretation of ZF in S0 = CP+PSC (paper sec 5), ~1.2-1.8k calibrated lines; soundness needs ranks/Collection in ZFc_reg.

**Why:** next sessions on m254 should start from this design rather than re-deriving it.
**How to apply:** read zf/m254/logic/DESIGN.md; relates to [[zf-machine-verification]], [[zf-ac-relcon]], [[zf-regcon-regularity]], [[formalization-estimates-too-high]].

Update 2026-10-13 (later): logic layer BUILT and CLOSED in zf/m254/logic/coq (~2k lines): L1_254 (enum254_halts <-> thm254 1), Bridge254 (thm254 1 <-> SIR ⊢TC ⊥), Logic_ZFc254 (enum254_halts <-> ZFc ⊢TC ⊥ via settheory S_equicons), all Print Assumptions closed. Lessons: keep wim/wel/wal/weq/P Opaque in Coq (concrete-numeral conversion explodes); never unfold/cbn hypotheses whose ND context is an explicit list (breaks ctx_push weakening) — use In-premise helper lemmas; Łukasiewicz-axiom derivations of S/B need the C++ CD prover (logic/cdfast.cpp), the Python one is too slow.

Final 2026-10-13: lead's clean check (zf/m254/check.py) PASSED. E2E254 proves zfc_254 halts <-> ZFc ⊢TC ⊥ (and the ZFC version), closed. Do not change files in zf/m254 without asking the lead.
