---
name: bb7-n2-decided
description: BB(7) holdout N2 (segment-coded f_(w+1) rebuilder) and its relabel proved NEVER HALT in Coq, 2026-10-23
metadata:
  type: project
---
N2 = 1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA and relabel 1RB1RE_1LC0RA_1RF0RD_1LC0LE_1LD0LC_1RG0RE_0RB--- never halt:
bb8_list/proofs/BB7_N2_1RB0RC.v + BB7_N2m_1RB1RE.v (flip + state perm after 4 steps), check.py PASS, no axioms (not pushed).
Invariant on K-configs (segments (01)^p(10)^q sep 11): phase O all odd; phase E x even, leftmost (even,odd). Report:
bb7_holdouts/n2_decide/REPORT.txt; OPEN_CANDIDATES entry SETTLED.

**Why:** generic CTL/NGramCPS failed; method that worked = fit K-level rules, then autoproof engine for cell-level pieces
with explicit waypoints (engine fails on whole rules with nested loops) + hand Coq composition.
**How to apply:** for other segment/list holdouts reuse n2_decide/coq (rules_def.py waypoint style, hand*.v.in). Pitfalls:
put run constants nearest the head (right-side runs: constants first); never write shared files with Python's default
cp1252 encoding (truncated OPEN_CANDIDATES once; write temp + os.replace, encoding utf-8). See [[screening-lessons]].
