# 10-state machines from the BB(7) champion (started 2026-10-06, user: "try a similar approach ... for a BB(10) champion")

## The bar (CORRECTED 2026-10-07)
- BB(10) champion (Racheline 2024): `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ`. The raw
  wikitext (MediaWiki API) reads `> f_\omega^2(25)` = f_ω(f_ω(25)): f_ω applied TWICE. The rendered page flattened the
  superscript to "fω2", which was first misread here as f_{ω·2}(25). Agent inv-bb10-champion confirms the structure: rows
  A-H are the BB(9) champion's, only the used-up-list rule R4 changes; the run rebuilds twice and halts at the third R4.
- Our BB(9) champion is about f_ω(6*(2^^13 3)) (one rebuild), below f_ω(f_25(25)) since 2^^13 3 << f_25(25).
- A 10-state machine beats the BB(10) champion if (a) it does two or more full rebuild-and-clear cycles before halting, or
  (b) it rebuilds once from a first exhaustion with b of at least about f_25(25) (a start of 25+ digits; the BB(8) record
  has 35). So rec14's rebuild-then-halt candidates ARE record-class if they rebuild twice.

## Size estimates (Knuth random probes, 60 s each, Idle; `est.sh`, `roots_est.txt`, `est_*.out`)

| root | fixed transitions | nodes | holdouts | CPU-h |
|---|---|---|---|---|
| c7m11 | BB(7) champion, first 11 | 1.1e10 | 6e8 | 9e4 |
| c7m12 | BB(7) champion, first 12 (the 9-state record's tree at 10 states) | 4.1e8 | 8e7 | 1e4 |
| c7m13 | BB(7) champion, all 13 reached (E0 = halt free) | 1 | 1 | 0 (the root never reaches E0) |
| rec13 | c7m12 + G0 = 0RH | 5.9e7 | 3e6 | 1.5e3 |
| **rec14** | rec13 + H1 = 0RE | 1.4e6 | 7e2 (heavy-tailed; rec15 says >= 2.6e4) | 14 |
| rec15 | rec14 + E0 = 1LI | 3.4e5 | 2.6e4 | 4 |
| rec16 | rec15 + I0 = 0LH | 8.3e3 | 4 | 0.06 |
| jz8 | BB(9) champion, first 8 (where the BB(10) champion lives) | 1.2e15 | - | infeasible |

The 9-state c7m12 was estimated at 1.6e6 nodes / 15 CPU-h; one more state multiplies the c7m12 tree by about 260, so
the full 10-state c7m12 is out of reach exhaustively (sampling would be possible: knuthfrom probes are random leaves).
rec13..rec16 follow our BB(9) record's TNF path (`rec9_prefix10.txt`): its G0/H mechanism with one extra state J free.

## Runs
- `knuth10.exe`: `../champ12_subtree/knuth_split.cpp` with `-DBBN=10` (MSYS2 g++). dlscan2.exe and trace2.exe handle
  10-state strings (checked: the record padded with an unused J grades NOBOUNDARY, first configuration at step 2149).
- **rec14/** (started 2026-10-06 22:4x): root `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RH0RF_---0RE_------_------`
  (8 2 6), free E0, H0, I0, I1, J0, J1. `knuth10.exe exactsplit ROOT 8 2 6 PART 4 4000 rec14/part_PART.txt`, 4 Idle
  parts (pids in `rec14/pids.txt`); watcher `python ../champ12_subtree/watch_champ.py ../bb10_from_bb7/rec14 35`
  (pid `rec14/watcher.pid`, log `rec14/watch.log`, hits `rec14/watch_hits.tsv`).

## Next
- After rec14: grade its NOBOUNDARY / R4-SOME rows for repeated rebuilds (a multi-exhaustion probe in the style of
  `../bb9_from_bb8/watch_exhaust.py`, with sim9.exe, which runs any number of states).
- Cheap add-ons: redirect roots of the BB(9) record (each transition in turn freed, plus J), as `../bb9_from_bb8/gen_roots9.py`.
- Bigger options (the user's call): rec13 (about 1.5e3 CPU-h), or sampling the 10-state c7m12.

## rec14 results so far (2026-10-07)
- Enumeration complete: 1.54e6 nodes, 104,059 holdouts (4 parts, ~3 CPU-h each; the holdout estimate was far too low).
- Watcher round 1 (29k): 983 NOBOUNDARY, 25 CHAMPION (starts <= 11 digits), 6 R4-SOME; round 2 (75k) running.
- Large-n probe of the 983 (`rec14/bign_r1.tsv`): 445 HALTS-AT-11 (champion-like), 285 NO-HALT, 253 CANDIDATE? in 65
  halting-grid patterns, 59 of them not seen in the 9-state c7m12 run. Not yet analysed.
- (Superseded caveat: the f_{ω·2} reading was wrong; two rebuilds suffice, see "The bar".)

## The BB(10) champion's own subtree (the BB(8) lesson: the 35-digit record was a relative of the BB(7) champion)
TNF path `r10_prefix10.txt`; estimates (`roots_r10.txt`, `est_r10m*.out`, 60 s probes):

| root | nodes | holdouts | CPU-h |
|---|---|---|---|
| r10m12 | 2.9e9 | ~7e5 | 675 |
| r10m13 | 2.6e8 | ~6e4 | 52 |
| r10m14 | 1.2e7 | ~3e3 | 3.6 |
| r10m15..18 | <= 3.6e5 | <= 1.3e3 | < 0.2 |

- **r10m14/** started 2026-10-07: root `1RB1RA_0LC---_0RD1LC_1RA1RG_---0RA_1LB---_1LH1RE_0LI1LH_0LF---_------` (9 2 6),
  4 Idle exactsplit parts (pids `r10m14/pids.txt`). No watcher yet: grading needs the champion's own family (the
  Jacobzheng/Racheline digit lists are unary, Kd ds a b, not the BB(7) champion's template) and an analysis of the
  BB(10) champion's rules, which the wiki does not have.

## c35m14 (started 2026-10-07): the BB(8) 35-digit record's prefix + 2 free states (route (b))
- TNF path of the BB(8) record at 10 states: `c35_prefix10.txt` (first 11 transitions = the BB(7) champion's; then G1 =
  0RH, H0 = 1RG, H1 = 1LF, G0 = 1LC; E0 only at the very end, so it cannot be branched directly).
- Estimates (`roots_c35.txt`, `est_c35m*.out`): c35m12 2.5e9 nodes / 4e4 CPU-h; c35m13 1.1e8 / 870 CPU-h; **c35m14 1.4e6
  nodes / ~12 CPU-h** (free G0, E0, I*, J*). Started: `c35m14/`, 4 Idle parts, watcher (BEST = 35, RECORD-LENGTH flags).
- Triage agent inv-bb10-bb7desc covers rec14 (both rounds) and c35m14: report `../bb10_bb7_descendants.md`.
- r10m13 (the BB(10) champion's own subtree, ~52 CPU-h) started the same day; agent inv-bb10-champion builds its grader.

## BB(10) champion formalized + its subtree graded (inv-bb10-champion, 2026-10-08; report `../bb10_champion_1RB1RA_0LF0LJ.md`)
- `proofs/BB10_champion_1RB1RA.v` check.py PASS (halts, no axioms); `proofs/BB10_champion_bound.v`: exact score b2 + 4
  ones (b2+3 on the tape + the 1RZ write), f_omega(f_omega(25)) < sigma; stronger b1 >= 2^25 * f_25(f_25(2)).
- Structure: rows A-H are the BB(9) champion's; new R4: b odd halts, b = 4m rebuilds [1,(0,0,3)^m,0,0,2], b = 4m+2
  rebuilds [3,(0,0,3)^m,0,0,2]; first list b0 = 28.
- Grader `../bb10_champion_1RB1RA_0LF0LJ/r10grade.py MACHINE [-v]`: all 7,721 r10m14 + 12,067 r10m13-only holdouts:
  **no BEATS-CHAMPION**, 8 EQUAL (incl. the J0-free `..._0LF0LJ_---0LG`, passed to bb8-ab as a redirect root).
- Why: past depth 3 every clearing lands in one of two fixed residues mod 2^K set by parity, so a halter with these rules
  makes at most two deep clearings (the champion uses both); b0 = 28 in every subtree from r10m10 on. The champion's own
  subtree is not a promising source of a BB(10) record.

## Loopers and their neighbours (2026-10-07)
- The triage agent (inv-bb10-bb7desc, report `../bb10_bb7_descendants.md`) found CLEAN INFINITE REBUILDERS in rec14
  (~140 machines, >= 3 classes; e.g. `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RE_---0RJ_0LB0RJ`, 107 share
  its history): K(0^n;0;R) -> K(1^(n+4R-6),0;12;6) -> cleared completely -> K(0^(n+4R-5);0;R'), forever, with no residue
  dependence. A relative that halts at a later exhaustion would beat f_omega^2(25).
- Every rec14 machine shares the 14 root transitions, and every value of a reached free slot is already in rec14, so the new
  territory is changes to the root. `loopnbrs/`: all 2,240 root-changing radius-1 neighbours of the 4 looper
  representatives (`gen_nbrs10.py`): 828 halt early, 15 keep the champion rules (dlscan2 NOBOUNDARY), all 15 NO-HALT on
  the large-n grid. No single root change turns a looper into a halter.
- The 15 rule-preserving changes are H1 (0RE -> 0RF / 1RE / 0RH / 0RI) and G0 -> 0RG (the BB(7) champion's own G0; a
  dead end: E0 is never reached). So the siblings of rec14 inside rec13 (G0 = 0RH, H1 free) are worth enumerating.
  Estimates (`roots_h1.txt`, `est_rec14_*.out`): H1 = 0RF 1 node (dead), **0RH 1.9e6 nodes / 14 CPU-h**, **1RE 1.3e6 /
  24 CPU-h**, 0RI 1.4e7 / 185 CPU-h.
- **rec14_0RH/ and rec14_1RE/** started 2026-10-07 evening: 2 Idle exactsplit parts each + watch_champ watchers.

## Triage result (inv-bb10-bb7desc, 2026-10-07, ~0.85M tokens; report `../bb10_bb7_descendants.md`)
- **No record candidate.** Nothing in rec14 halts after two f_omega-level cycles; nothing in c35m14 halts after a full rebuild
  of the 35-digit list.
- rec14 (2,174 rebuilders, 324 behaviour classes): 744 GROUP-1-LIKE, 587 CHAMPION-LIKE, 8 ONE-REBUILD, 154 infinite
  rebuilders (loopers), 37 runaways, ~640 UNCLEAR (conveyors with D2/D6 blockers, non-champion post-exhaustion processes,
  fit failures). 614 machines followed individually, 1,560 by class (shared first 3,000 canonical configurations).
- Best halter: `..._1LI0LC_..._---0RE_1LJ0LG_0RJ1RI` (6 machines): two full cycles, both at f_omega level 1, about
  f_{12B+1}(f_{12B}(...)) — above our BB(9) record's level, far below f_omega^2(25).
- Loopers (record shape, never halt): 116 + 38 in rec14, 2 in c35m14. A halting relative is the most direct lead; the root
  radius-1 search (`loopnbrs/`) found none, and the H1 sibling subtrees rec14_0RH / rec14_1RE are being enumerated.
- c35m14: all 15,166 holdouts screened; 397 reproduce the BB(8) record's run; none beats its score.
- Resume the member pass if needed: `python ../bb10_bb7_descendants/batch.py members.tsv results_mem.tsv 4 12 150000000`.
- The siblings rec14_0RH / rec14_1RE were not triaged by this agent; the nested detector (dlscan3, `../nested_detector/`)
  includes them in its LOOPER / MULTI / W1-HALTER scan.
- bb8-ab (2026-10-08, `../halt_redirect/champions_redirect.md`): one-new-state halt redirects of the BB(9) and BB(10)
  champions (164 + 180 extensions from the literal halting configuration, b = 1..39 and 1687): no candidate (~20 quick
  halts, 45 certified cyclers, the rest rebuild a list linear in b and never halt) — same two-residue cap as above.
  Not covered: two new states; redirects of transitions other than E0. BB(11) bar (raw wikitext): f_omega^2(10^^^^4).

## M3: f_{omega+1} claim WITHDRAWN (02:35) — halts at I0 at S2 of period 2 after 7 jumps; omega-level 1 at depth ~8 b_f + 50 (sigma >~ 3 R3, ~four nested levels); likely still above 0LJ0LC and 0LA; Coq of the finite chain in progress. Original (superseded) claim below: (inv-bb10-c35-rebuild, 2026-10-08; report `../bb10_c35_rebuild.md`)
- `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA` (BB(8) record + E0 = 1LI, I = ---0LJ, J = 0LD0RA).
- Record run to X(b_f, 35), one full cycle over 8b_f+48 ones, then periods: counter C -= 11, the I/J routine unpacks
  D(2r+3) into ~2r new zeros, whole run cleared again (s -> >= 2^(6s arrows) 3). Real class: tower accumulators s = 8
  mod 11 (2s+4 a tower), r = 3s+1 = 3 mod 11 -> C0 = 0 mod 11 -> one refill -> C' = 1 mod 11 -> halt at I0.
  sigma ~ f_{omega+1}(f_{omega+1}(s1/2)), s1 >= 2^(8b_f+50 arrows) 3.
- Evidence: 16,774 literal stage checks (m3stage0/1, m3rules, m3rules2), 0 mismatches; endgame.py halts for every odd r
  and C = 0..23. Not Coq; stages checked on grids, not for all parameters.
- Residue cross-check (lead): bb8-ab's universal clearing residue U = 49612750485498 satisfies U = 3*B (mod gcd of the
  moduli) with B the record's accumulator, i.e. follow2's R = 3s, so the agent's r = 3s+1 = R+1: R = 2 mod 11 and
  r = 3 mod 11 agree (the apparent conflict was a convention offset).
- Independent verifier inv-bb10-fw1-verify (report `../bb10_fw1_verify.md`) and Coq agent inv-bb10-fw1-coq
  (`proofs/BB10_fw1_*.v`, report `../bb10_fw1_coq.md`) running.
- Coverage of the c35-rebuild tree: 219,088 leaves, 17,033 still-halting followed; ~8,200 runaway/timeout/capped
  unresolved; halt slots first read only in the real class not re-branched (tree built at b = 3).

## Open threads (inv-bb10-open-threads, 2026-10-08, ~0.8M tokens; report `../bb10_open_threads.md`)
- c35m14 exception `..._1LI0LC_1RG1LD_0LD0RH_1RG1LF_0LJ1RI_---0LA`: record-SHAPED (outer Z ~ 7.2B' zeros rebuilt into
  counters/ones lists of length ~Z, cleared by champion rules), halting UNDETERMINED, leaning non-halting: real class
  Z = 48 mod 96, X = 3 mod 48; wrong-class Z = 12 halts at widths 3/7/9; real-class width 3 runs away. Real width 35.
- 27 g-type conveyors: record-shaped loopers (after the groups are used up the head walks off the left 11 and rebuilds a
  list ~ accumulator: 128R+517 ones for E0 = 0LI, D94 lists for E0 = 1LH; cleared in full; later walk-offs rebuild
  again); 216 left-end probes, none halted.
- rec14_1RE (24 rows): 4 looper-shaped (`..._0RI1RE_0LA0RJ_0LC---` + relatives), 18 unary blocker groups, 1 unclear,
  1 non-rebuilder; none halted.

## 2026-10-08 02:15 (after the usage-limit reset)
- **r10m13 PAUSED** (not killed): its 4 knuth10 parts (pids in `r10m13/pids.txt`) were suspended with
  `powershell -File suspend.ps1 -Action suspend -PidFile r10m13\pids.txt` to give cores to M3's verification/Coq (the
  user made M3 the top priority; the champion's subtree is unpromising). Resume with `-Action resume` (no progress lost).
- BB10_champion_upper.v re-verified by the lead from source (separate directory, 1943 s at Idle; own probe re-types
  champion_upper_ex and b1_le_tight; Closed under the global context).
- 0LJ0LC Coq (inv-bb10-lead-0LJ0LC): BB10_lead_1RB0RA.v (halt), BB10_lead_bound.v (score_exact, bf + 4 = arrow 27 2 3,
  b2 + 4 = arrow (4bf+33) 2 5), BB10_lead_vs_champion.v (candidate_beats_champion) compile; check.py pending.
  Relatives with J1 = 1RB (`..._1RE1RI_---1RB`, `..._1RE1LI_---1RB`): CORRECTED by the agent — their start-up rebuild gives an EVEN top, so they halt at the first exhaustion (~3^^50), far below 0LJ0LC and the champion; not candidates. (Earlier note: start with ~53/45-digit lists, possibly
  far larger f_omega^2-class candidates, unverified (still below M3 if M3 holds).
- Nested detector final (inv-nested-detector, report `../nested_detector.md`): dlscan3 v7 re-grade of 248 W1/MULTI rows:
  0 W1, 23 MULTI (all k = 1: 0LJ0LC; rec14 `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RD0RH_1RI0LJ_---0RF`
  R F^22 H, ~f_omega^2(11), below the bar; 21 r10m14 champion-parity rows), 214 MULTI?, 7 LOOPER, 3 REBUILD.
  Coverage: c35m14 done, rec14 36/70, rec14_0RH 12/16, r10m14 ~80%, rec14_1RE + r10m13 not started. Resume (held until
  M3 is done, user 2026-10-08): `bash nested_detector/scans/run10c.sh 2`; BB(8) scan `python nested_detector/bb8_scan.py
  --workers 2` not run yet.

## M3 independent verdict (inv-bb10-fw1-verify, 2026-10-08 ~02:50; report `../bb10_fw1_verify.md`)
- HALTS in I0 at the end of its first period (= the c35 agent's "S2 of period 2 after 7 jumps"), ω-level 1, strong
  evidence, no Coq. σ_ones = 3/2·A'' + A1 + 3/5·A''' + (212B+563)/5 (+1 if the halt writes a 1), 2B+4 = 2↑^37 3;
  σ > 2↑^(8B+57)(2↑^(8B+54)(2↑^(8B+52) 3)) > 2↑^(8B+56) 4.
- 170 literal runs of the final configuration in the real class (incl. B = 6366, halt at step 18,627,354,512) all halt
  with the exact ones formula; 10 stage rules 230-423 random checks each + 2,088 real-shape checks, 0 mismatches.
- Ranking (paper level): M3 > three-cycle sibling padded (< 2↑^(k+47) 4) > 0LA padded (< 2↑^(k+4) 4), k ≈ 2.4·2↑^37 3
  > 0LJ0LC (< 2↑^L 6, L = 4·2↑^27 3 + 17; Coq-proved) > BB(10) champion.
- Gap: uniformity of the exhausted-transit cascade for astronomical W1/A (route depends on W1 mod 5; transit parity).
  Coq: inv-bb10-fw1-coq.
- c35m14 exception `..._0LD0RH_1RG1LF_0LJ1RI_---0LA`: independent verdict NEVER HALTS (strong evidence; report
  `../bb10_c35exc_verify.md`): the inner record-copy game ends in a translated cycler (law Y < 2a+6, real values Y << a).
- **0LJ0LC VERIFIED by the lead (2026-10-08 03:00):** from-scratch rebuild of the whole Coq chain in a clean directory
  (BB102 → BB10_lead_vs_champion), own probe (statements re-typed, tm printed and matched to the string, Closed),
  check.py PASS. Proved: halts, σ = 2·(2↑^L 5) + 2L − 2 with L = 4·(2↑^27 3) + 17, and beats the BB(10) champion.
- 2026-10-08 ~04:00: rec14_0RH enumeration finished (both parts exited). rec14_1RE parts (466420, 478128) and both
  watchers (355912, 127908) SUSPENDED for M3's Coq (pids in `rec14_siblings_paused.pids`; resume with
  `powershell -File suspend.ps1 -Action resume -PidFile rec14_siblings_paused.pids`).

## BB(10) standings (2026-10-08 ~05:45; strong evidence unless marked Coq)
1. n1 `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC` (bb8-ab's G/H family): f_{ω+1}(~1.7B),
   σ > G^N(33), G(x) = 2↑^(x+1) 3, N = (12B+5)/7; independent verdicts: ours `../bb10_n1_verify.md` (+ bb8-ab's fable);
   Coq: bb8-ab's inv-n1-coq.
2. c1 `..._1LI0LC_0RG1LD_1RH1LG_1LC0RG_---1LJ_0RJ0RF` (bb8-ab): 2↑^N 5 < σ < 2↑^N(16B/3+23), N = (76B+141)/3.
3. M3 (ours): σ > 2↑^(8B+56) 4; Coq in progress (inv-bb10-fw1-coq).
4. M3J (ours, J = 1LD1LC): 2↑^(z+4) 5 < σ < 2↑^(z+4) 6, z = (24B+201)/5.
5. bb8-ab's 9-state 3-cycle sibling / 0LH / 0LA (0LA Coq-proved as BB(9)) padded.
6. 0LJ0LC (ours): Coq-PROVED, lead-verified: σ = 2·(2↑^L 5) + 2L − 2, L = 4·(2↑^27 3) + 17; beats the champion.
7. Published champion (Racheline) > f_ω²(25).
(2B + 4 = 2↑^37 3.)
- 2026-10-08 ~12:00: **M3 Coq-PROVED** (inv-bb10-fw1-coq): proofs/BB10_fw1_1RB0RA.v check.py PASS (lead re-ran), bound + beats_lead +
  beats_0LA Closed (lead probe). n1 Coq-proved by bb8-ab (merged into jeff87654/busy-beaver PRs #3, #4). Held jobs resumed
  (r10m13, rec14_1RE + watchers, nested detector run10c.sh 2, check-in scans from dlscan2, check.py on the last three
  1RB1LA proofs and BB9_redir_0LA.v; log tmp/resume_checks.log). bb8-ab's 3-cycle sibling `..._1LC1RH_0LH0RF_---0LA` Coq-proved (BB(9)).
- 2026-10-08 12:00 (user): resumed jobs PAUSED again so bb8-ab's n1 single-file proof can finish: r10m13 (r10m13/pids.txt),
  rec14_1RE parts + watcher (rec14_siblings_paused.pids), check-in scan driver + dlscan2 worker (resumed_jobs_paused.pids).
  Resume all three with `suspend.ps1 -Action resume -PidFile <file>`. The nested-detector resume never started (launch
  failed; rerun `bash nested_detector/scans/run10c.sh 2` from investigations\ later). The 4 check.py re-runs finished: all PASS.
