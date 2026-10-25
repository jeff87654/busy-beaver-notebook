---
name: m13-argon-bb13
description: "13-state f_(omega+2)(f_omega 20) halter M13, found/proved by Gemini \"Argon\" 2026-10-14 in bb8_list/proofs/BB13_M13*.v; verified by me"
metadata:
  node_type: memory
  type: project
  originSessionId: fc776c20-4d40-4570-94e4-ed5f097ff3b1
  modified: 2026-10-14T16:18:54.573Z
---

M13 = 1LB1LA_1RC0LA_1RD1RC_1RE1RK_1RF0LJ_0LG1RI_1RE0RH_1LF0RC_1RM0LE_1LA1LE_0LL1LB_0RM1LL_1RZ1RH
(13 states, TNF). Found and proved by Argon (Gemini, in Antigravity) overnight 2026-10-13/14. Files: bb8_list/proofs/BB13_M13.v (halt) and BB13_M13_bound.v (score_exact, sigma_lower_bound_strong: f_omega2 (f_omega 20) < score).

Verified 2026-10-14 09:18: check.py PASS on BB13_M13.v; the bound file's 09:13:57 version compiles and both sigma_lower_bound_strong and score_exact are Closed under the global context. f/f_omega/f_omega1/f_omega2 are standard FGH defs (lines 70-78). The 09:10 version had failed at pa1_bounds, so Argon was still editing it then.

**Why:** an f_(omega+2)-level BB(13) champion dominates T12a (f_(omega+1)^2), so the BB(13) wiki row would no longer be blank. See [[m14-argon-bb14]], [[bb12-t12a-coq]], [[wiki-champion-rows-convention]].

**How to apply:** Antigravity has no remote access, so the user can't always tell whether Argon is still working. Don't edit Argon's files while it may be active; verify read-only (compile a Print Assumptions file in the scratchpad with -Q proofs BB8). Not yet published to the repo as of 2026-10-14.

**PUBLISHED 2026-10-14: PR #17 merged (934461f), all 22 CI checks pass.** Was staged as worktree C:/Users/jeffr/Downloads/busy-beaver-bb1314, branch bb13-bb14, commit 502667d
(BB13/ + BB14/ + README + CI job bb13-bb14). Line 1 heading comments of BB13_M13.v / BB14_M14.v corrected (Argon overstated:
f_w2(f_w(f_w 20)) / ^3(16)). Argon's process doc = bb8/FW2_13_14_SEARCH_AND_PROOFS.md: its M14 table string and its section-4
machine description do NOT match the Coq M14; search_14_fw2.cpp / search_13_joint.cpp lost, search_core10.cpp + search13.cpp
published in BB13/search/. M14 = Jacobzheng BB14 with A<->M swapped, 20/28 transitions shared.
