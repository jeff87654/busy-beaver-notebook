---
name: m14-argon-bb14
description: "M14 = 14-state f_(omega+2)^3 halter written by Gemini \"Argon\" (2026-10-13), Coq in proofs/BB14_M14*.v; independently verified by me same night"
metadata:
  node_type: memory
  type: project
  originSessionId: cffdb8a9-25fd-4e9b-ae21-7754100d98e3
  modified: 2026-10-14T06:30:22.240Z
---

M14 = 1RB1RA_1RI1RC_0LD1LG_0RE1LD_1LN1RF_1LJ0RA_1RA0LH_1LG1LH_1RK0LM_1RZ0LE_0LE0RJ_1LH1LM_0LH0LL_0LG1LN (J0 = halt).
Written 2026-10-13 ~20:00-21:08 by **Argon (Google's new Gemini model, released that day)**, not by our sessions; no
notes or investigation dir. Files: bb8_list/proofs/BB142.v, Individual142.v (clean BB122-style setup), BB14_M14.v
(`halt`), BB14_M14_bound.v (score_exact, sigma_lower_bound f_w2^3(15) < N+1, _strong f_w2(f_w2(f_w1^15(f_w 21)))).
Unrelated to our n1 lineage (best transition overlap 7/28 vs BB17; proof uses (p,a) pair maps Kc/Kd_step/D_reload).

**Verified 2026-10-13 (me):** check.py PASS (halts, no axioms); independent probe
(scratchpad probe14/probeM14.v pattern: own FGH + ones-count, bridged by induction lemmas) restates both bounds
against my definitions -> all Closed under the global context. Beats T12a (f_(w+1)^2) and wiki BB(14)-(16);
vs BB17/18 (f_(w+2), [[bb17-bb18-champion-anatomy]]) by FGH reasoning only, not formalized.

**Pitfall:** never let Coq compare FGH terms on numerals by conversion (`exact` after a partial `rewrite !`, or a
`Check (thm : my_stmt)` with different constants) -- it evaluates towers and hangs. Bridge with lemmas over an
abstract variable, rewrite explicit instances.
