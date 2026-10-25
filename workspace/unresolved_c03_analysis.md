# C03: exact partial reduction; still unresolved

Machine: `1RB1LA_0LA0RC_1RA1LD_0LE0LF_0RA0LD_0LC0RG_1RH1RZ_0RG0RE`.

The sole halting transition is G1. The observations below are not a nonhalting proof. They reduce the outstanding question to a specific local guard.

## Universal lemmas

Use integer tape coordinates. Unmentioned cells are arbitrary and unchanged.

1. **C-origin safety.** Start at C on a 1 at coordinate x. C1 preserves this anchor and enters D at x-1. Each subsequent D0,E1 pair clears a 1 two positions to the left and crosses a 0 between it and the anchor. If the first D1 occurs after k such pairs, it clears x-(2k+1) and enters F at p=x-(2k+2). If F reads 1, every cell strictly between p and x is 0 and the distance x-p=2k+2 is even. If F reads 0 it returns to C instead. An E0 exits through A. Consequently an F1 reached through this C1/D/E sequence always has an even distance to its next right-hand 1.

2. **Safe G/H excursion.** For n>=1, F scanning the first cell of `1 0^(2n-1) 1` transforms that interval into `0 (10)^n` and enters E immediately to its right in exactly 2n+1 transitions. G always reads 0, and the terminating right-hand 1 is read in H. If the cell at E is 0, one more transition enters A two cells to the right of the original anchor.

3. **Rollback.** If that E cell instead contains 1, E1 clears it and the D/E sequence erases the entire newly written alternating trail. After 2n+2 further transitions it reaches E at p-1, immediately to the left of the original F head p. All cells p through p+2n+1 are now 0. If p-1 was 0, another transition enters A at p. The combined suffix-preserving macro is therefore

   `0 (F:1) 0^(2n-1) 11  ->  0 (A:0) 0^(2n+1)`

   in exactly 4n+4 transitions, with the head positions shown; all other cells are untouched. This notation includes the left guard cell and the cell after the anchor.

These follow directly by induction on the number of D/E or G/H pairs; they apply to arbitrary tape contexts satisfying the displayed premises.

## Sufficient unresolved invariant

At every reachable F1 configuration, write p for the head and q for its nearest right-hand 1. The needed guard is:

> If the cell q+1 is 1, the cell p-1 is 0.

Together with the three lemmas this would imply nonhalting: the first G excursion must originate from C1; every such excursion is safe, and the guard makes every rollback return to A before another F/G visit. A later F visit then again originates through C1. Thus G1 can never be reached. The guard has not been proved invariant, so this conditional argument does not classify C03.

## Bounded observations

An exact literal simulation from blank for 2,000,000 transitions (no macro acceleration) encountered 48,742 F1 events. The distance to the next right-hand 1 was 2 in 1,014 events, 4 in 47,308, 6 in 251, and 8 in 169; no odd distance appeared. Every F1 was preceded by a C visit after the most recent H1.

Of the H1 exits, 48,159 took E0 directly to A. The other 583 erased a trail and returned to A: 414 followed `(E1 D0)^3 E0 A0`, and 169 followed `(E1 D0)^4 E0 A0`. Their originating F events had (anchor distance, left-neighbor symbol) respectively (4,0) and (6,0). There were no observed violations of the proposed guard.

The first 100 sampled F events misleadingly all had distance 4; checking every event exposed distances 2,6,8. This is why the remaining guard is recorded as an open invariant, not inferred from the sample.

Artifacts: `unresolved_c03_trace.py/json`, `unresolved_c03_structure.py/json`, `unresolved_c03_origins.py/json`, and `unresolved_c03_rollback.json`. The trace records complete tapes at selected events; the structure and origins scripts collect every F event within the fixed bound. No broad native search or longer simulation is proposed as a replacement for proving the guard.
