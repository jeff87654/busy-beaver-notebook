---
name: bb17-bb18-champion-anatomy
description: Anatomy of Jacobzheng's BB(17)/BB(18) f_(omega+2) champions (2026-10-09): 7-state f_omega engine + 4-state counter layer + 6-state merge/parity layer; rules verified; notes in bb_champs_17_18/NOTES.md
metadata:
  type: project
---

The user wants an f_(omega+2) machine slightly bigger than n1 (10 states). First step (2026-10-09): analysed the
wiki BB(17)/BB(18) champions (Jacobzheng; no published analysis). Tools and notes are in bb_champs_17_18/
(rsim.py run-length sim, cfg.py crafted tapes, test_*.py rule checks, model.py abstract model, NOTES.md).

- **Layers:**
  - A-G is a digit-list f_omega engine: a list of m ones gives f_m.
  - H-K: decrement c, rebuild a list of ~A/2 ones from the accumulator.
  - L-Q: when c = 0, d -= 2 (halt at d = 1); N/O merge the output into a new c. When d = 0, P/Q merge into a new d.
- Halting is a parity gamble on the d refill.
- BB18 = BB17 + one state on A0, so it starts with d = 8 instead of 6 (one extra f_(omega+1)).
- The wiki already lists n1 as the BB(10) champion (f_(omega+1)(2^^363)). BB(14) is f_(omega+1); BB(15) f_(omega+1)^2; BB(16) f_(omega+1)^3 (wiki 2026-10-11).

**Why:** this is the template for an f_(omega+2) search.
**How to apply:** on an n1-type machine, w+2 needs a refill-counter-from-accumulator merge (2 states) plus a second
counter with a halt (about 2 states) and a large initial d. Best bases: loopers that already re-park a counter every
period. See [[bb10-selector-c1-counter-grower]], [[bb9-fw1-search-status]].
