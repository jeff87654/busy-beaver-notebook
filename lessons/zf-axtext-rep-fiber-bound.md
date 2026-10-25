---
name: zf-axtext-rep-fiber-bound
description: "ZF machine shrink 354->336 by replacing REP's functionality hypothesis with a fiber bound (POW, UNI dropped); Coq closed in zf/axtext/coq/R3"
metadata:
  node_type: memory
  type: project
  originSessionId: 7b95bc12-778b-4d66-a6e9-e51940c89aa8
  modified: 2026-10-11T07:34:59.302Z
---

2026-10-11: the ZF-inconsistency TM (zf/) went from 354 (B354) to 336 states (zf/axtext/search/cand/R3s336) by changing REP's hypothesis "A. v1 ph -> v2 = v1" to "A. v1 ph -> ( -. A. v0 ( v0 e. v2 -> v0 e. v1 ) -> v2 e. v1 )" (images of w lie in y u P(y)). POW and UNI become REP instances and were dropped. EXT and INF texts are unchanged.

Coq: zf/axtext/coq/R3 proves prov (Wel v0 v0) <-> ZFc ⊢TC ⊥, closed. zf/axtext/regcon gives the Reg and function-symbol variants (rebuild R3 first, then regcon). L1_R3s.v covers the machine-text equivalence. The port to zf/v336 is being done by the L1/L2/L3 team.

**Why:** the token cost per axiom is about 0.5 state per RPN token; dropping whole clauses beats shortening them.
**How to apply:** to shrink further, look for scheme generalizations that make other axioms instances, and measure them with the ILS in zf/axtext/search (Idle priority, at most 2 processes). Related: [[bb8-hunt-operating-policy]]
