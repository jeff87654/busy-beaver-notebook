# Exact equivalences within C13-C16

The original IDs refer to discovery_holdouts.txt. This reduces duplicate analysis;
it does not by itself establish halting or nonhalting.

## Two unconditional equivalences from blank tape

C13 and C14 differ only in G1; likewise C15 and C16 differ only in G1.
In each pair the first machine uses G1 = 0RC and the second uses G1 = 0LE.
The only instruction entering G is F1 = 1LG. Consequently every reachable
G configuration has a 1 immediately to the right of the head.

When G reads 0, both machines take the same transition. When G reads 1,
the first machine executes

    G1: write 0, move right, enter C
    C1: write 1, move left, enter D
    D0: write 0, move left, enter E.

The C1 read is supplied by the preceding F1. The D0 read is supplied by G1.
The resulting tape, head position and state equal those after the second
machine's single G1 = 0LE instruction. Neither intermediate instruction halts.
All other instructions agree. Induction on matched configurations proves:

- C13 halts if and only if C14 halts, with identical final tape and head.
- C15 halts if and only if C16 halts, with identical final tape and head.
- If a pair halts, the first runtime exceeds the second by twice the number
  of G1 executions in their common computation.
- If either member is proved nonhalting, that conclusion transfers to its partner.

## A further conditional shortcut, not yet a global equivalence

C13/C15 and C14/C16 differ in the bit written by E0. If E reads 0 and both
adjacent cells also contain 0, these two choices converge:

    E0=0LC: E0 C0 A0 B0 A1 A1  (6 steps)
    E0=1LC: E0 C0 A1 A1        (4 steps).

Both leave two ones on the initial head cell and its left neighbor, preserve
the right neighbor, and put A two cells left of the initial head. The head's
new cell is not read by these paths, so all other tape contents are arbitrary.

A 500,000-step literal trace of C13 observed only such E0 neighborhoods.
This observation does not prove that the neighborhood condition persists.
No unconditional equivalence across the E0 variants is claimed here.

## Finite observations

unresolved_family_trace.py/.json records ordinary transitions for two million
steps per machine, including H0 checkpoints. The four machines agree at the
sampled H0 tape/head checkpoints while reaching them at different times.
These finite observations motivated the identities above and do not decide
whether any of the four eventually halts.
