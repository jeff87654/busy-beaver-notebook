---
name: strategy-20261024-bb8-two-agents
description: "2026-10-24 BB(8) strategy (user asked highest-yield routes for a new BB(8) champion): launched Opus agents m8sweep (M8 recipe over all ~1,870 7-state f_omega rebuilders, real-orbit follower) and twoslot8 (two-change 8-state neighbourhoods of champion / champ_231 / M8)"
metadata:
  type: project
---
Ranking given 2026-10-24 (bar = M8, f_w^3(12..13); budget argument: 8 states = 7-state f_omega engine + 1 state, so
f_(w+1) at 8 is structurally blocked and the yield is the real-orbit "round lottery", which produced M8/h003/C7):
1. m8sweep (Opus, bb8_list/investigations/bb8_m8sweep/): redirect the first-exhaustion slot of EVERY 7-state Ackermann
   rebuilder in bb7_holdouts/reb7/final_all_verdicts.tsv (NEVER + NOT-RECORD-CLASS + halters; excluding the 18 fw1
   loopers, A/B/C+siblings+N2, champion set8, champ_231 c231ext already done) into a new state H; literal prefilter,
   then a real-residue per-round follower (reb7 rounds/mrounds + never_audit symsim); success = halt at round >= 4.
   Must rediscover M8 (round-3 halter) as positive control before any negative counts. The 2026-10-23 "low yield"
   dismissal rested on the fw1-looper <=1-rebuild argument, which does not cover f_omega bases (M8 is the counterexample).
2. twoslot8 (Opus, bb8_list/investigations/bb8_twoslot/): one new state + ONE redefined transition around the BB(7)
   champion, champ_231/232, plus M8 with one slot changed; same follower, same M8 control, must not flag set8's
   4-escalation rows.
3. Not launched (listed for later): 8-state branch continuation of the 452,828 >=2-undefined holdout rows via a NEW state
   (un-enumerated BB(8) TNF territory). Judged low: f_(w+1) at 8, more BB(7) passes, collapse searches, Y-type, designs.
**How to apply:** read both REPORT.txt files before relaunching; append outcomes here; any multi-round candidate goes to
OPEN_CANDIDATES.txt. Related: [[strategy-20261023-three-agents]], [[m8-bb8-c04-collapse]], [[screening-lessons]],
[[fw1-search-20261022]], [[bb7-holdout-triage]].

2026-10-24 ~15:50 m8sweep STOPPED EARLY (user low on budget), INCONCLUSIVE not negative (bb8_m8sweep/REPORT.txt): tracer
(zfg7-based) passes the M8 control (3 rounds from blank; wrong residue class halts one round early, so per-base tower
classes mod 720 were computed with reb7's residue engine; champion = 366 mod 720). Pool 769 f_omega bases - 53 done =
716; 389 have an exhaustion-only slot (engine-preserving redirect), 327 do not (not screened). Only 92/716 got tier 1:
no child halts after >= 2 rounds; ~178 run past 4 rounds = linear-growth two-phase rebuild loops the LOOP check misses.
Champion twin control unfinished (round 3 reached, final pass not run); h003 control not run (12x/round too costly).
RESUME: python launch.py jobs_scr.txt 3 (skips finished) -> tier.py passes 2-3 -> collect.py; bash ctl_chain.sh first.

2026-10-24 ~16:00 twoslot8 STOPPED EARLY, PARTIAL NEGATIVE (bb8_twoslot/REPORT.txt, ~13 core-h): 21,896 one/two-slot
parents per base (champion, champ_231, champ_232) + 480 M8 one-slot changes; stage 1 (1e7-step blank-run comparison)
keeps 357/465/459/64 engine-intact children, 579k DIVERGED children UNSCREENED (could be "champion rules, bigger first
list"). Control PASS: M8 + 4 twins rediscovered from the champion (2 escalations in world W2); set8 Q5 rows not flagged.
Champion+M8 world tree 1637 leaves: halts at 0 esc 385, 1 esc 0, 2 esc 7 (all M8 skeleton, first list 817), >= 3 none;
1145 non-halters have no reachable halt; 100 deep (5e9): small halts / rebuild loopers / Z1-type; a0230 open (<= 1 esc).
c231f.exe (champ_231 world follower from Coq rules R1ITER/CDP, validated vs Coq score) built but the champ_231/232
trees (924 children) NOT run. Tools: pkf8t/pkf8q (--qset for clone states), batt/batt231 jump batteries.
RESUME: REPORT section 7: 7.1 diverged-child battery -> world tree; 7.2 champ_231/232 trees (both parities); 7.3 --qset reruns.
CAVEAT: the champion/M8 world tree ran BEFORE the clone-state (--qset) fix; its negative is provisional until REPORT item 7.3 reruns it. deep1b stopped at 99/100 rows.
