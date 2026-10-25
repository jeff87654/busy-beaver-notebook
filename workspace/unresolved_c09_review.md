# C09: nonhalting closure corroborated; local word dynamics

C09 is nonhalting. The decisive result is a finite-language closure found by
mxdys's ExRWL search and checked using the separate generic CTL verifier. This
review checks the saved successful run and fresh-process replay, the exact
candidate correspondence, and the source path that verifies the closure.
The local word lemmas below explain some dynamics but are not a replacement
for the complete finite-language proof.

Machine, line 9 of `discovery_holdouts.txt`:

```
1RB1LA_0LA0RC_1RA1LD_0LE1RZ_1LC1LF_0RG0LE_1RH0RG_1RA0RF
```

## Independent proof-artifact review

Both `unresolved_native_runs/c09_p09` and `c09_p09_replay` use exactly this
machine, replacing only the halting transition D1=`1RZ` by upstream's `---`
notation. The write and move on this transition cannot affect nonhalting:
the proof excludes reaching it altogether. The command in each input is:

```
MitM_CTL ExRWL sim 1001 maxT 300000 H 12 tH 1 bsz 8 n 2 run
```

Both records have successful exit code, the machine followed by `N` in the
log, and the same actual verifier diagnostic:

```
verified: lset:116 lset_tr:118 rset:5940 rset_tr:6266 accept_set:42099 block_maxT:4
```

The invariant has 116 left-side automaton states and 118 transitions, 5,940
right-side states and 6,266 transitions, and 42,099 accepted tuples combining
left state, right state, machine state, and head direction. Every elementary
two-cell block update checked by this invariant takes at most four literal
Turing-machine steps.

In `candidate_deciders_deep_verified.cpp`, ExRWL's parameterized word summary
is used by the search only. Once a fixed point is found, line 1095 passes the
left and right push maps and the accepted tuples to
`CTL_Fixedlen_verify::Verifier`. The verifier at lines 657–702 independently:

1. Checks that blank blocks extend each blank-tail state to itself.
2. Reconstructs the exact post-1001-step seed in both automata and checks that
   its tuple belongs to the accepted set.
3. For every accepted tuple and every available incoming block transition,
   calls `WordUpdateLemma::from` to execute the real machine on that block.
4. Rejects a halt or failed block computation, and checks that each resulting
   tuple is again accepted.

This is an inductive invariant: the seed is represented; every actual next
block computation stays represented; and none can halt. The infinite zero
padding is covered by the blank-state loops. The validity of the resulting
closure does not rely on ExRWL's heuristic summary preserving exact tapes.

The `exec` route does not set `CTL_skip_verify`; its default is false. The
only assignment setting it true belongs to the separate enumeration route.
The printed `verified:` line is reached inside the checker only after all
checks pass, so it also establishes that the check was not compiled away.
I found no flaw in this source path. This is source review and replay
corroboration, not a formal verification of the C++ implementation.

## Short universal tape rules

A state marker appears immediately before the scanned cell. `W` is an
arbitrary continuation, and a displayed local rule never reads beyond the
displayed prefix. For every n >= 0:

```
F> 0 1^n 01 W  ->  0^(n+1) 10 F> W      in n+3 steps
F> 0 1^n 00 W  ->  0^(n+1) 11 A> W      in n+3 steps
```

Proof: F0 moves into G; G1 erases each of the n ones; G0 writes a one and
enters H; H1 clears a one and enters F, while H0 writes a one and enters A.
Thus these are universal sweep rules, not a pattern extrapolated from a
finite run.

The left sweep has the following local rules. In each, the last cell of the
input word is scanned by E:

| Input ending at E's head | Output in the displayed cells | Final head/state | Steps |
| --- | --- | --- | --- |
| `00` | `11` | A on the cell immediately left of these two | 4 |
| `010` | `011` | E on the cell immediately left of these three | 3 |
| `11` | `01` | E on the cell immediately left of these two | 2 |
| `110` | halts | halt | 3 |

These follow respectively from E0 C0 A1 A1; E0 C1 D0; E1 F1; and E0 C1 D1.
In particular, F scanning the final one in `1101` halts in four steps:
F1 E0 C1 D1. The halt trigger is therefore very local. Merely seeing a long,
growing tape is insufficient to rule it out.

Define the recurring left-boundary form

```
K(n,W) = ...000 F> 0 (10)^n 11 W.
```

There is a universal initialization rule

```
K(1,W) -> K(2,0W) in 17 steps.
```

With the initial F head at coordinate zero, the final F head is -3. The
exact transition sequence is

```
F0 G1 G0 H1 F1 E0 C1 D0 E0 C0 A1 A1 A0 B1 C1 D0 E1.
```

It never visits a coordinate greater than 4, the last cell of the known
`01011` prefix. Hence W really is arbitrary. Subsequent even-n configurations
often add pairs or reset n; a complete human-readable recurrence was not
needed once the finite-language invariant closed.

There are close-looking halting inputs: `K(2,00010011W)` halts after 21
steps, for arbitrary W. Its finite prefix trace is saved in the companion
JSON, and does not read W. The nonhalting proof establishes that the blank
trajectory avoids all such dangerous configurations. It does not claim
that every K-form input, or every tape sharing the same length/ones count,
is safe.

## Reproduction and scope

`unresolved_c09_review.py` uses an independent literal transition loop to
check the local formulas and traces, the 1001-step seed, both proof inputs
and diagnostics, and the saved source hash. It writes
`unresolved_c09_review.json`. These finite checks guard against transcription
errors; the universal sweep derivations and the generic closure induction
are the reasons the corresponding claims hold for arbitrarily long runs.

Earlier experimental files `unresolved_c09_profile.*` and
`unresolved_c09_local_rules.*` are retained as investigation evidence. Their
finite cutoffs and partial rewrites were not used to infer nonhalting.
