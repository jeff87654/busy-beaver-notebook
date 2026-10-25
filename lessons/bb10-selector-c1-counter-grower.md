---
name: bb10-selector-c1-counter-grower
description: Selector search (2026-10-08; SCREENING EVIDENCE ONLY, independent verification pending as of 06:15): n1 = GH machine ..._1LI0LC_..._0LJ0LI_---0LC is an f_(omega+1)-class grow-and-count halter (follow2 level rises per period, counter 12B+7, halts at exhaustion for B's class); c1 (omega-level 1, index ~25B) and G6 (non-halting) are the cousins; tools in halt_redirect/sel/
metadata:
  type: project
---

Grow-and-count search in the G/H-sibling family of the BB(8) record (write-up: bb8_list/investigations/halt_redirect/selector.md,
tools in halt_redirect/sel/: evtrace/ev.py, stageu.py, fol.py, gsearch.py, gs2/gs4.py, branch.py).
- **EXACT SCORE PROVED 2026-10-08 ~09:20:** proofs/BB10_n1_exact.v (lead recompiled + probed, Closed): ones at halt = 2W + 3*arrow (S W) 2 (arrow (fst s) 2 5) + 12J + 5 with J = (3T-13)/7, s = stepn J (34, arrow 35 2 (arrow 34 2 5 - 1)), W = fst s + 2 snd s - 6, step (n,g) = (n4, arrow (S n4) 2 (arrow n2 2 5 - 1)), n2 = n+2g-6, n4 = n2 + 2*arrow (S n2) 2 (arrow n 2 5 - 1) - 4; standard score = +1. score_value_gt links to the old lower bound.
- **CLEAN-ROOM REBUILD PASSED 2026-10-08 ~09:10** (lead; 9-file closure in an empty dir, all exit 0, no axioms; log investigations/bb10_n1_coq/clean_room_build.txt; BB10_n1.v sha256 2731f80d...).
- **STATUS 2026-10-08 ~08:30: n1 FULLY PROVED as a BB(10) champion candidate** — BB10_n1_bound.v (lead recompiled 53 s; probe: halt, score_exact, sigma_lower_bound, beats_champion (nc+1 < no+1 vs BB10_champion_bound score_exact), beats_lead (vs 0LJ0LC), dominates — all Closed under the global context). Report investigations/bb10_n1_coq.md. Earlier: **n1 HALTING PROVED** — proofs/BB10_n1.v check.py PASS (agent inv-n1-coq; lead re-ran: PASS, no axioms); proves w >= F^(2JJ+1)(34), F n = arrow n 2 4, JJ = (3T-13)/7, T = arrow 37 2 3 (T = 2 mod 7 proved). Bound file BB10_n1_bound.v in progress (beats champion score_exact, 0LJ0LC, generic domination of (2^K)^x(x) for K,x <= F^3(34); M3 has no proved upper bound so formal n1 > M3 not possible yet).
- STATUS 06:30: peer's inv-bb10-fw1-verify INDEPENDENTLY CONFIRMS (strong evidence, own tools, both size orders): halts J0, sigma > G^N(33), G(x)=2^(x+1 arrows)3, N=(12B+5)/7 ~ 1.71B growth events, f_(omega+1)(~1.7B); report investigations/bb10_n1_verify.md. Coq agent inv-n1-coq launched (proofs/BB10_n1.v, reuse peer's BB10_fw1_*.v). Earlier: screening only (mini-follower, follow2 to level 2, size-ordered policies, literal halt replays). Independent verifiers: fable-n1-verify (halt_redirect/n1_verify.md) and the peer's inv-bb10-fw1-verify (investigations/bb10_n1_verify.md). Not proved.
- n1 = `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC` (J0 = halt): parked counter list 1^(12b+7)
  behind D2 blockers (-14 per 6-stage period), cleared zero list grows by (2P+4)/3 per period where P = 2R'+3 is the
  previous period's parked accumulator token (follow2: zeros 4/3 R3 + 4/3 R6 + .., omega-level +1 per period), ~2R/3
  full cycles per period, halts in J0 when the counter is gone (replayed with far bits for R = 19/2539). Halting class
  b = 6 mod 14 (b0 = 6, 20 halt; 11/16/21 continue into junk); real B = 6 mod 2520 is in it. sigma ~ f_(omega+1)(0.86B).
  Only found after filtering screens on 'zeros=' (cleared list), not k (total tokens): k-filters hide it.
- c1 VERIFIED (inv-c1-verify, halt_redirect/c1_verify.md, ~90%): halts for B = 0 mod 3 (real), (4B-3)/3 periods, 2^N 5 < sigma < 2^N(16B/3+23), N = (76B+141)/3 ~ 25.3B arrows; b = 1,2 mod 3 halts at b0 were representative artefacts.
- c1 = `..._1LI0LC_..._---1LJ_0RJ0RF`: D6 counter 4B+3, constant growth 13/period, omega-level 1 at index ~25.3B.
- G6 = `..._0LI0LC_..._1RJ1LA_1LI---`: R-growth with a D6 counter but repacks a new counter forever (non-halting);
  exhaustive gadget enumeration (160k leaves) shows no gadget halts there.

**Why:** the lead asked for an f_(omega+1) selector machine; n1 is the answer-shaped candidate, c1 the fallback.
**How to apply:** judge growth by the cleared list only (lead's correction); mf35g b0 = 6 world + fol.py --policy
big/shrink + literal replays with far bits are the cheap checks. See [[bb8-hunt-working-style]].
