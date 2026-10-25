# G6 slice of the f_(omega+2) search: REPORT (Opus investigator, 2026-10-09)

G6 = `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1RJ1LA_1LI---`

## Verdict: NEGATIVE. No Tier 1 or Tier 2 machine. G6 cannot host an outer counter with 2-3 extra states.

Evidence level: literal measurements on G6 itself, plus a capped (non-exhaustive) enumeration. There is no positive
result to verify.

## Why G6 cannot carry a counter across a round boundary
At every left event (the end of a round) G6's whole state is `[1^N | 1 | R]`, with fixed residues
(R = 19 mod 2520 every round). A left event happens only when every list digit is a zero. So an outer counter d
would have to live outside the list, and both ends of the tape get overwritten:

1. **The left end is rewritten at every left event.** The repack is the BASE machine's left-end unpack. The borrow runs
   off the left end (B1 at the list's first cell, then F0 one cell left). The unpack then writes (011)^(4r+8) blocks
   into fresh cells to the left. After that, the E0/I/J conveyor turns those blocks into the new D6 run.
   - Leftmost cell reached = -(8r+26), measured exactly for r = 19, 79, 139, 259 (-178, -658, -1138, -2098).
   - In the real run R is astronomically large, so any structure at a fixed offset to the left gets overrun.
2. **Nothing placed to the left survives a left event.** survive.py put every far-left bit pattern of length <= 8 at
   gaps 1-6 in front of `[1^30|1|19]` (1,530 cases) and ran one literal stage of G6:
   - 36 cases give G6's standard repack, and in every one of them the pattern was erased (clean tape).
   - 1,094 cases change the tokens: the pattern is read as a list digit (so no left event happens) or merged.
     A far token D(X) at gap 2 is merged into the new counter (6^16 8 becomes 6^18 8 for X = 4, and the token is gone).
   - 400 cases are W (run off the tape width).
3. **The list and the right end are rewritten too.**
   - Every token left of the D6 run is absorbed at exhaustion:
     - G6's growth/exhaustion walk is `[X Y 1 P 0 1^n|1|r] -> [X-2, 2r-(P-3)/2+1+Y, 1^(n+P+2)]`.
     - With X blank the walk absorbs Y as well: `[Y 1 P 0 1^n] -> 7 1^(n+..+2Y)`.
     - A token behind a separator acts as an f_omega digit (R3, eaten 3 at a time) and is used up before the left event.
     - The D2 refill rule `[d 2 1^n|R] -> [d-3, 2R+6, 1^n]` refills a token counter, not a D6 run.
   - The zero list is fully cycled.
   - The accumulator r grows rightwards to accumulator size.
4. **No cheap hook exists.**
   - Consecutive slot-read k-grams were collected for k = 2..6, with 23 normal period configs (including r = 2539 and a
     parked P = 5081) against 6 special configs (exhaustion, `7 1^n`, left event and repack).
   - Every k-gram seen in the special stages also occurs in normal stages.
   - So no clone-split chain of up to 5 cloned states can fire only at a round boundary. Detecting the boundary needs
     a side probe of about 3 states (K, L, M), and that leaves no state for storing or moving d.

Consequences:
- **Tier 1** would need at least 1 bit carried through the base machine's 8R-cell unpack, plus a conditional rewrite of
  that bit at the far end. That takes more than 3 states.
- **Tier 2** would need d of accumulator size; there is no place to keep it.
- Even a toggling flag written by the conveyor cannot tell the startup left event apart from later ones. Stage 0 is
  the same left event as every later one: the record's K(0^35;0;b) exhaustion.

## Enumeration (supporting evidence only, not exhaustive)
gs13.py redirects one of G6's 19 defined transitions X to a new state K (keeping X's write and move). K, L and J1 are
free and enumerated lazily, TNF on the new states. Each machine is followed from the real start in the std world
(b0 = 6) for 60 stages, which is more than 2 rounds. Round 1 (stages 0-25) must reproduce G6's tokens exactly; far
bits may differ.

| outcome | count |
|---|---|
| stage-nodes in total (every entry's DFS was stopped by its 4,000-node cap) | 78,745 |
| halts at stage >= 20 | **0** |
| halts inside round 1 | 1,604 |
| round-1 token mismatches | 11,079 |
| T (time-outs, junk loops) | 29,476 |
| W (run off the tape width) | 32,079 |
| ALIVE at stage 60 | 28 (27 exact G6 emulations, 1 other non-halting run) |

The T and W leaves are mostly junk loops. Because of the caps this is only a sample of each tree. The 13-state
(K, L, M) tree was not run.

## Tools (all in this dir; see NOTES.md)
- stage13.cpp/.exe and g6lib.py: the GH-family stage runner and follower for machines of up to 16 states.
- st.py: one literal stage per crafted configuration.
- evtrace13.cpp/.exe and ev13.py: event tracer with per-slot counts, positions, pair counts and the leftmost cell.
- snap.py, traj.py, firstleft.py: tape snapshots, step windows, and the first reads left of the list.
- kgram.cpp/.exe, kg.py, kgcmp.py: k-gram context comparison of special against normal stages.
- survive.py: tests whether a far-left pattern survives a left event.
- gs13.py: lazy gadget enumeration through the real-start follower.

## Recommended next step
- Drop G6 as a w+2 base. Its counter refill is the base machine's left-end unpack, which destroys everything outside
  the list.
- Prefer a base whose counter refill happens in place, or one with no left event:
  - n1: its far region (FarE k) persists, and event H turns the accumulator into a counter list in place. Check that
    H can be re-triggered at exhaustion without a left-end unpack.
  - An engine that grows in one direction only, as in BB17, with c and d on the side the engine never extends.
- A G6-specific route would need a gadget that pushes a marker ahead of the unpack frontier. That costs at least about
  6 states and is outside the 12-13 state budget.
