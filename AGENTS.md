# AGENTS.md: guide for AI agents

You are probably here to find or prove new Busy Beaver machines. This repository is the lab notebook of a search that
produced the current entries in [jeff87654/busy-beaver](https://github.com/jeff87654/busy-beaver). Use it to avoid
repeating closed searches, to reuse tools, and to copy the methods that worked.

## Read in this order

1. [`STATUS.md`](STATUS.md): what is proved, what is closed, which claims are wrong, and what is still open.
2. [`METHODS.md`](METHODS.md): how the records were actually found, and the failure modes to guard against.
3. [`lessons/README.md`](lessons/README.md): 57 short lessons. Read `screening-lessons.md` before you build any screen.
4. [`INDEX.md`](INDEX.md): find the reports for the machine class or idea you are working on.

## Trust rules

- **Only the main repository is verified.** A note that says "proved", "theorem", "Q.E.D." or "record" is a claim
  until it matches a Coq file there with `Print Assumptions` closed. Check `claims_status` in `index.jsonl` first.
- **Simulation is not proof.** Many reports, especially by the Gemini agent Argon, call rule fits or simulations
  "proofs" or "theorems". Several of those were wrong (see STATUS.md, "Claims that turned out wrong").
- **Notes go stale.** The bar a record had to beat changed about ten times in a month. Old notes describe old bars
  as current. Today's bars are the main repository's README tables.
- **Wrong in both directions.** Leads dismissed as hopeless ("Collatz-hard", "never halts") later became records
  (C04, M8, h003, champ_231). A dismissal deserves the same suspicion as a claim.

## Searching this repository

```bash
# notes about a topic, most useful first
grep -i '"topic": "bb9"' index.jsonl | grep '"value": "high"'
# everything mentioning a machine (strings use the standard bbchallenge format, e.g. 1RB0RA_1LC1LF_...)
grep -rl "1RB0RA_1LC1LF" workspace lessons
# open leads
less workspace/bb8_list/investigations/OPEN_CANDIDATES.txt
```

`index.jsonl` fields: `path`, `title`, `summary`, `topic` (bb5-6, bb7, bb8, bb9, bb10, bb11-14, bb17-18, bb43,
zf-consistency, pa-goldbach, search-method, infrastructure, other), `kind`, `claims_status` (verified, refuted,
superseded, open, negative-result, mixed, n/a), `status_note`, `value` (high, medium, low).

## Conventions

- Machine strings: bbchallenge standard format, states `A..`, `---` = undefined (halting) transition; `1RZ` or
  `1RH` written in some notes = a defined halting transition.
- σ (score) = ones on the tape when the machine halts. Whether the halting write counts differs between notes; the main
  repository's README states the convention for each entry.
- Fast-growing hierarchy: f_0(n) = n + 1, f_(k+1)(n) = f_k^n(n), f_ω(n) = f_n(n), f_(ω+1)(n) = f_ω^n(n),
  f_(ω+2)(n) = f_(ω+1)^n(n). "f_w" in ASCII notes means f_ω.
- Proofs use [busycoq](https://github.com/meithecatte/busycoq) at commit `bd2e36f` with Coq 8.20.1.
  `workspace/bb8_list/proofs/check.py` is the acceptance checker that the agents had to pass.
- Paths in notes are absolute Windows paths: `C:\Users\jeffr\Downloads\bb8\X` is `workspace/X` here.
- Short names (M8, C04, C7, h003, n1, T12a, champ35, champ_231, fw2, M13, M14) are project labels; STATUS.md maps them
  to machine strings.

## Key tools (all under `workspace/`)

| tool | what it does |
|---|---|
| `bb8_list/pipeline.py`, `bb8_list/README.md` | holdout enumeration pipeline (enumerate, pre-filter, rank, follow up) |
| `bb8_list/neighbors/dlscan.cpp`, `dlscan2.cpp`, `dlscan_all.py`, `dlscan2_all.py` | digit-list (counter / Ackermann) structure detectors over holdout chunks; dlscan2 has the CHAMPION grade (halts when its list runs out) |
| `bb8_list/investigations/nested_detector/dlscan3.cpp` | nested-counter detector (BB(8) and 10-state scans) |
| `bb8_list/neighbors/dlnbr.cpp` | radius-k neighbourhood enumeration around a parent machine |
| `bb8_list/neighbors/nob_screen.py`, `dispatch_queue.py` | grids the list-exhausted case; ranks rows for investigator dispatch |
| `bb7_holdouts/reb7/reb7.py`, `bb7_holdouts/rank/rank7.py` | BB(7) holdout rebuilder classifier; ranks hits by estimated size |
| `bb8_list/autoproof/` | automatic busycoq non-halting proofs for a digit-list class (engine.py, coqgen.py) |
| `bb8_list/investigations/bb8_m7_0RB0LC_ctl/gen_ngcps_v.py` | NGramCPS certificate search with a verified checker; long asymmetric windows |
| `bb8_list/investigations/bb10_n1_coq/mexp.py` | symbolic "spec" workflow used for the f_(ω+1) Coq proofs |
| `bb8_list/proofs/selfcontained/gen_selfcontained.py` | merges a multi-file busycoq proof into one file |
| `bb8_list/investigations/bb8_resid/tools/collapse.py` | collapse detector (a record with n states that is really n−1) |
| `bb8_list/investigations/halt_redirect/` | halt-redirect enumeration (the route to the BB(9) records) |

Many tools have known limits recorded in the lessons. For example, `ngann.exe` (built from `ngann.cpp`) is unsound
for 9 or more states, so use `bb9_parked/src/ngann9.cpp`. Before trusting a tool, grep `lessons/` for its name.

## If you find something

Check it the way the project checked its own finds before believing it: simulate the real orbit from the blank tape,
look for a parity or residue invariant that blocks the halt, have a second agent re-derive it independently, then
prove it in Coq. METHODS.md describes how.
