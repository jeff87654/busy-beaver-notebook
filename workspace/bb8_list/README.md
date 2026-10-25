# BB(8) holdout list

A public-ready list of 8-state, 2-symbol holdouts from mxdys's TNF enumerator, with every holdout
ranked by a growth heuristic. As of 2026-09-26 no public BB(8) holdout list exists. The wiki's
Nov 2025 sample is cited only through Discord.

## Method
- **Enumerator.** github.com/ccz181078/TM `main.cpp` at a41db6c (sha256 22294ab2…, identical to
  upstream HEAD) with an 8-state config block (N_STATE=8, N_CHAR=2, log2_N_STATE=3, log2_N_CHAR=1).
  The only additions are the deadline/checkpoint hooks in `../mxdys_pilot.cpp` and `../mxdys_resume.cpp`.
  Subtask ids 0..999999 use the upstream partition.
- **Parallel runner.** `run_job.py`:
  - a 60 s seed run finishes the BFS partition;
  - the frontier is then split into chunks and resumed by a worker pool with 1-hour slices, re-splitting as needed;
  - the runner is crash-safe and restartable.
  - Validated on BB(7) subtasks 614767 and 530167 (`jobs7/`): identical node counts and holdout sets to uninterrupted runs, including 80 forced re-splits.
- **Job order.** `jobs_order.txt` = `random.Random(20260926).sample(range(10**6), 1000)`.
- **Ranking.** `rank_incremental.py` ranks each chunk's holdouts as soon as the chunk is accepted.
  - Settings: Ligocki Quick_Sim (unmodified, `../third_party/ligocki` @ 1b31c66, venv `../third_party/venv311`) via `../ligocki_runner.py`, with `--recursive --max-loops 1000000 --sim-time 2`.
  - `--sim-time` is a wrapper-side time budget. It starts at the first simulation step, so imports and block finding are excluded, and on expiry the run stops cleanly and still reports its counts.
  - Holdouts are sorted by decimal digits of sigma reached into `top_candidates_bb8.tsv` (all jobs) and `jobs8/<id>/ranking.tsv`.
  - Calibration on BB(7) subtask 243308 (157 holdouts): the known champion ranks #1 with 833 digits; the next best is 220.
  - Rejected settings:
    - a fixed 2000-loop budget took ~36 s per BB(8) holdout, too slow to keep up;
    - 300 or 1000 loops, or dropping `--recursive`, miss the champion;
    - a clock started at process launch killed BB(8) runs before their first step.
  - The score measures growth, not halting.

- **Follow-up.** `followup.py` runs every 30 min (1 worker, Idle priority).
  - Selection: holdouts scoring at least 100 digits, or halting with at least 10 digits, grouped by identical behavior.
  - Each is rerun at 10 and 40 CPU-seconds and classified by digits per simulator loop:
    - flat and small (~0.01) means ordinary exponential;
    - near Quick_Sim's ~3 digits-per-loop cap means doubling-class: the BB(7) champion is here, but so are non-halters (see `investigations/bb7_control_16582.md`), so doubling-class machines need real analysis.
  - Results go to `followup/all.tsv` and `followup/promising.tsv`.
- **Pre-filter.** `prefilter.py --promising` runs 8 deeper configurations of mxdys's verified deciders (NG / RWL_mod / CPS_LRU, exec mode with closure verifier, successes replayed) on undispatched doubling-class machines. It is Idle priority, at most 8 s per attempt.
  - Calibration: it decided 9 of 10 Coq-proven BB(8) non-halters and none of the 4 Coq-proven halters, in 33 CPU-s total.
  - Decided machines are recorded in `prefilter_results.json`. That verification is C++, not Coq. Machines it leaves unresolved go to investigators.
