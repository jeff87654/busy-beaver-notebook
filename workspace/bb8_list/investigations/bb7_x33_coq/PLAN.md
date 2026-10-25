# X33 Coq plan (ABANDONED 2026-10-22: halting claim false)
Machine 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE. Planned: champ_231-style proof (R1/R2/R3 micro lemmas, CDP clearing,
init by `do 4442 step`, halt at the true exhaustion K([],0,b3), score b3+3 with b3 = U32(U32(U31(W31 7)))).
Abandoned before any Coq: the parity check shows b3 is even, so the machine rebuilds there instead of halting (see REPORT.txt).
A Coq NON-halting proof would reuse the same rules plus a closed invariant (total ones even, counter >= 2*depth at each borrow).
