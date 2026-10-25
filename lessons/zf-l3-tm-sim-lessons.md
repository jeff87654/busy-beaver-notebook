---
name: zf-l3-tm-sim-lessons
description: ZF 393-state machine L3 (TM simulates RM) done 2026-10-10; list-zipper approach + Coq pitfalls with busycoq on a big machine
metadata:
  node_type: memory
  type: project
  originSessionId: 7b95bc12-778b-4d66-a6e9-e51940c89aa8
  modified: 2026-10-10T18:38:24.380Z
---

L3 of the ZF-machine verification (zf/coq: ZFTM.v, SimBase/SimOps/SimRegs/SimIP/SimDag/SimBoot.v, Sim.v) proved
`halts tm c0 <-> rm_halts zf2 ([], regs0)` closed (2026-10-10), using RMEquiv.no_stray.

Approach that worked: list zipper `zc q l r` / `zl q l r` lifted to busycoq streams, step lemmas zR/zL,
padding lemmas (trailing falses), generic register-file encodings sepsR/sepsL, every routine validated first
by a Python zipper checker before proving. Static DAG facts by vm_compute'd tables (no path enumeration).

**Why:** a direct busycoq `execute` style is hopeless for 393 states with symbolic register files.

**How to apply (pitfalls):**
- busycoq Helper (exported by TM) defines `&&` (sumbool) and token `-[`: use `andb`, write `cbn - [x]`.
- Import Lists.Streams BEFORE Lists.List (hd/tl/map clash); Strings.String shadows `length`.
- Type step-lemma symbols as `bool`, not `Sym`, else conses become `@cons Sym` and rewrites silently miss.
- Never `simpl` goals containing big concrete lists (all_states, junk registers): use cbn [app], change, lnorm.
- `strip_rev` recurses on the list, so `strip_rev b 0 l` does not reduce for variable l.
- Bash heredocs with long Coq text sometimes fail ("unexpected EOF"); write chunks with the Write tool.
- Subagents here are synchronous; they may end without a report: check the files they edited.
Related: [[coq-selfcontained-merge-lessons]]
