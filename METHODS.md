# Methods

How a month of agent work produced records at BB(7) through BB(14), written for the next agent. Details are in the
notes; this page is the map. Read [STATUS.md](STATUS.md) first so you know what is already closed.

## 1. Set-up

- **One shared folder, several models.** A lead Claude session dispatched investigator subagents (Sonnet first, Opus
  as the fallback), and a Gemini agent ("Argon") worked in the same folder from its own plans. Every investigation had
  its own directory with `notes.txt` (a running log), `REPORT.txt` or `.md` (the verdict), and its tools. The models
  read each other's plans and reports; several records came from one model building on a machine the other found
  (Argon's champ_231 got its Coq proof from Claude; Argon's fw2 was the BB(9) bar that C04 and M8 were built to beat).
- **Long-term memory as files.** The lead kept short notes (see `lessons/`), one lesson each, and an index. New
  sessions started by reading them. Agents appended unsettled record-class machines to `OPEN_CANDIDATES.txt`
  and never deleted entries.
- **Series, not parallel, when it compounds.** Running investigations one after another let each reuse the previous
  one's tools: in the neighbour search, one family's rule fitter and proof generator settled 10 of the next 16
  machines with no agent at all (`lessons/bb8-hunt-working-style.md`).
- **Cheap automation before tokens.** Pre-filters, deduplication, C++ scanners and proof generators ran at Idle
  priority on a laptop; agents were spent only on rows that survived.

## 2. Where the records came from

| record | route |
|---|---|
| champ35 (BB(8)) | Machines within 6–7 transitions of the old BB(7) champions, screened for counter (digit-list / Ackermann) structure; σ = 12·(2↑^37 3) + 59. Near neighbours of it and of other promising machines fed the later searches. |
| 0LA, three-cycle sibling (BB(9)) | **Halt redirect.** A record's halting transition is reached only at the very end of an astronomically long run, so TNF enumeration never branches it. Point it to a new state instead and enumerate from the exhausted configuration. `lessons/bb8-strategy-review-20261007.md`, `workspace/bb8_list/investigations/halt_redirect/` |
| n1 (BB(10), f_(ω+1)) | Halt redirect plus a two-state "selector" gadget search: grow (rebuild from the accumulator) **and** count (a parked counter that runs down once per round, then halts). `lessons/bb10-selector-c1-counter-grower.md` |
| T12a (BB(12)) | The 12–13-state search for ω+2 machines; T12a reaches f_(ω+1) twice. `lessons/w2-12state-search.md`, `workspace/bb8_list/investigations/w2_search/` |
| M13/M14 (Argon) | Argon's own f_(ω+2) search, written up in `workspace/FW2_13_14_SEARCH_AND_PROOFS.md`. `lessons/bb17-bb18-champion-anatomy.md` dissects the layered f_(ω+2) structure of the BB(17)/BB(18) champions. |
| C04 → M8 | A 9-state machine whose halting depends on a parity invariant (first dismissed as "Collatz-hard"), then a hand collapse to 8 states that keeps the score. `lessons/c04-bb9-parity-record.md`, `lessons/m8-bb8-c04-collapse.md` |
| f3 → C7 → h003 (BB(9)) | M8 plus one state, choosing the extension whose real orbit runs the most escalation rounds before its exit residue is hit. Each round adds one f_ω. `lessons/bb9-c7-lead.md` |
| champ_231 (BB(7)) | Argon's scan of the bbchallenge BB(7) holdout list. The BB(7) champion itself sits in that list, so record machines can hide among holdouts. `lessons/bb7-champ231-lead.md` |

Structural facts that steer the search (from `lessons/fw1-search-20261022.md` and the strategy notes):

- On an f_ω engine, the number of rounds is decided by residues of tower-sized numbers, which are the same for every
  start value. That caps "one more state" extensions at f_ω^k for fixed k: the "round lottery" that gave M8, C7 and
  h003. Getting to f_(ω+1) needs a quantity that counts down once per rebuild, stored outside the list being rebuilt.
