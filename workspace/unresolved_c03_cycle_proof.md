# C03 is nonhalting: a translated suffix cycle

Machine: `1RB1LA_0LA0RC_1RA1LD_0LE0LF_0RA0LD_0LC0RG_1RH1RZ_0RG0RE`.

C03 is **proved nonhalting** by a finite repeated computation, independently replayed by two separate literal simulators. The earlier rollback guard remains unproved and is not used here.

At transition 83,806 from the blank start, the machine is in state F with head at coordinate -50. Take the boundary B=-54. Its entire tape at or right of B is the following finite word S, followed by infinitely many zeros; the head is four cells to the right of B:

`0110100010010011000101100011000110001100011000100100011000101110001100011000110001100011000101100010001000110001010011000110001100010010001100011000110001001100011000100111000110001`

The next 23,636 transitions do not halt. Every read and write lies between coordinates -51 and 159, so no cell left of B is consulted or changed. They finish in state F with head at -18, and replace the suffix `S 0^omega` by `W S 0^omega`, where

`W = 01110010100101010111100101000101`

has length 32 and contains 16 ones. The complete suffix from B+32 at the end therefore equals the initial suffix from B, and the head has translated by 32.

This finite computation applies for **any** tape left of B. Determinism makes the next period execute the same transition sequence translated by 32 cells. Inductively the process repeats forever: after n periods the boundary and head have shifted by 32n and the tape contains `W^n S 0^omega` to the right of the original boundary. No period reaches the halting state. Thus C03 cannot be a Busy Beaver contender.

## Reproduction and provenance

`unresolved_c03_suffix_cycles.py` discovered the witness within the previously examined two-million-step bound. Its JSON uses a loop-index-plus-one search counter; the exact certificate timestamps are 83,806 and 107,442 transitions, independently reconstructed below.

`unresolved_c03_verify_cycle.py` parses the machine independently, literally replays its blank start, checks complete suffix equality and the exact read range, and replays two additional periods. It imports no simulator or accelerated transition code. Its output is `unresolved_c03_cycle_certificate.json`, containing all endpoint tapes, the suffix, parameters, and source hash.

The audit agent independently checked the same finite macro while representing cells left of B as unknown. It confirmed no unknown cell is read, exact translation +32, and read/write range [-51,159]. Its independent artifacts are `lastfive_decider_c03_independent.py/json`.

The period is 23,636 transitions, not the simulation cutoff. The conclusion follows from the inductive recurrence, not from surviving a long simulation.
