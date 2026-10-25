---
name: zf-machine-reduction
description: ZF-inconsistency TM state reduction (Wade's 393 framework) — results, tracks A/B/C, tools in zf/reduce
metadata:
  type: project
---
2026-10-10: reduced Wade's 393-state "halts iff ZF inconsistent" TM inside his framework (zf/reduce/RESULTS.md, cand/).
Track A (prov unchanged) 361 = cand/A361.tm; Track B (equivalent variants of EXT/INF/REP) 354; Track C (POW+UNI merged) 353; dedup 392, +param perms 388.
Key wins: param-role perms, DET pop into scratch3, destructive B6a test (params 0 at loop head), tag-based wff builders, pushwff/select sharing one pair/unpair instance, if_eq w/o break-2, dechain to cap dispatch at 7.
**Why:** the user wants a smaller machine that the completed 393 Coq proof ([[zf-coq-proof]]) can be retargeted to cheaply.
**How to apply:** validation = crosscheck.py + symrm.py + semtest.py (symbolic RM vs Python port of Enum.v); searches plateaued (ILS/LAHC hours) — further gains need framework changes (zf/framework/ is another agent's task).
