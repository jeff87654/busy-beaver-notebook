---
name: bb7-champ231-lead
description: "!!! 2026-10-22 possible NEW BB(7) RECORD champ_231 = 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB (+ champ_232 G0=1LC) from the BB(7) holdout list; Argon claim ~3↑^20; c231-check + c231-coq launched"
metadata:
  type: project
---
Found by Argon (Gemini, run by the user) in our triage7 hits (bb7_holdouts/hits_triage7.tsv, chunk c00185; Argon's
files bb8_list/investigations/bb9_triage7_and_1RB1LA). dlscan2: CHAMPION, R1 b->b+3, R2 a=b+3, R3 refill b+3-k,
R4 always halts. Claim: 20-digit list of 1s by step 3715; D a->3a+3, Bk refill 3a+3-k, E halts at C1 -> ~20 up-arrow
levels vs the BB(7) champion's 12-digit doubling list (sigma = 3*(2↑^13 3)+22). Lead's literal run matches the shape.
LEAD'S MISTAKE: I had dismissed the triage7 CHAMPION rows as constant-slope false alarms from base rates without
checking; these two have genuine Ackermann rules. Lesson: check every CHAMPION row's R1 slope (1b+c = real).
Agents (Opus): c231-check (bb7_c231check, independent rules/score/prior art), c231-coq (bb7_c231_coq).
Related: [[bb7-holdout-triage]], [[bb8-champion-subtree-lead]].
!!! 2026-10-22 ~20:00 champ_231 COQ-PROVED, LEAD-VERIFIED (agent c231-coq, bb7_c231_coq/coq, busycoq bd2e36f, 7-state
instance BB72/Individual72): lead re-ran probe.v (exit 0, 7x Closed): table_matches_string (parser), halt_entry,
c0_is_blank_A, c231_halts, c231_score_exact (ones = 2*W 20 5 + 7; sigma = N since the halt reads C1 on a 1),
c231_lower (Lc 20 < N, 3↑^19(3↑^18 3) < N, 3↑^20 2 < N), c231_beats_bb7_champion (3*(2↑^13 3)+22 < N and
2↑^11(2↑^11 3) < N). Bounds are stated as "exists halting c with ones c N /\ bound" (fine by determinism; repo style
uses forall-halting-c: restate when packaging). T3d.v/T5d.v contain Admitted but are unused (not imported; Print
Assumptions clean). Next: champ_232, c231-check's prior-art result, then packaging (user's call on announcing).
2026-10-22 night: user approved packaging champ_231 as BB7/ on the repo + an explainer; Ligocki's wiki analysis of
the champion saved in bb7_c231_writeup/ligocki_bb7_champion_wiki_2026-10-22.txt; packaging assigned to c231-coq
(after champ_232). !!! bb7-rank (rank7 estimator) found X = 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE
(G1=1LG sibling of dl3's never-halting 'i'): one rebuild to a 32-digit list, parity argument says halt, ~2↑^34 >
champ_231 (~2↑^21). Unverified; x33-check (bb7_x33check) + x33-coq (bb7_x33_coq) launched. Also
1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF ties the champion exactly.
2026-10-22 night: X33 REFUTED by x33-check (never halts): borrows leave tail digits 2 (rank7 used dlscan2's
"tail=1"), so Phi = b + sum(ds) mod 2 stays 0 -> every true exhaustion even -> rebuild forever (same invariant as
sibling i). x33-coq stopped; bb7-rank told to measure rules literally, add an invariant check, add X33/i as negative
controls, and re-rank. Lesson: dlscan2's fitted parameters (tail values) are not trustworthy inputs for a parity argument.
!!! 2026-10-22 ~21:15 PUBLISHED: PR #34 MERGED ed1580b — BB7/ (verify: Defs.v + Statement.v; c231/c232 _table _halts
_halting_config _score (= 2*W 20 5 + 7) _lower (3↑^20 3) _beats_bb7_champion; CI job bb7 3m25s; write-up with Ligocki
comparison; README BB(7) row crediting Argon). Not yet announced to bbchallenge (user's call). X33, Z16 refuted.
2026-10-22 ~21:35 the USER announced champ_231 on the bbchallenge community Discord with a link to the repo. Watch for
community feedback (independent checks, wiki edits, questions about the BB(7) holdout status); answer from BB7/ files.

2026-10-23: launched Opus agent c231ext (bb8_list/investigations/bb8_c231ext): 8-state halt-redirect extensions of champ_231/232 (C1 -> new state H), residue-faithful, control = old champion -> M8; 9-state only if 8 promising. User idea (M8 = champion E0 redirected to 1LH, H=1RG---).
2026-10-23 c231ext DONE, NEGATIVE at 8 states (512 ext): no halt after a rebuild; best halter 12a_f-29 (~2x champ_231). 16 clean infinite rebuilders (gadget reads only n, never a residues); 1LH/1LC parity gadget halts n odd but even-n rebuild leaves junk. champ_231 accumulators do NOT share tower residues (a_f=(5*3^(3w+2)-3)/2, parity flips per step) -> needs eng7-style level-table engine. 9-state idea: 1 more state on clean family / 1LH/1LC => 2 rebuilds+halt ~f_w^3(20) > M8; h003 needs ~6. REPORT: bb8_list/investigations/bb8_c231ext/REPORT.txt
