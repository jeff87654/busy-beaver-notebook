---
name: m254-tm-layer
description: "zfc_254 TM layer (zf/m254/tm) DONE 2026-10-14: tm254_rm : halts tm c0 <-> rm_halts p254 ([], R0) closed via certified symbolic executor on the final table; check_tm254.py"
metadata:
  node_type: memory
  type: project
  originSessionId: a872c5f9-7ee6-45a6-89ec-58594d6fffa6
  modified: 2026-10-14T04:09:09.449Z
---

zf/m254/tm (2026-10-13): third-party 254-state ZFC machine. Decision: verify the FINAL table directly with a Coq-verified symbolic run-length executor (SymExec.v: segments SB/SR(a*n+c)/SBox, self-loop acceleration, box oracles). Not via the 261 named table + context-merge certificates.

Done, no axioms:
- Box.v: 4 register lemmas (mark/inc/dec0/decp)
- all 8391 site cases by vm_compute (24 s)
- Boot.v: 264,982 steps (vm 1.5 s)

RHS = RM.v rm_halts on the tree from paths.json (verified consistent with Wade path semantics; wf ok), logical register order, R0 = nextproof 2.

DONE 2026-10-14: Main.v tm254_rm + tm254_iter, closed. p254/R0 frozen in coq/Prog254.v (M254.Prog254); m254-prog does iter_halts p254 R0 <-> enum. Check: python zf/m254/tm/check_tm254.py. See zf/m254/tm/DESIGN.md.

Pitfalls: never `simpl` a hypothesis containing exec/walk on p254 (unrolls fuel 4000/6460, hangs); use cbn [specific consts]. Sections close over Hypotheses (site_run needs box lemmas as args).

Machine facts: dispatch state 96 head on first PC cell; PC read 3x per instruction (phases by the 2 cells after P: 00 prep, 11 select/mark, 01 execute); gap D>=38 needed, boot gives 62; positive decnz appends a 0 block.

Lesson: [[formalization-estimates-too-high]] held again — the whole per-site + register part took ~1 session.
