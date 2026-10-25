---
name: argon-bb9-fw2
description: "Argon's 9-state blank-tape f_omega(f_omega 465009) machine 1RB0RD_... (2026-10-15) verified by me 2026-10-16; its M9 (2026-10-14) is NOT a blank-tape f_(w+1) machine"
metadata:
  node_type: memory
  type: project
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-17T01:19:39.001Z
---

Gemini "Argon" ([[m13-argon-bb13]], [[m14-argon-bb14]]) wrote these files in bb8_list/proofs. None of them is published to the repo yet.

**BB9_M9_halt.v (2026-10-14 20:01).**
- Machine: M9 = 1RB1RA_0LI1RC_0LD1LG_0RE1LD_1RF1RF_0RB0RA_1RA0LH_1LG1LH_---0LD.
- From a blank tape it halts in 7 steps with 1 one.
- The f_(ω+1) growth only holds from the prepared tape `0 0 (111100)^Z`. It is the engine core shared with M11/M14 (rows A-H), not a champion.
- The user called it "argon's 9-state w+1 machine". Correct that framing if it comes up again.

**BB9_fw2_1RB0RD.v + _bound + _vs_records (2026-10-15 08:10-09:12).**
- Machine: 1RB0RD_1LC1LC_0RA0LB_1RE1RD_0LG0LF_1LE1LF_0RH1LG_1RD1RI_1RZ1RA.
- It halts from blank with σ > f_ω(f_ω(465009)), using standard FGH f 0 = S, f (k+1) n = (f k)^n n.
- Verified 2026-10-16:
  - check.py PASS.
  - The scratchpad probe (probe9/Probe9.v) printed 9 Print Assumptions as Closed: halt, the bounds, score_exact, and beats over our BB9 records (redir_0LA, redir_0LA_fh, record 1RB0RA), the BB9 champion (Jacobzheng) and the BB10 champion (Racheline).
- It does NOT beat our 10-state n1 (f_(ω+1)), which stays the BB(10) record ([[bb10-n1-coq]]).

**BB11_M11_halt.v (2026-10-15 08:50).** An 11-state blank-tape halter. Its title claims f_(ω+1)(f_ω(f_8 2)/3). If true, it beats n1's f_(ω+1)(~2↑↑37) and takes the blank row 11 (it stays below T12a for row 12).
- 2026-10-16:
  - The user wants the 9-state fw2 machine in the repo; I write the PR (the user prefers my PRs).
  - The BB11_M11 halting proof passes check.py, but the file has NO bound (its title claim is unproved).
  - Agent m11-bound is writing BB11_M11_bound.v + BB11_M11_vs_n1.v to decide whether M11 takes the blank BB(11) row (it must beat n1's F^N(34)).
- M11 RESOLVED (2026-10-17): NOT a record. f_ω^3(5) < score ≤ f_(ω+1)(30), and the title claim is refuted in Coq. n1 beats M11, and the lead probe printed all 6 theorems Closed. See [[m11-argon-bb11]].
- User decision 2026-10-17: M11 is NOT included in the repo (not a record). The PR covers only the 9-state fw2 machine. Agent bb9fw2-package is preparing branch bb9-fw2 (BB9/ write-up in M13 style, multifile verify, CI, README).
- The repo BB9/ previously held our record 1RB0RA_..._0LH1RZ (f_ω(f_13 2)); fw2 supersedes it.

- 2026-10-17: a reboot killed agent bb9fw2-package, but its stage-2 build had already passed (scratchpad fw2build: exit 0, 5/5 Closed, stage 2 took 1 h 43 min with PAR=1). The lead added the logs and sha256 (blob hashes, LF), committed 9ed1e7a on branch bb9-fw2, and opened PR #21. Merge once CI is green.
- !!! PUBLISHED 2026-10-17: PR #21 merged as 56be2ce (all 28 checks green; the bb9-fw2 job takes ~2 min).
