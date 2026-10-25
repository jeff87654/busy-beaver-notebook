# Audit of the existing BB(8) search

## Independent verification

The existing local winner

`1RB1LC_1RC1RB_1RD0LE_1LA1LD_1LH0LA_1RH1RZ_0RB1RF_1RG0LG`

halts after exactly **131,112,087 steps** with **20,481 ones**. A literal
one-transition-at-a-time JavaScript simulator, independent of both Python
accelerators, reproduced these values in 4.013 seconds. It visited tape
positions -20,432 through 49. See `audit_verify.js` and
`audit_verification.json`.

## All six saved unresolved machines provably diverge

Every unique unresolved table in `run2_merged.json` has these reachable rules,
where X is C or H:

| State / symbol | Transition |
|---|---|
| A / 0 | 1RB |
| B / 0 | 1RX |
| B / 1 | 1RB |
| X / 0 | 1LD |
| D / 0 | 1LA |
| D / 1 | 1LD |

At time `t(n) = 4n² + 2n`, the machine is in A at position `-2n`,
and the tape consists of `4n` consecutive ones occupying
`[-2n+1, 2n]`, with zeros everywhere else. This includes the blank initial
configuration for n = 0.

Starting at this configuration, A writes a one, B crosses the `4n` existing
ones, B and X write two new ones on the right, D crosses the `4n+2` ones
to its left, and D writes one new one before returning to A two cells
left of its previous position. This takes `1 + 4n + 1 + 1 + (4n+2) + 1
= 8n+6` steps. The result is exactly the configuration for n+1, proving
the invariant by induction and proving nonhalting. No other transitions
are ever read. This is an expanding sweep, not a translated fixed-width
cycle. `audit_unresolved.py` recognizes the family, checks its first ten
cycles independently, and records all six classifications.

## Search weaknesses and small bugs

- The hill climbers accept only strictly better halters. Changes to
  unreachable states cannot accumulate, even though those states often
  need multiple coordinated edits to become useful. Neutral drift,
  occasional multi-entry mutations, and a deduplicated population would
  substantially broaden exploration.
- Unresolved candidates are ranked by simulated step count alone. A
  simple expanding sweep dominates this ranking. Rule-based divergence
  detection and topology/diversity filtering would recover substantial
  compute and prevent repeated copies of one family filling the queue.
- `seeded_table(rng)` calls global `random.choice(SEEDS)` instead of
  `rng.choice(SEEDS)`, so its documented worker seeds do not fully determine
  the sampled machines.
- The initial README describes four unresolved machines beyond 10^12,
  whereas the saved merged data has six unique unresolved machines at
  111,111,888,889 steps. Classification is now proved above.
- `sim.py`'s prose says `---` means halt, but parsing it yields an
  undefined transition and simulation returns `undef`, without a halt
  step. The search never generates `---`, so this does not invalidate its
  recorded halters, but the documentation should distinguish it from Z.

No unsound transition or chain-acceleration rule was found in the existing
RLE or block macro simulators during this read-through. This is a code
audit and independent verification of one result, not an exhaustive proof
of the simulators.
