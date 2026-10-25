# Investigation of the 16 remaining BB(8) candidates

Current result: **12 nonhalting, 4 unresolved, no new halter.**
Candidate IDs refer to the original line numbers in `discovery_holdouts.txt`,
which is preserved. The reduced list is `candidate_remaining.txt`; full
machine strings, origins, and evidence are in `candidate_analysis.json`.

## Per-candidate outcome

| Candidate | Outcome | Original shard / line |
| --- | --- | --- |
| C01 | nonhalting | pilot8_243308 / 3 |
| C02 | nonhalting | pilot8_243308 / 2 |
| C03 | nonhalting | pilot8_202609 / 2 |
| C04 | nonhalting | pilot8_202609 / 1 |
| C05 | nonhalting | pilot8_202609 / 4 |
| C06 | nonhalting | pilot8_202609 / 3 |
| C07 | nonhalting | pilot8_202609 / 6 |
| C08 | nonhalting | pilot8_202609 / 7 |
| C09 | nonhalting | pilot8_202609 / 8 |
| C10 | nonhalting | pilot8_202609 / 9 |
| C11 | nonhalting | pilot8_202609 / 10 |
| C12 | nonhalting | pilot8_202609 / 11 |
| C13 | unresolved | pilot8_202609 / 12 |
| C14 | unresolved | pilot8_202609 / 13 |
| C15 | unresolved | pilot8_202609 / 14 |
| C16 | unresolved | pilot8_202609 / 15 |

## What establishes nonhalting

Eight candidates (C01, C02, C04, C07, C08, C09, C11, C12) were settled by
the mxdys deciders. C03, C05, C06 and C10 were settled separately by proofs below.
The mxdys deciders construct finite automata describing an infinite language
of tape configurations. In `exec` mode the closure verifier is enabled.
It checks membership of the initial configuration, then re-simulates exact
base transitions for all accepted abstract contexts and requires every
successor to remain accepted, without reaching halt. Each positive result
was replayed in a fresh process. Diagnostics retain DFA sizes and the number
of accepted abstract tuples; these are not counts of concrete tapes.

The commands, machine inputs, binary/source hashes, return codes, verifier
output and replays are retained in `candidate_deciders.json` and
`candidate_deciders_runs/`. Complete automaton certificates are not exported;
the saved commands regenerate and verify the invariants. This is a
machine-checked inductive argument, not a formalization in a proof assistant.

The deeper native-decider build expands word capacity from 128 to 256 bits
so longer history encodings fit. The search and closure-verification logic
are unchanged; this capacity change was independently inspected. The
initial and deeper results remain in separate bundles, including hashes.

## An explicit proof for C07 and C08

Both machines reach a configuration with a left block of nine ones, state H
on a separating zero, and no right-hand ones. Let H(n,k) mean a left block
of n ones, the H head on a zero, and a right block of k ones. For all
n >= 5 with n = 1 modulo 4, and k >= 0:

    H(n,k) -> H(2*n-1,k+1).

No H state occurs between these endpoints. The sole halt transition is H1,
but every H endpoint reads zero. The left lengths are therefore
9, 17, 33, 65, ... forever. Huge simulated counts do not make these halters.

`candidate_theory_proof.md` derives the universal recurrence using sweep
identities. `candidate_theory_certificate.py/.json` records the fixed local
identity and 978 exact finite checks. The checks support the symbolic
argument; finite examples alone are not its proof. The automaton decider
independently reaches the same nonhalting conclusion for both machines.

## A separate symbolic proof for C10

