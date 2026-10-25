# Independent audit of C01–C06 follow-up analysis

The parameter portfolio in `candidate_audit.py` completed 108 runs in
237.437 seconds, with two workers. It varied block size (1, 2, 3, 4, 6,
8, 10, 12), backsymbol macros, and recursive proving. It produced no new
halting or nonhalting classification. `candidate_audit.json` retains the
individual outcomes; wall-clock cutoffs are unresolved.

After another worker proved C01, C02 and C04 nonhalting, further direct
work on those candidates was stopped. The prepared exact translated-cycle
script was not executed, because a stronger closure proof already existed.

## Audit of the closure proof mechanism

I independently inspected the verifier, decider, execution dispatch, and
actual instrumented source used for `mxdys_pilot8.exe`:

- `CTL_Fixedlen_verify::Verifier::verify` checks that both tape automata
  accept indefinite zero padding and that the initial finite configuration
  belongs to the proposed invariant.
- It checks every accepted abstract configuration and every possible
  next block represented by the relevant automaton. `WordUpdateLemma`
  directly executes the original transitions within that finite block.
  A possible halt or unresolved block transition rejects verification.
- Every successor must remain inside the accepted configuration set.
  Together with initial membership, this is an inductive nonhalting
  invariant, rather than a finite simulation cutoff.
- A successful `MitM_CTL` decider result passes the verifier assertion
  before returning result 2. The `exec` path starts with
  `CTL_skip_verify = false`; the flag is enabled only in the separate
  enumeration path.
- The instrumented source explicitly redefines `assert` to an active
  failure check, independently of `NDEBUG`. Verification failure exits
  with a nonzero return code. The runner checks that return code.
- Textual comparison confirmed that both the verifier body and the
  decider region are identical in `mxdys_main.cpp` and
  `mxdys_pilot.cpp`.
- The C01/C04 replay input files match their corresponding `N` log entries.
  C02 uses the RWL-modulo abstraction but passes the same final verifier.
  Replacing the candidate's explicit halting transition by `---` does not
  alter any trajectory before that transition is reached; proving that
  it is never reached applies to the completed candidate as well.

This substantiates the other worker's C01/C02/C04 classifications. It is
an independent source audit of the closure argument, not a separate
formal verification of the entire C++ implementation. It does not rely
on the program's hash-based translated-cycle detector.

## Backtracking on C03, C05 and C06

`candidate_backtrack.py` used the upstream backward reachability filter
with a requested depth of 500 and a frontier limit of 20,000. All three
reached the frontier cutoff without proving halting or nonhalting:

| Candidate | Reached depth | Frontier size | Explored nodes |
|---|---:|---:|---:|
| C03 | 61 | 24,898 | 71,721 |
| C05 | 23 | 29,921 | 56,584 |
| C06 | 23 | 22,471 | 42,004 |

These results are in `candidate_backtrack.json`. C03, C05 and C06 remain
unresolved by this audit's methods. No new champion or halter is claimed.
