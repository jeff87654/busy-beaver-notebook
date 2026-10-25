---
name: bb7-holdout-triage
description: "BB(7) holdout dlscan2 pass (16.9M, ~340 CPU-h) replaced by a triage plan 2026-10-21 (user: 'Let's do it!'): 1% sample run + bb7-prefilter agent (--skipdl flag, pf7 reset-signal pre-filter, triage7.py driver)"
metadata:
  type: project
---
Measured 2026-10-21 on 500 holdouts: dlscan ~12 ms/machine (pass DONE 2026-10-05, 2,416 key hits, 14 real lists, 3
rebuilders graded MULTI?/LOOPER by dlscan3 = not halting); dlscan2 ~60-72 ms/machine regardless of census (1M/300k/100k)
or probes: inference 57% + R1-R3 fits 31%; 82% of holdouts get some (permissive u=1/s=0) template, so "has a template"
prunes only 18%. Full dlscan2 pass = ~340 CPU-h (3.5 days at the 4-core cap).

Plan (user approved): (3) 1% random sample (169,944 machines, seed 20261021) through dlscan2 census 300k:
bb7_holdouts/sample1pct_run.py, outputs sample1pct/s_*.tsv + hits.tsv, pid in sample1pct/run.pid, 2 Idle workers
(~3 CPU-h). (1)+(2) agent bb7-prefilter (Opus, bb7_holdouts/prefilter): dlscan2 --skipdl (drop dlscan-covered
templates) as neighbors/dlscan2_skipdl.exe; pf7.exe reset-signal pre-filter (accumulator consumed and regrown:
>= 2 large drops of the longest run at end events), calibrated to 0 misses on cal.txt/champion/h14/sample grades;
triage7.py resumable driver. The lead starts the full pre-filtered run after reading prefilter/REPORT.txt.

**How to apply:** check sample1pct/hits.tsv first (zero CHAMPION/R4-SOME in 170k => low expected yield); never
run the plain 340 CPU-h pass. Related: [[bb8-strategy-review-20261007]], [[bb8-champion-subtree-lead]].

**2026-10-22:** bb7-prefilter DONE (prefilter/REPORT.txt): pf7 "clean transfer" filter passes ~17%, 0 misses on all
graded sets; --skipdl saves only 2%. triage7.py run 2 STARTED 2026-10-22 (pid file triage7_run.pid; status: python
triage7.py status; ~1.5-2 days). dlscan3 over the 2,416 first-pass hits: 0 W1-HALTER/MULTI; agent bb7-hits
(dl3_hits/REPORT.txt) settled all 21 R4-SOME/REBUILD rows: 18 are f_(omega+1)-TYPE NON-HALTERS (families F1/F2/F3
rebuild lists linear in the accumulator, e.g. 423-digit tripling list; a parity invariant always picks the rebuild
branch), 3 not record class; MULTI? b<=k argument holds. NEW DIRECTION: agent bb8-fw1-redirect (bb8_fw1_redirect/)
adds one state to these 7-state f_(omega+1) loopers (M8 trick) hunting an 8-state f_(omega+1) halter (> M8 by an
omega level), then 9 states.
2026-10-22 bb8-fw1-redirect CLOSED NEGATIVE (bb8_fw1_redirect/REPORT.txt, ~370k tokens, 6 core-h): 556k 8-state
redirect nodes over the 18 bases + ~128k 9-state (exhaustion-only slots, 3 bases): at most one certified rebuild then a
halt (<= 18-digit list, ~f_18). Reason: between exhaustions only the accumulator carries over, and with the engine intact
its certifiable info is a residue class fixed by an invariant -> ~1 rebuild max. 9-state 850-digit leaf
1RB1RE_..._1LB0LI_---0LF never halts (accumulator = 18594 mod 2^16 at every exhaustion). Untried: a counter kept
OUTSIDE the list (e.g. parked behind a 00 gap the exhaustion walk reaches). Agent once killed processes by command-line
match (its own folder only; logged) - remind agents: recorded PIDs only.
2026-10-22 bb7-rank DONE (bb7_holdouts/rank/REPORT.txt, rank7.py v2; ~835k tokens incl. 2 subagents): 63 CHAMPION/R4-SOME
rows -> only champ_231/232 beat the champion (est level 21 vs 13, calibrated +-1). X33, Z16 refuted (dlscan2 R3 tail
default); Y19 never halts; P=101 family + C1 never halt; A1/A2 (~level 3) and B1 (sigma ~10^(6.35e38)) HALT but small =
decided BB(7) holdouts, not records. Champion twin 1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF ties exactly.
Run rank7 after each scan (command in REPORT.txt, 20-30 s/row); suggested dlscan2 R3 fix + triage7 status hook in REPORT.
rank7 FINAL (2026-10-23 05:13Z): + invariant search (linear Phi = ca*a+cb*b+cd*sum(ds) mod 2/3/4/6 preserved by all
refit rules -> NEVER-HALTS if no halting exhaustion allowed) and check_controls.py (champion, champ_231 halt; X33, i never
halt: all pass). 63 rows: 2 RECORD? (champ_231/232), 2 CLOSE (champion + exact twin), 20 NEVER-HALTS, 21 REBUILD,
14 LEAVES-TEMPLATE, 4 below. Run rank7 + check_controls after the remaining BB(7) scan.
2026-10-23 user approved: agent reb7 (Opus, bb7_holdouts/reb7) triages 7-state REBUILDERS (~790 now: 698 in
bb9_fw1_hosts/cls_all.tsv incl. 640 OUT/grow; ~1000-1500 after the scan) for "rebuild then halt" (f_omega class >>
champ_231): families -> halt reachability (backref) -> invariant lock through rebuilds -> residue-FAITHFUL re-test of
survivors (real accumulator residues, Res.v-style), controls incl. M8 as positive. Side pool: 8-state rebuilders
(rank/bb8/rank8.tsv; ranking run on the 21 BB(8) graded rows found nothing: 18 rebuild forever, H8, 2 refit failures).