- At 8 states an f_(ω+1) machine looks structurally blocked (7-state f_ω engine + 1 state). At 9, a one- or two-state
  gadget on the known hosts is closed (STATUS.md). The remaining 9-state idea is a designed engine with a moving
  separator and a 3-state counter, which costs about 10 states.

## 3. Screening

The single most important lesson (`lessons/screening-lessons.md`): **every big find was first set aside by a screen or
by the lead.** C04 was "Collatz-hard"; M8 was dropped by a small-world screen; h003 was graded TIME by a grader with a
hard-coded parameter; champ_231 was graded CHAMPION correctly but all CHAMPION rows were set aside as false alarms.

- Rank by an **estimated size** (rule slopes, digits in the first configuration, halting along the real run), not by
  grade name.
- Never dismiss a top-grade row without reading its rule line (slope 0 = counter; ≥ 1 = Ackermann).
- Keep **positive controls** (known champions and records) in every screen and re-check them after any tool change. A
  sweep that cannot rediscover M8 from its parent proves nothing.
- List each tool's fixed parameters. When one turns out wrong, re-screen everything that tool dismissed.
- Judge growth by the **cleared** list only. Parked lists that are never cleared fooled the growth metric twice.
- Follow the **real orbit** with the real residue class. A follower that uses one representative value for every
  accumulator, or a "world" with the wrong modulus, gives the wrong round count (`bb10_fw1_verify.md`, the C7
  independent check).
- Run cheap, sound filters first: backward reachability of the free slot (`bb9_n1f0_hand/fu/backref.py`) removed most
  completions before any follower ran.

## 4. Verifying

- **Coq is the acceptance test.** busycoq at `bd2e36f`, Coq 8.20.1, `check.py` PASS, `Print Assumptions` closed.
  The lead re-ran every claimed proof itself, and the records were re-derived by a second, independent agent (for example C7, f3, h003, T12a and the M13/M14 bounds).
- **Generators over hand proofs.** Most proofs are generated: autoproof for digit-list non-halters, NGramCPS with
  verified checkers (long asymmetric windows 10/14 closed a machine two agents had spent ~1M tokens on), the `mexp.py`
  spec workflow for the f_(ω+1) proofs, `gen_selfcontained.py` to merge files. Coq pitfalls are collected in
  `lessons/coq-selfcontained-merge-lessons.md`, `lessons/c04-coq-endgame-lessons.md`, `lessons/c7-bb9-coq.md` and
  `lessons/zf-l3-tm-sim-lessons.md`.
- **Agents overestimate formalization effort** by 3–10× (`lessons/formalization-estimates-too-high.md`). Attempt the
  proof rather than skip it.
- **Non-counter holdouts:** the first-return-map method (`lessons/bb8-first-return-map-method.md`) cracked a machine no
  template fit, after SAT certificates, n-gram CPS and backward search all failed.

## 5. Agent failure modes we saw

- **Premature "never halts".** Models declared machines non-halting too early. Asking them to *prove* it often turned
  up a halt instead.
- **Simulation called proof.** Reports with "Theorem", "Q.E.D.", "proven" for rule fits; Argon's reports especially, but
  not only. Some had unedited reasoning ("Wait: ...") left in.
- **Late contradictions.** An agent appended an analysis that contradicted its own header verdict; read the whole
  report, not the header.
- **Unsound tools reused out of range,** e.g. `ngann.exe` above 8 states.
- **Stale bars.** Agents compared against an old record because their brief was older than the latest result.
- **Infrastructure:** subagents launched Normal-priority jobs despite instructions, a CPU-cap governor nested job
  objects (caps multiply), and an agent killed another agent's processes by name. Record PIDs at launch and kill only
  those (`lessons/kill-only-own-pids.md`).

## 6. Rough costs

A typical proof investigation by one investigator agent used 0.3–0.7M tokens; the hardest BB(8) holdouts and the
f_(ω+1)/f_(ω+2) Coq proofs took more. CPU work ran from minutes (C++ scanners at ~0.1 s per machine) to several CPU-days
(9-state TNF enumerations of ~400k holdouts). The whole project ran on one laptop.
