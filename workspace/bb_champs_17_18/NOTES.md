# BB(17) / BB(18) champions (Jacobzheng): how they reach f_(omega+2)

Source: wiki.bbchallenge.org/wiki/Champions (fetched 2026-10-09). No analysis is published there; everything
below was derived here. Each rule below was checked on crafted tapes (test_engine.py, test_h.py, test_l.py).
The composed model (model.py) agrees with the full machines on all 24 small crafted starts that halt (validate.py).

    BB17 = 0RE1LD_0RH0RC_1RB1LD_0LD1LE_1LF1RA_1RG0LE_1RB1RG_1RL0LI_0LI1LJ_1LK1LK_1RG0LJ_0LP1RM_1RZ0LN_1LO1LN_0LG1LN_1LQ1LP_0LO1LP
           wiki bound > f_(w+2)(f_(w+1)^2(f_w^2(60)))
    BB18 = BB17 with one state inserted between A0 and E: A0=0RH, H=1RE1RA (later letters shift by one)
           wiki bound > f_(w+2)(f_(w+1)^3(f_w^2(60)))

The machines are a strictly modular three-layer stack.

| layer | states (BB17) | job |
|---|---|---|
| f_w engine | A B C D E F G (7) | Ackermann digit-list engine |
| w+1 | H I J K (4) | decrement counter c, rebuild the engine input from the accumulator |
| w+2 | L M N O P Q (6) | when c is empty: d -= 2 (halt if d = 1), refill c by merge; when d is empty: refill d by merge |

Tape at each engine start: `1^3 B> 1^l1 0 1^l2 0 ... 1^ln 0 0 1^c 0 1^d` (the list, then counters c and d).

## Engine (A-G)
- S: `1^3 B> 1^k 0` -> `1^(3k) 0 1 B>`; each 1 crossed adds 3 to the accumulator (a bounce, so quadratic time).
- pass: `B> 1 0` -> `0 1 B>`
- T: `1^A (01)^p B> 1^e 0` (e >= 2) -> `1^3 B> (10)^(p-1) 1^(A+1) 0 1^(e-1) 0`
- exit: `B> 0 0` (the empty block) -> H layer, with `1^A (01)^p 0` on the left.

Abstractly, for a list l, set A = 3*l1 and p = 1 + (the number of 1s that follow). At the first entry e >= 2,
the list becomes [1^(p-1), A+1, e-1, rest].
- [x, e] -> [f^(e-1)(x), 1] with f(x) = 3x+1, which is exponential.
- Each further list position adds one FGH level, so [1^m, 2] ~ f_m. Feeding m ~ A/2 ones gives f_w(A).

## w+1 layer (H-K)
- c >= 1: `1^A (01)^p 0 H> 1^c 0 1^d` -> `1^3 B> [1^m, 2] END 1^(c-1) 0 1^d` with m = floor((A-1)/2) + p - 1.
  H erases one cell of c; I walks left; J/K rewrite 1^A as (01)^(A/2).
  So each c-period is A -> f_w(A), and a full c-loop is f_w^c.

## w+2 layer (L-Q), entered by H0 when c = 0
- d >= 2: d -= 2 (L passes a cell, M erases the next), and N/O fill every single 0 leftward up to the `00`.
  This merges the whole engine output into one unary block: c := A + 2p + 2, list := [2].
- d = 1: M reads 0 -> **HALT**.
- d = 0: L0 -> P/Q, the same merge but bridging one more `00` gap: d := A + 2p + 3, c := 3, list := [2].

d counts down by 2 per c-loop (f_(w+1) each time), so one d-run is f_(w+1)^(d/2) = f_(w+2). When d hits 0 it is
refilled from the accumulator. **Halting is a parity gamble.** A refill with odd d (equivalently A even, i.e. the
exit l1 even) halts at the end of that d-run. An even refill runs another, larger d-round.

## Trajectory
- BB17: P/Q fires at step ~7 (d starts 0) -> d = 6.
  - d 6 -> 4 with c = 5: the small c-loop, ending in two real engine runs ([1^61, 2] and the next) = f_w^2(~60).
  - d 4 -> 2 and 2 -> 0: f_(w+1)^2.
  - d refilled to an (assumed odd) huge value: f_(w+2)(d/2), then halt.
- BB18: the only difference is the first transition (H0 writes a 1), so d starts at 8: one more f_(w+1).
- The parity of the second refill was not checked here; the wiki asserts the halt.

## Lessons for a ~11-13 state f_(w+2)
- The design is modular and state-wasteful. Their w+1 layer alone is 4 states on a 7-state engine, and their
  w+1 champions BB(14)-BB(16) are 14-16 states, against n1's 10.
- What w+2 needs on top of an n1-type w+1 machine:
  - (a) at counter exhaustion, refill the counter from the accumulator instead of halting (merge gadget, 2 states).
  - (b) a second counter, decremented once per refill, that halts when empty (2 states).
  - (c) d must be accumulator-sized at least once. BB17 refills it with a P/Q copy of the merge, which also
    initialises it; d = initial b would already give f_(w+2)(b).
- A non-halting looper that re-parks a counter from its accumulator every period (an f_(w+1)-per-period looper,
  e.g. check whether G6 in halt_redirect is one) already has (a). It then needs (b) plus an initial d.