- **Investigations.** Promising machines the pre-filter leaves unresolved go to subagents using `investigation_brief.md`; their reports are in `investigations/`.
- **Ackermann-style (digit-list) scan.** `neighbors/dlscan_all.py` screens every enumerated holdout for machines that behave like the `1RB1RA...` digit-list counter, straight from the enumerator's chunk files (it does not wait for the ranker or the follow-up).
  - `neighbors/dlscan.exe` (`dlscan.cpp`) does the work in C++, about 0.05 s per machine (0.13 s at Idle priority under load):
    - a 5,000,000-step run from the blank tape records every (state, suffix) shape seen at either tape end and samples the tape to infer digit encodings (unit^d with separator);
    - for each shape it probes constructed digit lists for the count-down (R1), reset (R2) and zero-digit refill (R3) rules, stopping at the first failure.
  - `neighbors/dlscan.py` confirms each screen hit with the unchanged `kfit.py` and grades the halting boundary from its safety conditions: SAFE (the parent's non-halting argument applies), CHECK (the rules fit but the argument does not carry over), HALT? (the halting boundary is within reach), NOBOUNDARY.
  - Hits go to `neighbors/dl_hits.tsv`; screen output per chunk is in `jobs8/<id>/dlscan/`. `python neighbors/dlscan_all.py --status` (also the last line of `status.py`) prints the totals.
  - Calibration:
    - all 29 Coq-proven digit-list machines (the parent and its 28 neighbours) are detected, and the tetration-level halters `1RB1RH...` and `1RB1LG...` are not;
    - `neighbors/test_dlscan.py` compared 18,585 C++ probes with the Python `kfam.run_next`: no mismatch;
    - re-scanning the 7,934 machines the old scan had covered took 10 minutes instead of about 20 hours and found 9 digit-list machines where the old scan found 6.
  - The old scan (`stage1.exe`, `scan_ack.py`, `ack_general.py`, about 10 s per machine) is kept for reference. It missed digit lists containing a zero digit (its census required single 0s between runs), and it only looked at the right end of the tape.
  - The maintenance check-in runs `dlscan_all.py` on new chunks.
- **Generalised digit-list scan (BB(7)-champion structure).** `neighbors/dlscan2_all.py` runs `neighbors/dlscan2.exe` (`dlscan2.cpp`) over every chunk; hits go to `neighbors/dl2_hits.tsv`, screen output to `jobs8/<id>/dlscan2/`.
  - Why: the original template cannot describe the BB(7) champion `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF`. Its configurations, checked on literal runs, are `111 (01)^(3 b_k + 1) 1 ... (01)^(3 b_1 + 1) 1 (01)^(3 a) 1010011100 A>`: unit `01`, digits written as 3d+1 repeats, fixed blocks at both ends; it keeps zero digits when it borrows, and it halts when the list is used up.
  - Templates are prefix, unit, separator, digit encoding alpha*d+beta, accumulator encoding and suffix. They are inferred from snapshots kept per kind of end event (state plus the 12 cells next to the head), so a rare family configuration is still sampled. Probes (20,000 steps; hits re-checked at 1,000,000) test count-down, reset and borrow with either refill style, then the empty-list rule.
  - Grades: CHAMPION (R1-R3 fit and the empty list always halts), R4-SOME (halts for some b), then HALT? / CHECK / NOBOUNDARY / SAFE as before.
  - Calibration: the champion is graded CHAMPION with an inferred template; the `1RB1RA` parent and the subtask-240161 machine are found (CHECK); the tetration-level halters `1RB1RH...` and `1RB1LG...` are not. About 0.12 s per raw holdout.
  - It needs lists of at least two digits in the snapshots, so the original scan stays in use for machines like the `1RB1RA` family early in their run.
  - The 396 undecided doubling-class machines (and the 75 of them with 3 or more large counters on Quick_Sim's compressed tape, `neighbors/qs_tape.py`) gave no fit at all.
- **NOBOUNDARY screen.** `neighbors/nob_screen.py` (added 2026-10-04) closes a blind spot of both graders.
  - The graders probe the list-exhausted case only on the empty list (b = 1..5). A real run ends on an all-zero list `K(0^n; 0; b)` with n large, so a machine that halts only for some (n, b) would be graded NOBOUNDARY.
  - The script runs that case over n = 0..6, b = 0..8 (`investigations/rebuilder_nbrs/r4grid.py`) for every NOBOUNDARY row of `dl_hits.tsv`, `dl2_hits.tsv` and the subtree watchers' `watch_hits.tsv`. On a halting cell it traces the blank-tape run to see whether the cell is reached.
  - Results go to `neighbors/nob_screen.tsv` (CLEAN / GRID-HALT [REACHED or unreached] / NO-TEMPLATE).
- **Dispatch queue.** `neighbors/dispatch_queue.py [--top]` ranks every dispatchable machine not in `investigations/dispatched.txt`:
  - RECORD (a champion-structure start longer than 35 digits) > CHAMPION > R4-SOME > GRID-HALT > HALT?/HALT-SOME/CHECK > NOBOUNDARY.
  - The 6-hourly check-in launches the top row (at most one per check-in, at most two investigators running).
  - User decision 2026-10-04: tokens are not a constraint, and missing a record is the cost to avoid, so NOBOUNDARY rows are dispatched too, last.
  - Within NOBOUNDARY, rows whose R1 has a constant slope (`R1 0b+c`) come after the genuine counters (user, 2026-10-05). Two such rows proved not to be digit lists: the 193804 bouncer and the 048631 first-return-map machine.
- **Proofs.** Machine-checked busycoq/Coq 8.20.1 non-halting proofs live in `proofs/` (see `proofs/README.md`). `python proofs/check.py <File.v>` verifies a proof mechanically: it matches the table to the machine, checks the theorem statement, and confirms there are no axioms.

## Running
- Three detached processes, all at Idle priority; each is restartable and continues where it left off.
  - Enumerator: `Start-Process python -ArgumentList 'pipeline.py','--workers','6','--no-rank' -WorkingDirectory <this dir> -WindowStyle Hidden` (pid in `pipeline.pid`).
  - Ranker: `Start-Process ../third_party/venv311/Scripts/python.exe -ArgumentList 'rank_incremental.py','--workers','2' ...` (pid in `ranker.pid`).
  - Chunk runs use 1-hour slices. An unfinished chunk is re-split only when the queue runs low.
  - Follow-up: `third_party/venv311` python `followup.py --workers 1` (pid in `followup.pid`).
  - Worker count: edit `workers.txt` (0 pauses). All processes run at Idle priority and share spare CPU with other idle jobs.
- Progress: `python status.py`, or `jobs8/<id>/progress.log`.
- Stop: kill the python pids in `pipeline.pid`, `ranker.pid` and `followup.pid`, plus any `mxdys_resume8.exe`. Kill the workers too; otherwise orphans hold their work dirs. Unfinished chunks are simply redone.

## Layout
- `jobs8/<id>/`:
  - `seed/`, `chunks/{pending,done}`, `results/` (per-chunk holdouts and stats);
  - `holdouts.txt` and `job.json` once complete;
  - `growth.json` and `ranking.tsv` after ranking.
- `discord_draft.md`: a message to coordinate with the bbchallenge community before publishing.

## Expected cost on this PC
- The first job (076450) measured ~3,300 nodes/s per worker and ~1,000 holdouts/hour on 12 workers.
- By extrapolation, ~500 CPU-hours (~1.5-2 days) and ~80k holdouts per subtask.
- Ranking: ~6-7 s wall per holdout per worker under load, so 4 workers keep up.
