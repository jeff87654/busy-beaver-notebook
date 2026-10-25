# BB(8) hunt — session artifacts (2026-06-11)

Attempt to find a new 8-state, 2-symbol busy beaver champion.

September follow-up: see `hunt_20260926.md` and `discovery_20260926.md`.
Feasibility estimates and the current plan: `plan_20260926.md` (data in `estimate_20260926/`).
The current BB(7) champion was discovered by enumeration, then analyzed.
The new search direction uses the original enumeration/decider pipeline.
The follow-up on the 16 survivors is in `candidate_analysis.md`;
`candidate_remaining.txt` contains the current unresolved subset.

## The bar

As of this session, [BB(8)](https://wiki.bbchallenge.org/wiki/BB(8)) is
"unsolved and largely unexplored"; its listed champion is just the BB(7)
champion by default:

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF   (Kropitz, May 2025)

which runs more than 2↑¹¹2↑¹¹3 steps (eleven Knuth up-arrows).

## Artifacts

- `sim.py` — exact RLE/chain-step accelerated simulator. Validated: exactly
  reproduces BB(2)=6, BB(3)=21, BB(4)=107, BB(5)=47,176,870.
- `macro.py` — Marxen-style k-cell block macro simulator with memoized block
  transitions and chain steps; independent cross-check of `sim.py`.
- `search.py`, `search2.py` — parallel hill-climbing search over 8-state
  tables, seeded partly with known champions embedded in 8-state tables.
- `extend.py` — the halt-extension construction (below), validated on the
  BB(4) and BB(5) champions.

## Best *verified* halter found by search

    1RB1LC_1RC1RB_1RD0LE_1LA1LD_1LH0LA_1RH1RZ_0RB1RF_1RG0LG

Halts after exactly **131,112,087 steps** leaving **20,481 ones** —
verified independently by `sim.py` and by `macro.py` at block sizes 2, 3,
and 4. Found by two rounds of elite-seeded hill climbing (648,915 machines
simulated total, ~397k of them halters). It is a BB(5)-champion core with
the three extra states evolved into a re-entrant postlude (~2.8x the BB(5)
step count). Full leaderboards in `run1_merged.json` / `run2_merged.json`.

The six unique candidates listed as unresolved in `run2_merged.json`
are now **proved nonhalting**. They all execute the same expanding sweep:
at step `4n² + 2n`, the machine is in state A at position `-2n`, with
exactly `4n` consecutive ones on `[-2n+1, 2n]`. Each cycle adds four
ones and repeats this configuration form. See `audit_notes.md` for the
inductive proof and `audit_unresolved.py` for the recognizer.

An independent literal simulator (`audit_verify.js`), using no chain or
macro acceleration, also confirms the existing local winner's exact
131,112,087 steps and 20,481 ones. Results are in
`audit_verification.json`.

## Constructive 8-state machine beating the listed BB(8) bound

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RH0LC_1RG1LD_0RG0RF_1RZ1LH

This is the BB(7) champion with its halt transition (E0) redirected to a new
state H that sweeps left over 1s (1 → 1LH) and halts on the first 0
(0 → 1RZ). Proof sketch:

1. The table differs from the BB(7) champion only at E0, so the trajectories
   are identical until E0 first fires — which is the champion's halt step.
   Hence this machine takes > 2↑¹¹2↑¹¹3 steps before entering H.
2. From any configuration, H halts: while reading 1s the head moves strictly
   left, and only finitely many tape cells are non-blank, so H reaches a 0
   and halts. Total steps ≥ champion's steps + 1; ones = champion's + 1.

**Caveat:** this is the classic "trivial extension" (the standard argument
that BB(n+1) > BB(n)). It strictly beats the machine listed on the BB(8)
page, but the busy beaver community would not regard it as a genuine new
champion. A substantive new record needs a halting argument and a runtime
comparison that beats the existing machine. It can be discovered by search:
the current BB(7) champion was found in subtask 243308 of mxdys's enumeration
and analyzed afterwards. There is no basis for requiring hand design or
predicting that analysis must take months.
