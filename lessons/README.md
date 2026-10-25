# Lessons

The lead Claude agent's long-term memory from the project (2026-09-26 to 2026-10-25): one fact, method or
lesson per note, usually with **Why** and **How to apply** lines. `[[name]]` links point to other notes here by
their `name:` field; a few point to notes that were not published. Paths inside refer to the original working
folder `C:\Users\jeffr\Downloads\bb8\`, which is `../workspace/` in this repository.

Good first reads: [screening-lessons](screening-lessons.md), [bb8-hunt-working-style](bb8-hunt-working-style.md),
[bb8-first-return-map-method](bb8-first-return-map-method.md), [fw1-search-20261022](fw1-search-20261022.md),
[strategy-20261023-three-agents](strategy-20261023-three-agents.md),
[formalization-estimates-too-high](formalization-estimates-too-high.md).

- [argon-bb9-fw2](argon-bb9-fw2.md): Argon's 9-state blank-tape f_omega(f_omega 465009) machine 1RB0RD_... (2026-10-15) verified by me 2026-10-16; its M9 (2026-10-14) is NOT a blank-tape f_(w+1) machine
- [bb10-n1-coq](bb10-n1-coq.md): n1 (10-state, f_(omega+1)) halting proof BB10_n1.v passes check.py; bound file beats BB(10) champion and 0LJ0LC (2026-10-08)
- [bb10-selector-c1-counter-grower](bb10-selector-c1-counter-grower.md): Selector search (2026-10-08; SCREENING EVIDENCE ONLY, independent verification pending as of 06:15): n1 = GH machine ..._1LI0LC_..._0LJ0LI_---0LC is an f_(omega+1)-class grow-and-count halter (follow2 level rises per period, counter 12B+7, halts at exhaustion for B's class); c1 (omega-level 1, index ~25B) and G6 (non-halting) are the cousins; tools in halt_redirect/sel/
- [bb12-t12a-coq](bb12-t12a-coq.md): T12a 12-state f_(omega+1)^2 halter: proofs/BB12_T12a.v check.py PASS, bound file beats n1 (2026-10-10); round-2-end spec workflow and pitfalls
- [bb17-bb18-champion-anatomy](bb17-bb18-champion-anatomy.md): Anatomy of Jacobzheng's BB(17)/BB(18) f_(omega+2) champions (2026-10-09): 7-state f_omega engine + 4-state counter layer + 6-state merge/parity layer; rules verified; notes in bb_champs_17_18/NOTES.md
- [bb43-champion-coq](bb43-champion-coq.md): BB(4,3) champion 1RB1RD1LC_2LB1RB1LC_1RZ1LA1LD_0RB2RA2RD Coq-proved 2026-10-17 (halts + exact sigma = 4 e4 + 18 > 2^^^2^^^2^^^(2^96-1)); 3-symbol busycoq pitfalls
- [bb7-c231-coq](bb7-c231-coq.md): BB(7) record candidates champ_231/232 (Argon) Coq-proved 2026-10-22, sigma = 2*W20(5)+7 > 3↑^20 3; proof layout + pitfalls
- [bb7-champ231-lead](bb7-champ231-lead.md): !!! 2026-10-22 possible NEW BB(7) RECORD champ_231 = 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB (+ champ_232 G0=1LC) from the BB(7) holdout list; Argon claim ~3↑^20; c231-check + c231-coq launched
- [bb7-holdout-triage](bb7-holdout-triage.md): BB(7) holdout dlscan2 pass (16.9M, ~340 CPU-h) replaced by a triage plan 2026-10-21 (user: 'Let's do it!'): 1% sample run + bb7-prefilter agent (--skipdl flag, pf7 reset-signal pre-filter, triage7.py driver)
- [bb7-n2-decided](bb7-n2-decided.md): BB(7) holdout N2 (segment-coded f_(w+1) rebuilder) and its relabel proved NEVER HALT in Coq, 2026-10-23
- [bb7-never-audit](bb7-never-audit.md): 2026-10-24 adversarial audit of reb7's biggest BB(7) NEVER-HALTS verdicts: none broken (160/173 confirmed via symsim-measured rules + invariants); tools in bb7_holdouts/never_audit
- [bb8-annotated-ngcps-g](bb8-annotated-ngcps-g.md): When plain NGramCPS fails because a sweep runs off a forgotten tape end, writer-annotated windows + halting-reach set g close it tiny (m7 1RG0LC PROVED 2026-10-08)
- [bb8-first-return-map-method](bb8-first-return-map-method.md): Method that cracked a non-counter BB(8) holdout (048631 1RB0RC1LB1RD): probe the family with random states, fit the first-return map, validate on a long orbit
- [bb8-hunt-working-style](bb8-hunt-working-style.md): How the user likes the BB(8) search work run: series with lessons learned, cheap automation before tokens, verified results
- [bb8-m7-nobd-1RH1LG-r4](bb8-m7-nobd-1RH1LG-r4.md): R4 structure of the m7 NOBOUNDARY machine 1RB0RA..1RH1LG_0RG1LD_0RH0RF (rebuild to a P-less list, D2 stage, final cycler) and the P-less K-parser trick
- [bb8-ngcps-long-windows](bb8-ngcps-long-windows.md): NGramCPS with long asymmetric windows (nL=10,nR=14) proved the m7 0RB0LC champion-tower machine; reusable verified Coq checker generator
- [bb8-strategy-review-20261007](bb8-strategy-review-20261007.md): 2026-10-07 strategy review for a new record candidate - the unexplored halt-redirect gap (TNF never branches the records' never-reached halt transitions), the never-queued roots_grade pocket, BB(7) list dlscan2 pass not run
- [bb9-c7-lead](bb9-c7-lead.md): !!! 2026-10-20 BB(9) lead C7 = M8 with H0=0LI, I=1LC0RA (1RB0RA_..._0RG0RF_0LI---_1LC0RA): 11 top-level rebuilds then a class-independent 9-step cascade halt, ~f_w^6(11); strong evidence; c7-check + c7-coq + c7-triage agents launched 2026-10-21
- [bb9-f3-0rc-candidate](bb9-f3-0rc-candidate.md): !!! 2026-10-19 BB(9) lead f3_0RC = M8 with H0 = 0LI, I = 0RC 1RF (y1-fable F3 screen): bigger 2nd escalation, then M8's cascade; claimed to beat M8 in EVERY class if parametric; checks pending
- [bb9-fw1-search-status](bb9-fw1-search-status.md): 9-state f_(omega+1) search (2026-10-09): closed slices (record base + 1 state; BB(7) champ + I,J; c7m12; all 11-digit/35-digit engines + 1 state; roots9; BB(7) Ackermann parents are fixed-depth); n1f0 = c7m10 F0=0RG branch ENUMERATED (394k holdouts), dlscan3 scan nested_detector/scans/n1f0; structural lesson
- [bb9-gh0LH-verify-lessons](bb9-gh0LH-verify-lessons.md): Lessons from verifying the 9-state G/H-swap redirect (---0LH); representatives mod 2520 are 2-adically unfaithful; tools in halt_redirect/ghv
- [bb9-redir-0la-coq](bb9-redir-0la-coq.md): BB(9) redirect candidates 0LA and its three-cycle sibling (..._1LC1RH_0LH0RF_---0LA) proved halting in Coq with exact scores beating the BB(9) record (2026-10-08); tooling lessons
- [bb9-y1-class-dependent](bb9-y1-class-dependent.md): Y1 (M8 + H1->0LI, I=0RA---) is OPEN/not certifiable: halts at M8's point (sigma(M8)-1) in key31 rho 0/4; extensions of M8's halt are class-dependent
- [c04-bb9-candidate](c04-bb9-candidate.md): !!! C04 (1RB0RA_..._1LH0LC_..._1RI---_0RI0RF) 9-state record candidate: halts after its 2nd escalation, sigma > f_w(f_w(12B+24)) >> fw2 (STRONG EVIDENCE via parity invariant, c04-fable 2026-10-17); Coq agent c04-coq started
- [c04-bb9-parity-record](c04-bb9-parity-record.md): C04 (BB9 record completion 1RB0RA_..._1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF) halts after 2nd escalation, sigma > f_w(f_w(12B)) -- parity invariant of its 5-adic chain; Coq-proved 2026-10-18 (see c04-bb9-candidate)
- [c04-coq-endgame-lessons](c04-coq-endgame-lessons.md): Lessons from closing C04's Coq endgame: reuse generic per-J lemmas at small L, clean explore targets, capture exact halt/K-moment configs by single-stepping
- [c7-bb9-coq](c7-bb9-coq.md): C7 = M8 + H0=0LI, I=1LC0RA: BB(9) record Coq-PROVED, N > f_omega^5(2*2^^13 3) and f_omega^6(12) (Lower5), PUBLISHED PR #32; mexp + fixpoint-unification lessons
- [coq-selfcontained-merge-lessons](coq-selfcontained-merge-lessons.md): How to merge busycoq-based multi-file Coq proofs into ONE self-contained .v (gen_selfcontained.py for BB9, gen_selfcontained_n1.py for BB10 n1) and the pitfalls met 2026-10-06/08
- [f3-0rc-bb9-candidate](f3-0rc-bb9-candidate.md): !!! f3_0RC = M8 with H0=0LI, I=0RC/1RF: 9-state machine beating M8 in EVERY class, COQ-PROVED 2026-10-20 (bb9_f3_coq, lead re-ran probe 2026-10-21); packaging PR bb9-f3 by agent f3-package; dominated by the C7 lead if that proves
- [formalization-estimates-too-high](formalization-estimates-too-high.md): My Coq formalization effort estimates run 3-10x too high; calibrate down and don't let them gate decisions
- [fw1-search-20261022](fw1-search-20261022.md): 2026-10-22 f_(omega+1) plan after h003: residue-driven exits cap at f_w^k (fixed k); agents fw1-counter9 (counted-halt gadget on the 18 BB(7) f_(w+1) loopers) and topmap-sweep (top-map + real orbit over all M8 extensions)
- [gpp-path-pitfall](gpp-path-pitfall.md): compiling C++ tools on this machine: g++ by full path fails silently (exit 1, no output); put C:\\msys64\\ucrt64\\bin on PATH first
- [kill-only-own-pids](kill-only-own-pids.md): Never kill coqc/python by image name or start time; only by the PID recorded at launch (other agents share the machine)
- [m11-argon-bb11](m11-argon-bb11.md): Argon's 11-state M11 is NOT a BB(11) record; its title claim f_(w+1)(f_w(f_8 2)/3) is false (Coq-refuted 2026-10-16); lia/zify sealing pitfall
- [m13-argon-bb13](m13-argon-bb13.md): 13-state f_(omega+2)(f_omega 20) halter M13, found/proved by Gemini \"Argon\" 2026-10-14 in bb8_list/proofs/BB13_M13*.v; verified by me
- [m14-argon-bb14](m14-argon-bb14.md): M14 = 14-state f_(omega+2)^3 halter written by Gemini \"Argon\" (2026-10-13), Coq in proofs/BB14_M14*.v; independently verified by me same night
- [m254-tm-layer](m254-tm-layer.md): zfc_254 TM layer (zf/m254/tm) DONE 2026-10-14: tm254_rm : halts tm c0 <-> rm_halts p254 ([], R0) closed via certified symbolic executor on the final table; check_tm254.py
- [m254gb-goldbach-machine](m254gb-goldbach-machine.md): Project started 2026-10-24: TM halting iff PA ⊢ Goldbach (user switched from ZFC to PA); native PA proof-search machine, workspace zf/pagb, agents pagb-machine + pagb-coq
- [m254tg-ac-zfcgu](m254tg-ac-zfcgu.md): zf/m254tg/ac — Con(ZF+GU) -> Con(ZFC+GU) via L + condensation, DONE 2026-10-14 (3.78k lines, CHECK PASS); headline tg296_halts_iff_ZFCGU
- [m254tg-universe-machine](m254tg-universe-machine.md): Project (started 2026-10-14): TG-strength TM (halts iff ZF + Grothendieck universes inconsistent) built on the 254 machine; UG schema design, agents, workspace zf/m254tg
- [m8-bb8-c04-collapse](m8-bb8-c04-collapse.md): !!! 2026-10-18: C04 collapses to an 8-state machine M8 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG--- (same tape, sigma = sigma(C04) ~ f_(w+1)(3)), a huge BB(8) record; Coq transfer agent m8-coq running
- [open-candidates-log](open-candidates-log.md): User wants a durable log of potentially record-beating machines we can't settle yet: bb8_list/investigations/OPEN_CANDIDATES.txt
- [pa-goldbach-coq](pa-goldbach-coq.md): PA ⊢ Goldbach TM (zf/pagb, 449 states, frozen): Coq end to end closed 2026-10-25 (Headline.v); layers, pitfalls
- [popen-create-no-window](popen-create-no-window.md): Agent-launched exes pop a visible console window on the user's screen unless Popen uses CREATE_NO_WINDOW (0x08000000); put it in every agent brief
- [screening-lessons](screening-lessons.md): Lessons on our screening pipeline (2026-10-22 after champ_231): rank by estimated size not grade name; never dismiss a top grade by base rate; positive controls; re-screen after bug fixes
- [strategy-20261023-three-agents](strategy-20261023-three-agents.md): 2026-10-23 strategy review (post h003/champ_231) and the three Opus agents launched: collapse-search (h003/C7/n1 state collapse), bb7-nonlist (BB(7) holdout non-digit-list residue), pocket-rescreen (roots_grade + unranked 8-state rows)
- [strategy-20261024-bb8-two-agents](strategy-20261024-bb8-two-agents.md): 2026-10-24 BB(8) strategy (user asked highest-yield routes for a new BB(8) champion): launched Opus agents m8sweep (M8 recipe over all ~1,870 7-state f_omega rebuilders, real-orbit follower) and twoslot8 (two-change 8-state neighbourhoods of champion / champ_231 / M8)
- [w2-12state-search](w2-12state-search.md): f_(omega+2) 12-13 state search (started 2026-10-09): bases G6 (looper, rounds reload counter) and n1 (J0 gadget); brief + agents in investigations/w2_search/
- [wiki-champion-rows-convention](wiki-champion-rows-convention.md): The BB wiki champion table blanks rows n dominated by a smaller-n machine (11-13 blanked after n1 at 10); H14 proof not needed
- [zf-ac-relcon](zf-ac-relcon.md): zf/zfc — object-level Con(ZF)->Con(ZFC) via L in the Kirst-Hermes Coq library, DONE 2026-10-11 (CHECK PASS, closed); design + pitfalls
- [zf-axtext-rep-fiber-bound](zf-axtext-rep-fiber-bound.md): ZF machine shrink 354->336 by replacing REP's functionality hypothesis with a fiber bound (POW, UNI dropped); Coq closed in zf/axtext/coq/R3
- [zf-framework-design-lessons](zf-framework-design-lessons.md): ZF-machine (halts iff ZF inconsistent) framework-level design study 2026-10-10 — measured negatives (single chain, boot, O(1) dispatch, string-stack machine) and where the states go
- [zf-framework-study](zf-framework-study.md): ZF-machine framework-level study (2026-10-10): Wade's register-DAG framework is near-optimal; measured negatives for register-stack op and tape-native strings; cost rule for new ops
- [zf-l3-tm-sim-lessons](zf-l3-tm-sim-lessons.md): ZF 393-state machine L3 (TM simulates RM) done 2026-10-10; list-zipper approach + Coq pitfalls with busycoq on a big machine
- [zf-machine-reduction](zf-machine-reduction.md): ZF-inconsistency TM state reduction (Wade's 393 framework) — results, tracks A/B/C, tools in zf/reduce
- [zf-regcon-regularity](zf-regcon-regularity.md): Con(ZF-Reg)->Con(ZF) formalized in undecidability-library FOL syntax (zf/regcon, 2026-10-10); library ZFeq has open schema instances (pitfall)
- [zfc254-logic-scoping](zfc254-logic-scoping.md): zfc_254 (third-party 254-state ZFC machine) program/logic-layer scoping 2026-10-13 - coding differs from Wade, spec validated, quotient interpretation is the crux
