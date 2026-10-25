---
name: zf-framework-study
description: "ZF-machine framework-level study (2026-10-10): Wade's register-DAG framework is near-optimal; measured negatives for register-stack op and tape-native strings; cost rule for new ops"
metadata:
  node_type: memory
  type: project
  originSessionId: 7b95bc12-778b-4d66-a6e9-e51940c89aa8
  modified: 2026-10-10T22:23:48.844Z
---

Framework-level design study for the "halts iff ZF inconsistent" TM, results in zf/framework/ (REPORT.md, IDEAS.md, attrib/, proto1/, proto2/).

- Cost model (measured on zf2.tm 393 = 69 + 324): framework = 38 constant + 2 per register + 1 per dispatch level (longest car run - 1); DAG = 1 state per hash-consed cons cell, ~0.5 state per axiom token after outlining, engine 142 / clauses 178.
- RULE: a new register-op TYPE costs its gadget + one chain state per register index up to the highest index it is used on (ops on the stack top >= 11 chain states). Push/pop renumber registers above them, so a stack cannot sit at low indices.
- proto1 (register-stack op Q + depth guard, Cantor wffs kept): 406 (+13), fully validated. Depth guard is mandatory (boot junk run of value 1 = |v0 e. v0| would be popped -> false halt).
- proto2 (tape-native postfix token strings): engine ~310 states measured (COPY 56, DET 69); total 350-518. Open soundness issue with malformed parameter strings.
- Program-as-data/interpreter >= 600 (lambda evaluator alone 360 in NQL); wade-mtm lam_*/blc files are CatsAreFluffy's BB-lower-bound work, not ZF.

**Why:** prevents re-spending effort on framework rewrites; the gains are program/logic-level (zf-reduce reached A361/B354 in the unchanged framework).
**How to apply:** when asked to shrink the ZF machine, work on registers/clauses/axiom bodies inside Wade's framework; quote the cost rule before proposing new framework ops. See [[bb8-hunt-working-style]].
