---
name: bb7-never-audit
description: 2026-10-24 adversarial audit of reb7's biggest BB(7) NEVER-HALTS verdicts: none broken (160/173 confirmed via symsim-measured rules + invariants); tools in bb7_holdouts/never_audit
metadata:
  type: project
---
Audit (bb7_holdouts/never_audit/REPORT.txt): 173 reb7 NEVER rows re-derived independently (v/U10/U110/C1 codings from literal
tapes, rules measured by symsim symbolic runs per class mod 720, exhaustion per class, invariant search, 1e9-step lockstep).
160 CONFIRMED, 9 UNDECIDED (tool limits: F5 outer-counter siblings size 26, F89 multi-template size 27), 4 NO-TEMPLATE (N2, dl3 k/l/m).
Of the 166 NEVER rows with lists >= 20 digits (34 families), 162 are in families with a confirmed member. No rule disagreement with reb7.
dl3 F3 rows need the projected-parity / last-B2 argument (f3check.py), not a linear invariant.
M8 control: pipeline flags it OPEN (exhaustion leaves template) but cannot reproduce its real-class halt.

**Why:** a halting rebuilder at level 20-604 would be a huge BB(7) record; fitted-rule errors caused the X33 false alarm before.
**How to apply:** reuse audit2.py/deep.py (symsim --stopq patch in never_audit/src) to audit new rebuilder verdicts; it flags coding
mismatches as DISAGREE/OPEN rather than false CONFIRMED. Related: [[bb7-holdout-triage]], [[screening-lessons]].