C10 reaches a configuration C(2,1) after 71 ordinary transitions, where
C(a,b) has tape word `1111 (01)^a 0 1^b 01` and H on the blank just to
its right. Universal tape-sweep identities reduce its evolution to an
integer recurrence. Set `S_j = 6*2^j-j-6`. If `S_j < a < S_(j+1)`,
the machine returns from C(a,1) to C(a',1), with

    a' = 24*2^j-9-j-a,
    S_(j+1) < a' < S_(j+2).

Since `S_0 < 2 < S_1`, every return stays strictly between consecutive
halting boundaries. Every constituent sweep is finite and avoids halt,
so the machine runs forever. The successive outer parameters are
2, 13, 25, 60, 120, 251, 503, 1018, ... .

`candidate_audit_c10.md` proves the C-configuration sweep rules, including
the boundary cases. `candidate_theory_c10.md` supplies the return sweeps
and arithmetic induction. Both derivations were independently reviewed.
`candidate_theory_c10_certificate.py/.json` adds 667 exact finite checks
for transcription errors; these checks are not substitutes for the
universal lemmas. The native C10 decider attempts remain inconclusive.

## Follow-up on the eight survivors: C05, C06 and C09 settled

C09 passed the previously untried ExRWL abstraction and a fresh-process
replay. Its checked invariant has 116 left automaton states, 5,940 right
automaton states and 42,099 accepted abstract contexts. Every checked
block update takes at most four ordinary transitions. The exact command,
source hashes and logs are in `unresolved_native_portfolio.json` and
`unresolved_native_runs/c09_p09*`; independent source/artifact review and
local tape identities are in `unresolved_c09_review.md`.

C05 and C06 eventually repeat a fixed computation farther left, leaving
one additional one behind every period:

| Machine | Verified seed step | Period in steps | Head displacement | Ones at seed |
| --- | ---: | ---: | ---: | ---: |
| C05 | 30,517 | 30,494 | -324 | 4 |
| C06 | 12,631 | 12,611 | -205 | 3 |

A compact proof uses state A on a blank immediately left of `11100000`
for C05, or `110000000` for C06. Everything farther left is blank; the
right suffix is arbitrary. The exact finite computation never reads that
suffix and recreates the same prefix farther left. Induction therefore
applies forever, regardless of the growing right-hand tape.

`unresolved_early_proofs.md` supplies both the universal sweep derivation
and this simpler locality proof. Independent Python and JavaScript
checkers reject any read of an unknown suffix cell and verify the exact
blank seeds and final prefixes. Their results are in
`unresolved_early_locality_minimal.json` and
`unresolved_early_locality_js.json`. These are finite certificates of a
universal transition identity, not conclusions from simulation cutoffs.

## Further follow-up: C03 settled

C03 reaches an exact recurring suffix after 83,806 steps. Each period takes
23,636 transitions, shifts the head and entire active suffix 32 cells to
the right, and leaves a fixed 32-cell block containing 16 ones behind.
The computation never reads the discarded left context. This gives an
inductive proof of nonhalting for an arbitrary left-hand tape.

`unresolved_c03_cycle_proof.md` documents the recurrence. Two independent
literal implementations checked the complete suffix, exact blank seed,
read bounds, state and head displacement. Their results are retained in
`unresolved_c03_cycle_certificate.json` and
`lastfive_decider_c03_independent.json`. The earlier unproved rollback
guard is no longer needed for the classification.

## What remains

C13, C14, C15 and C16 remain unresolved. However, C13 and C14 have
identical computations after collapsing one three-step path to one step;
C15 and C16 have the same correspondence. Each pair must have the same
halting outcome. Thus the four unresolved machines can be studied through two
representatives: C13 and C15. The elementary transition-table proof is
in `unresolved_family_equivalence.md`.

The new native searches made 202 parameter attempts (plus one successful
replay); C09 was the only positive result. An independent Ligocki CTL1-4
portfolio made 128 tests across all offsets of block sizes 1, 2, 3, 4 and
6 for C13/C15; all were inconclusive. Two-million-step literal profiles
of C13-C16 motivated the pair equivalences but did not decide halting.

The follow-up on the last five additionally tested 108 window/history
abstractions and 252 modular stack abstractions on C13/C15; none settled
these representatives. Exact symbolic-tail calculations established seven
universal C14 boundary maps, but no closed recurrence. The new evidence,
rejected conjectures, and limits are collected in
[lastfive_progress.md](lastfive_progress.md).

## Earlier work on unresolved candidates

All sixteen received nonhalting-decider attempts. C01-C06 additionally had a
108-run macro-simulator portfolio. C09-C16 had an 80-run portfolio varying
block sizes 1,2,3,4,6,8,10,12 and backsymbol choices. No additional halter or
nonhalting result came from those simulator portfolios. Timeout/loop cutoffs
remain unresolved. Backward reachability checks were also attempted; a
branch-width cutoff is not evidence that halting is impossible.

The initial native portfolios made 190 parameter attempts, including the separate
C10-targeted pass (`candidate_deciders_targeted.json`). These attempts are
not a count of different machines.

Evidence files include `candidate_audit.json`, `candidate_portfolio.json`,
`candidate_backtrack.json`, and `candidate_backtracking.json`. 

The remaining candidates should not be called champions, nonhalters, or
known open mathematical problems on the basis of these finite runs.
