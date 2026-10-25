---
name: zf-framework-design-lessons
description: "ZF-machine (halts iff ZF inconsistent) framework-level design study 2026-10-10 — measured negatives (single chain, boot, O(1) dispatch, string-stack machine) and where the states go"
metadata:
  node_type: memory
  type: project
  originSessionId: 7b95bc12-778b-4d66-a6e9-e51940c89aa8
  modified: 2026-10-11T02:32:26.272Z
---

Framework-level study of Wade's 393-state ZF machine (zf/framework/, IDEAS.md, SM_SPEC.md, REPORT.md), 2026-10-10.

Where the 393 go (measured, framework/measure/attr.py): 69 framework (22 of them register chains), DAG 324 =
62 main loop/parse + 87 DET/GEN machinery + 175 axiom templates (276 ops, hash-consed to ~150 cells = 7.5 bits
of program per state). Templates are the floor for any "1 cell per op" design.

Measured negatives (framework/fwmin): single chain per register impossible with the zf2 DAG (11 inc leaves in
cdr position; a leaf only hands over 1 written bit + entry state); ret1/ret2 merge >= 0; O(1) dispatch
impossible (pumping over 0-runs, marker drifts); no 5-state boot with gap >= 15 (full TNF, max gap 10).
String-stack machine SM (wffs as token strings, prefix order, DET by prefix-freeness): DAG 228 cells (vs 324,
fully tested, framework/sm) but hand-written tape primitives >= 160 states for 10/14 primitives (framework/smfw)
=> total >= ~420, worse than zf-reduce's 354. Lesson: on a 2-symbol run-length tape every find/carry/flag
routine costs 8-15 unshareable states; unary inc/decnz + DAG sharing is the efficient split.

Positive logic-level ideas (handed to zf-reduce): B6a distinctor form -. A. z z = x -> ( -. A. z z = y -> B6a )
has no side condition (-7..-9 cells); POW+UNI merged axiom (-5..-7); DET by unpairing the major premise.

**Why:** avoid re-deriving these; future "new framework" proposals must beat the template floor + ~70
engine, not the 393.
**How to apply:** for ZF-machine records work program-level (zf-reduce style) and logic-level; treat framework
constants as tight. See [[bb8-hunt-working-style]].
