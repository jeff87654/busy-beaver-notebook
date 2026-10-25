# Follow-up on the last five BB(8) candidates

Current outcome: **C03 proved nonhalting; C13-C16 remain unresolved.**
Across the original sixteen, twelve are now nonhalting and four are unresolved.
The four survivors form the established equivalent pairs C13/C14 and C15/C16.
No new blank-tape halter was found.

## C03: an exact recurring suffix

At step 83,806, C03 reaches state F with a head at -50. Its complete tape
suffix beginning at -54 repeats after 23,636 transitions, translated 32
cells to the right. The period reads only cells [-51,159]; it never reads
the arbitrary left context. It emits a fixed 32-cell block with sixteen
ones. This is a universal partial-configuration recurrence, giving
nonhalting by induction. The earlier unproved rollback guard is not needed.

Two independent literal implementations verified the seed, full suffix,
state, head shift, and read boundary. See `unresolved_c03_cycle_proof.md`,
`unresolved_c03_cycle_certificate.json`, and
`lastfive_decider_c03_independent.json`.

## New tests on the two remaining representative cases

Standalone CPS searches tried 108 new window/history combinations on C13
and C15. Seventy-six admitted an abstract halting configuration and thirty-two
hit an external time limit. All outcomes are inconclusive; an abstract
halting configuration need not be reachable by the real machine. Exact
settings, a corrected local history abstraction, and independent certificate
calibration are documented in `lastfive_decider_notes.md` and the two
`lastfive_decider_cps*.json` portfolio files. The upstream files are preserved.

An exact one-sided recurrence search checked C14 and C16 for ten million
ordinary transitions each at E0 checkpoints, using contexts up to 1,024
cells. Neither yielded a recurrence witness. Results and code are in
`lastfive_cycle_search.json/.py`. These finite limits do not classify them.

A new modular stack abstraction retains the full stack's binary residue
alongside its exact near-head suffix. The 252 attempts covered six moduli,
suffix lengths two through eight, and block sizes one through three, on
C13/C15. All were inconclusive; there were no errors or external timeouts.
The existing closure verifier is byte-identical to the base version.
Actual encoding checks and simple loop/halter controls passed. Source,
binary hashes, commands and logs are recorded in
`lastfive_modular_summary.md/.json` and `lastfive_modular_*results.json`.

## Exact reduced models and rejected conjectures

C16 has been reduced to fifteen rules on states A, E and H, with direct
transition derivations and 6,144 finite local cross-checks. Its left carry
rewrites either `111` or `010` to `011` while moving E three cells left.
The dangerous pattern is `110` with E scanning the final zero. See
`lastfive_family_map_reducer.py/.json`.

C14 has related exact sweep and carry identities, but differs on the
`010` carry. Therefore the two representative cases cannot be identified
merely because their early blank-tape traces look alike. The C14 derivations
and checks are in `lastfive_family_theory_macros.md/.py/.json`.

Counterexamples rejected several proposed invariant languages. These start
from **artificial nonblank tapes**, not the Busy Beaver blank start. With
A on the blank left of runs of ones separated by single zeros:

- Runs [4,2,4,1] halt after 1,058 steps in C16 and 1,086 in C14.
- Runs [3,2,3,4,1] halt after 10,910 steps in C16. Thus even a unique
  four-one run with a leading three-one run is insufficient for safety.

The falsification data are in `lastfive_grammar_*.json`. No such input is
claimed to occur in the blank-tape computation.

The exact C16 reduced interpreter also followed the blank trajectory to
27,632,517 ordinary transitions without reaching an E0 with a one on its
left. Its checkpoint is saved in `lastfive_c16_guard_search.json`. This is
an observation and restart point, not a proof of a permanent guard.

## Symbolic terminal-tail acceleration

A useful universal rule avoids simulating an arbitrarily long terminal
tail. If H scans the first cell of `(011)^k 01`, the cell immediately left
is zero, and all cells right of the tail are blank, it returns A two cells
left of the initial head. It writes three ones around the old tail start
and shifts the same terminal tail two cells right. The computation takes
`18+12k` steps for C14 or `16+12k` for C16, for every integer k >= 0.

The right scan costs 5k+4 steps, the right-end reset costs seven or five,
and k+1 local left carries cost seven steps each. The arbitrary earlier
left context is never read. This supplies a sound symbolic acceleration,
rather than a runtime formula fitted to samples. More complicated mixed-run
prefixes still need an invariant or a recurring symbolic configuration.

The symbolic engine completed seven universal C14 boundary maps, each
valid for every nonnegative terminal-tail parameter. Starting from the
verified blank seed at step 17, they reach a boundary at exact step 429,755
with tail parameter 181. The eighth map exceeded a 50-second bound; no
prefix repeat or nonhalting conclusion was obtained. The original partial
run retained counters but not a resumable tape checkpoint. The saved
standalone engine now includes checkpoints for future bounded runs.

The universal tail lemma, exact finite prefixes and affine time formulas
are documented in `lastfive_family_theory_symbolic.md`, implemented in
`lastfive_family_theory_symbolic.js`, and preserved in the accompanying
JSON. These maps provide exact progress toward a possible invariant;
seven completed maps alone do not establish endless continuation.
