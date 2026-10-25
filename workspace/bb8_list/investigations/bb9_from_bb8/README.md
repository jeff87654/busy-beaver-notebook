# 9-state machines from the BB(7) champion (started 2026-10-05)

## The bar
- The BB(9) champion `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH` (Jacobzheng 2024) has
  sigma > f_omega(f_9(2)), machine-checked here in `../../proofs/BB9_champion_bound.v`.
- A champion-type machine whose list just runs out and halts reaches about 2^^(L+1) 3 for L digits. That is far
  below the bar for any start length that is reachable.
- What can beat it is a machine that **rebuilds its list once and halts at the next exhaustion**. Halting after
  one rebuild of a 30-digit rebuilder gives about f_omega(2^^31 3) > f_omega(f_9(2)).
- So grade for R4-SOME / HALT-SOME and mixed (n, b) grids (`../rebuilder_nbrs/r4grid.py`, n up to 12), not only for
  CHAMPION. CHAMPION hits are still recorded with their start length.

## Runs
- `knuth9.exe`: `../champ12_subtree/knuth_split.cpp` built with `-DBBN=9` (MSYS2 g++ at C:\msys64\ucrt64\bin).
- Size estimates (Knuth random probes, 60 s each; `champ7_prefix9.txt`, `est_m*.out`) for the champion's TNF
  prefix of the first m transitions, as a 9-state root:

  | m | nodes | holdouts | CPU-h |
  |---|---|---|---|
  | 7 | 1e12 | 5e2 | 1e5 |
  | 8 | 1.6e10 | 27 | 4.9e3 |
  | 9 | 4.8e9 | 6.7e6 | 1.9e3 |
  | 10 | 2.1e8 | 3.1e3 | 487 |
  | 11 | 3.2e7 | 1.7e5 | 205 |
  | 12 | 1.6e6 | 6.3e4 | 15 |