2026-10-22 late: user OK to run reb7 on ALL promising candidates (all dlscan3 rebuild rows, unsettled CHAMPION/R4/Ackermann rank rows, 8-state rebuild rows, and new triage7 rows incrementally); ~20 s/machine, 2 cores, resumable driver.

2026-10-23 reb7 DONE: BB(7) triage7 scan finished (1828 hits); all 1797 7-state rebuild/digit-list rows classified: 762 NEVER (no halting class at true exhaustion; 9 by parity invariant), 1003 not record class, 32 small halters (champion/twin, champ_231/232, A1/A2/B1 siblings, 1RB1RD_1LC0RD_... ~5-6 arrows). No rebuild-then-halt record. N2 (segment f_omega rebuilder, f_(w+1) if it halted) in OPEN low. CAVEAT: pipeline does not reproduce M8 rebuild-then-halt, only flags it (T); all 7-state T rows resolved by hand. REPORT: bb7_holdouts/reb7/REPORT.txt.
2026-10-23: launched n2-decide (Opus, bb7_holdouts/n2_decide) to prove N2 halting/non-halting (regular-language certificate or segment invariant; Coq if feasible).
2026-10-23 N2 SETTLED: never halts, Coq (bb8_list/proofs/BB7_N2_1RB0RC.v + relabel BB7_N2m_1RB1RE.v, check.py PASS, re-run by lead). Segment parity invariant (phase O all odd / phase E); generic deciders (NGramCPS 12/12, tctl) fail. Candidate for bbchallenge holdout contribution (user call).
2026-10-23 reb7 FINAL: 1876 7-state rows: 832 NEVER, 1003 not record class, 32 small/known halters, 9 open (doubling counters, not record class). 1611 bounded prefilter rows probe-only. 19 M8-style escalators end in translated cyclers (log-size counter). Conclusion: BB(7) holdouts contain no rebuild-then-halt record; champ_231/232 only record-level halters. Corrections sent to reb7 (N2 Coq, 8-state row NGramCPS).
2026-10-23 reb7 closed the 2 unclassified rows: 1RB0LF_0RC0LG_... = relabel of settled f_(w+1) never-halter (start state differs); 1RB0RD_0LC1RF_... fixed-depth (<= f_3), halting undecided at 7e10. FINAL 1876: 833 NEVER / 1004 not record / 32 small-known halt / 7 open likely cyclers. BB(7) hunt via holdouts CLOSED.
