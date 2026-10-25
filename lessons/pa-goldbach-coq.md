---
name: pa-goldbach-coq
description: "PA ⊢ Goldbach TM (zf/pagb, 449 states, frozen): Coq end to end closed 2026-10-25 (Headline.v); layers, pitfalls"
metadata:
  node_type: memory
  type: project
  originSessionId: 205a0b68-c138-46ef-afb2-3059e16fcd57
  modified: 2026-10-25T03:35:47.520Z
---

**DONE 2026-10-25.** Frozen 449-state pa_wade.tm (sha ed795af7…). `zf/pagb/e2e/Headline.v` (52 lines) proves `halts tm c0 <-> PAeq ⊢TC GC_form` and `GC_adequate`, both closed. Top-level check: `zf/pagb/check.py` (layer checks + coqchk). Agents: pagb-coq (me, Coq lead) and pagb-machine (designer). Messages to the designer misroute, so use zf/pagb/INTERFACE.md plus the lead as relay.

Layers:
- **coq/:** Spec, then the reference calculus pprov ⇔ PAeq. Code-level `thm` ⇔ pprov (PA_Thm, PA_CompCode, with CD lemmas from m254). Then L1 (PA_Enum/PA_L1, 21 AX slots) and PA_Logic.
- **tm/:** an Opus subagent ported it from m254tg/tm.
- **prog/:** ported from m254tg/prog by node structural hashing (tools/port.py). New ProgOccPA.v proves the occurs-check walk (well-founded on Σ(2t+1)).

Design lessons:
- Atom vacuity must be general (B6a for every z ∉ atom, nested terms). Pinned or flat-only vacuity is circular; the machine uses an occurs-check gate.
- Use PAeq, not PA (the library's PA has no equality axioms).
- Open induction instances need a parameter-free closure for soundness.
- The pprov primitives have the machine's shapes (B7v/B7c, IND with c = fcode a); the general forms are derived.

Coq pitfalls:
- Never let Coq evaluate concrete row codes (huge unary nats). `constructor` and `exact` against closed codes hang; use cd (enc a) and Opaque P.
- The vendored library must live outside the -Q PAGB dir.
- Library imports turn on implicit arguments, so add Unset Implicit Arguments.
- BusyCoq's `>>` notation clashes with the library's, and halts/c0 live in the instantiated functor PAGBT.ZFTM.ZFTM.

Links: [[m254gb-goldbach-machine]], [[m254-formalization]], [[m254tg-universe-machine]].