- **c7m12/** (first experiment, user choice: the BB(7) champion as the root):
  - Root `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_---0RF_------_------`; free E0, G0, H0, H1, I0, I1.
  - `knuth9.exe exactsplit ROOT 7 2 6 PART 4 4000 c7m12/part_PART.txt`: 4 Idle parts; pids in `c7m12/pids.txt`.
  - The hourly watcher `../champ12_subtree/watch_champ.py ../bb9_from_bb8/c7m12 35` grades new holdouts with
    dlscan2 and records first family configurations in `c7m12/watch_hits.tsv`, plus RECORD-LENGTH for starts over
    35 digits. Log: `c7m12/watch.log`.
- **Next:** m = 11, which frees G1 as the 8-state find needed (about 205 CPU-h).
- **Ready but not run:** `roots9.tsv` (`gen_roots9.py`): 79 redirect roots of the rebuilders p0-p3 and the
  35-digit machines, each with one transition plus the new state I free. Tiny subtrees (estimates: ~5e3-7e3 nodes,
  1-70 CPU-s per root). Run with `python run_roots9.py roots9.tsv roots9_out 4`.

## Interim results (2026-10-05 evening, c7m12 with 3 of 4 parts done, 16,188 holdouts graded)
- Watcher grades: 233 CHAMPION (229 with the champion's 11-digit start, 2 with 1 digit, 2 with 2 digits; none
  longer), 113 NOBOUNDARY, 1 R4-SOME, 1 HALT?.
- **R4-SOME** `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RH0LC_1RG1LD_0RH0RF_1LI0LE_---0RG`: the champion's rules and start; the
  exhausted case halts for every b at n >= 2, including the real first exhaustion n = 11 (`c7m12/r4some_probe.txt`).
  Champion-like: halts at its first exhaustion, so its score is on the BB(7)-champion scale.
- **nob_screen GRID-HALT (27 nine-state rows)**: 23 share one pattern (E0 redirected into I: `0RI0LC`). Extended
  probes (n up to 12) show they halt at n = 11, again champion-like.
- **Large-n probe** of all 113 NOBOUNDARY rows (`bign_probe.py`, n = 11..49, b = 0..13; `c7m12/bign.tsv`): 79
  NO-HALT, 25 HALTS-AT-11, 9 CANDIDATE? (no outcome at n = 11 within 2e7 steps, halts at several larger n).
- **CANDIDATE? `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0RE0LG_---1LF`** (7 rows share its grid), traced from
  K(0^11; 0; b) with `watch_exhaust.py`:
  - for b >= 1 the exhaustion first rebuilds a new list on the left whose length grows with b (about 6b - 1 blocks);
  - then a b-independent process runs at the right end: one run shrinks (01)^28 -> 19 -> 10 over 1e5..3e8 steps
    while another grows. Still running at 3e8 steps (34,598 cells).
  - If the right-end process ends and the machine returns to the rebuilt list, this is a rebuild driven by the huge
    b of the real run: the f_omega-type growth that could matter for BB(9). Under investigation.

## Candidate verdicts (2026-10-06, Opus investigator; report ../bb9_c7m12_1RB0RA_0RI0LC.md)
- Group 1 (`..._0RI0LC_..._0RE0LG_---1LF` + 6 relatives): HALTS at the inner exhaustion; sigma = 12*(2^^13 3) + 3*(2^^6 3) - 13. The rebuilt list L(B) is never used.
- Group 2 (`..._0LI0LC_..._0RE0LG_0RF---`, `..._1LI0LC_..._1RH---`): HALTS; the second rebuild over L(B) forms (12B-30)/7 groups but only the last group is used; sigma ~ 17.1*(2^^13 3).
- Neither comes near f_omega(f_9(2)). The f_omega shape (a rebuild over a list whose size grows with b) did appear, but the run used only a small part of the rebuilt list before halting.
- Caveat for future screening: probe2 has a tape cap that hides many exhausted-case halts (its "T" is not "no halt"). Use sim9.exe for long runs.

## c7m12 complete (2026-10-06)
- 4/4 parts finished; 57,947 holdouts graded by the watcher: 502 CHAMPION (all with the champion's 11-digit start or
  shorter), 282 NOBOUNDARY, 3 R4-SOME, 1 HALT?.
- Large-n probe of all 282 NOBOUNDARY rows (`c7m12/bign_all.tsv`): 221 NO-HALT, 40 HALTS-AT-11 (champion-like),
  21 CANDIDATE?. Nine of the CANDIDATE? rows are groups 1 and 2 (settled above: both halt, not records). Twelve new
  variants of the same E0 -> I mechanism, plus one R4-SOME with an inconclusive n = 11 probe, went to the same Opus
  investigator for classification.

## !!! Possible BB(9) record (2026-10-06, unconfirmed)
`1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---` (and twin `..._0RH0RE_0LH---`): at the first
exhaustion they rebuild one champion list of 12b-12 ones, which the champion rules consume; probes of the end of the list
halt. If confirmed: sigma >~ 2^^(6*(2^^13 3)-35) 3, far above f_omega(f_9(2)). Verification by inv-bb9-cand-opus is in
progress, followed by an independent check by the lead.

## CORRECTION (2026-10-06): the record claim is UNSUPPORTED
At the D2 stage `[4,21,4,2,0^k | a=D1]` (k = 12B-11) the machine does not do the champion R3 borrow into the second D4.
It rebuilds irregularly instead (the tail grows; the structure depends on k), and sim9 finds no halt within 2e9 steps
for k = 1..3. The earlier end-of-list halts (the investigator's and the lead's verify_chain sweep) were for shapes the real
run never reaches, and verify_chain.py's parser silently matched nothing when the tail differed from j = 6. Halting is
open; inv-bb9-record-coq is characterising the D2 stage by simulation.

## Update (2026-10-06): halting supported again, via the D2 stage
The D2-stage outcome depends on k mod 5. The real k = 12B - 11 is 1 mod 5 (2B+4 = 2^^13 3 = 1 mod 5). For k = 1 mod 5
with k >= 11, `[4,21,4,2,0^k | a=D1]` (tail j = 6) halts with ones exactly 2r + 9q + 78 (q = (k-1)/5, r = 3b'+2). The
lead reproduced this for k = 11..61 and b = 0..20 on both twins (378 cases). Status: strong evidence. The Coq proof
(stages a-f, including a comparison with the BB(9) champion's actual score) is in progress. No claim until it is done.

## RESULT (2026-10-06): a new BB(9) champion candidate, fully machine-checked
`1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---` (twin `..._0RH0RE_0LH---`), found in c7m12, the 9-state
TNF subtree below the BB(7) champion's first 12 transitions. All checked by the lead: check.py PASS for both halting
files, and probes of the statements and assumptions for the rest.
- `proofs/BB9_record_1RB0RA.v`: `halt : halts tm c0` (built in ~43 min); twin `BB9_record_twin_1RB0RA.v`.
- `proofs/BB9_record_bound.v`: ones at the halt = 3*(2^^(12B-9) 8) + 108*floor(B/5) + 70 with 2B+4 = 2^^13 3;
  sigma > 2^^(2^^13 3) 3.
- `proofs/BB9_record_vs_champion.v`: `record_beats_champion`: the BB(9) champion (Jacobzheng) halts with b2+3 ones and
  ours halts with N > b2+4 ones; corollary `sigma_ours_gt_champion` states it in standard-score form: Nc + 1 < No (champion halts on E0 with 1RZ, ours on I1 reading a 1).
How it works: the BB(7) champion's program, then a rebuild of the list with 12B-11 digits, then a countdown, then a
halt that depends on B = 1 mod 5. Report: investigations/bb9_record_1RB0RA_1LI0LC_coq.md. Announcing is the user's call.
- 2026-10-06: the lead rebuilt the whole set from scratch in a clean directory (BB92, Individual92, halting 3012 s,
  bound 293 s, champion files 34 s + 26 s, comparison 67 s, twin 3161 s). Every theorem is "Closed under the global
  context", and all three printed tm tables match the machine strings entry by entry.
