---
name: bb8-annotated-ngcps-g
description: "When plain NGramCPS fails because a sweep runs off a forgotten tape end, writer-annotated windows + halting-reach set g close it tiny (m7 1RG0LC PROVED 2026-10-08)"
metadata:
  node_type: memory
  type: project
  originSessionId: 45e83fb6-f8fb-4d8b-a595-56f7c666ca5e
  modified: 2026-10-08T07:50:44.185Z
---

2026-10-08: m7 machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE (E0 = 1RG sibling of 0RB0LC) was
PROVED (check.py PASS) after plain NGramCPS failed at every window pair up to 16/16. Fix: n-gram CPS over cells
annotated with the state that last wrote them (ghost, existentially quantified) plus, on the right side, g = set of
states whose right-moving run halts before turning (a DFA read from the far end). Closes at 8/6 with only 105k
configs (|S_L| 2986, |S_R| 66). Neither part alone closes; exact tail memory / near-head stacks (tcps2/3) never closed.

**Why:** the halt was a G/F/H/E sweep running off a tape end through a digit block whose barrier (`3|`) sits
arbitrarily far away; g carries "would a sweep from here run off the end" exactly, annotations stop unreal splices.

**How to apply:** for a NGramCPS FAIL where the halting local config is a sweep into blank, try
`investigations/bb8_m7_1RB0RA_1RG0LC/opus/ngann.exe MACHINE kL kR 2 1` (scan kL/kR 6..10), check with
`pycheck.py` / `realchk.exe`, emit Coq with `gen_coq.py CERT OUT.v FUEL` (edit the tm table and pycheck/realchk
machine string for other machines; generic sound lemma nonhalt_of_check). Related: [[bb8-ngcps-long-windows]].

**!!! WARNING (2026-10-17, bb9-parked):** ngann.exe is UNSOUND on 9+ state machines. It packs the state into 3 bits (q<<61) and g into 8 bits, so state I aliases to A (it gave a false NONHALT on N1b in 0.5 s). Use the widened copy bb8_list/investigations/bb9_parked/ngann9.exe (it reproduces the m7 proof exactly). Never trust an old ngann NONHALT on a 9- or 10-state machine. Coq certificates are unaffected because gen_coq/check.py re-verify, but triage verdicts are affected.
