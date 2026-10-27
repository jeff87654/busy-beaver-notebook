# Search code behind M13

These two C++ programs were written by Argon (a Google Gemini model) during the search that found M13, on
2026-10-13/14. They are copied here unchanged (sha256 below). Their search claims are Argon's. The section
"Re-runs" says which outputs we reproduced and which we did not.

`search_core10.cpp` uses Argon's **core labels**, not M13's labels. In core labels the start state is H, and M13 is

    1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_0LK1RJ_1RE0LA_1RA0RF_1LH1LA_1RB1RM

This is M13 with its states renamed A..M → H, G, M, B, A, I, K, F, J, L, C, D, E (checked entry by entry by
`../tools/m13_writeup_chk.py`).

Compile with `g++ -O2 -o search_core10 search_core10.cpp` (likewise `search13.cpp`). Neither program takes
arguments. The parameters are in `main`.

## search_core10.cpp

- **The fixed core.** It fixes a 10-state core: 17 transitions of states A, B, C, D, E, F, G, H, L, M, including
  B0 = 1RA. It leaves free the core slots A0, E0, F0 and the outer states I, J and, with 13 states, K. So a 13-state
  machine has 9 free transitions, and a 12-state machine (no K) has 7.
- **The search.** It runs a depth-first search over the free slots. It defines a slot only when a test simulation
  reads it, and uses a normal form: J appears only after I, K only after J, and A0 must move right.
- **The tests.** Each test starts from `0^∞ (10)^p 1^(A+2) A> 0 1^d` and runs until state A returns to a `(10)^c'`
  block with the tape in the same shape. Four tests (d = Δd, Δd + 1 and A = 6, 8) require a C_REL-type reload:
  - the new inner counter c' ≥ A/2;
  - d falls by exactly Δd;
  - p', a', c' do not depend on the extra 1 of d.

  Three more tests (d = 0, d = 1, and p = 1) look for a D_REL-type reload on one input and a 1RZ halt on the other.
- **The output.** It prints each hit as `HIT_D0_VS_D1[_PARITY_OK]` or `HIT_P1_VS_P2`, with the machine string. A
  hit is a partial machine. Choosing the remaining slots and checking the run from the blank tape was a separate
  step, and that code is not here.
- **The `main` as shipped** runs only the 12-state case (`init_base(12)`, at most 6 slots for C_REL and 7 in all),
  for Δd = 1, 2, 3.

## search13.cpp

- **The fixed core.** This is the earlier 13-state attempt on the core of the 14-state machine M14
  ([`../../BB14/`](../../BB14/)). It uses the labels of Jacobzheng's BB(14) champion, which are M14's labels with A
  and M swapped (start state M). It fixes B0 = 1RI and I1 = 0LA (M14's I1 = 0LM), among others. It leaves 7 slots
  free: E0, F0, I0, and the states J and K.
- **The tests.** Each test starts from `0^∞ (10)^p 1^(A+1) I> 0 1^d` with p = 4. It requires a C_REL-type reload
  that takes 1 from d for d = 1, 2 and A = 7, 8, and a D_REL-type reload for d = 0.
- **No halt.** It does not look for a halting transition.
- **The output.** It prints every completion with at most 7 defined slots (`[BOTH n_def=…]`) and a count by the
  number of defined slots.

Argon's write-up also cites `search_13_joint.cpp`: a joint search over all 9,754,218 outer assignments on M14's
9-state core, which it reports found no halting machine. That file did not survive and is not here.

## Re-runs (2026-10-14, g++ 16.1.0 -O2, on a shared laptop)

| program | what was run | result |
|---|---|---|
| `search_core10.cpp` | as shipped (12 states, Δd = 1, 2, 3) | 31 s. **0 hits** for each Δd. This matches Argon's report of no halting 12-state machine on this core. Argon also reports "6 non-halting loopers"; this version of the code has no such category, so we could not check that number. |
| `search_core10.cpp`, `main` edited in a scratch copy | 13 states, Δd = 2, at most 5 slots for C_REL and 9 in all | 4 s. **111 hits.** One of them is M13's full 9-transition core-label string above, tagged `HIT_D0_VS_D1_PARITY_OK`. Argon reports 180 gadgets. Its exact limits are not recorded, so we did not reproduce that count. |
| `search13.cpp` | as shipped | 58 s. 8 completions, each with all 7 free slots defined. So no slot is left for a halt. |

These are search results for these fixed cores only. They are not bounds on BB(12) or BB(13), and they do not show
that no 12-state machine reaches f_(ω+2). The proof that M13 halts and the bound on its score do not depend on any
of this code.

## Hashes

    374c6b2c373774454493bc256475aaa3c26c24283495466d430a6f443628ccef  search_core10.cpp
    66c2871c3574249cacdf492c8a7eb209e27788cbf87197458c6a12b5b8a90a61  search13.cpp
