# SAT synthesis of digit-list machines: outcome (stopped 2026-10-07)

**What it tried.** `sat_dl.py SPEC.json` encodes bounded executions as SAT (CaDiCaL via python-sat). The unknowns are
the 16 transitions of an 8-state machine (A0 = 1RB fixed). Each example says "from this family word, reach that family
word within T steps" or "halt within T steps", in the BB(7) champion's digit-list template. The goal was to *design*
machines with chosen rules (a longer start-up, rebuild-then-halt) instead of finding them by enumeration.

**Calibration test.** `champ_fix4.json`: rediscover a known champion-rule machine from 4 examples (three rule steps of
500-720 steps and one 350-step halt), with 4 of the 16 transitions pinned (B0 = 1LC, C1 = 0LB, F0 = 1RG, G1 = 0RF).
- The encoding has 294,060 variables and 2,312,956 clauses and builds in 5.5 s.
- It ran from 2026-10-03 22:28 to 2026-10-07 at Idle priority: **55 CPU-hours, no answer (neither SAT nor UNSAT)**,
  using about 1.5 GB. It was stopped by the lead at the user's request.
- `champ_test.json` is the same test with no pinned transitions, which is harder. It was never run to completion.

**Conclusion: the SAT route does not scale to these machines as encoded.**
- The rule examples need hundreds of steps each, and a start-up example would need thousands (`../startup/FINDINGS.md`).
  The unrolled tape-by-time encoding is then far too large for the solver, even when the machine is mostly pinned.
- Real targets (fewer pinned transitions, longer runs) would be much harder than the calibration.
- Not pursued further. Ideas that could change this, none tried: encode macro steps or rule applications instead of
  single TM steps; give the solver the configuration family as an invariant (a CPS-style closure) instead of explicit
  runs; or use incremental solving with short examples first.
