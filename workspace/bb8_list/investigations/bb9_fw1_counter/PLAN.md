# bb9_fw1_counter PLAN (design phase, 2026-10-22)

Goal: 9-state f_(omega+1) halter = 7-state f_(omega+1)-type looper (rebuilds a list ~ accumulator at every
exhaustion E, never halts) + a 2-state COUNTER gadget (created once, read/decremented once per round, halt when empty).

## 1. The 18 dl3 bases (F1 r s h u, F2 i a b c t j, F3 d f o n e g p q): DESIGN-LEVEL NEGATIVE

Geometry (literal, tm.py/look.py/micro.py on r, i, d, p; the rest share rule sets):
* All three families are v-coded odometers: digit d = 1^d 0, zero digit = a single 0, accumulator = a unary run
  next to the least significant digit (LSD). F1/F2: list left, accumulator right; F3: mirror image.
* D-phase: the accumulator grows OUTWARD at the LSD end (r: right frontier moves ~2A per D step).
* Borrow walk Bk = exhaustion walk E: the accumulator run is TRANSPORTED toward the most significant digit (MSD)
  one cell per iteration (r: G sweeps left through the run, G0 writes 1, look-ahead C reads the next cell:
  C0 = zero digit, continue; C1 = nonzero digit found = borrow), emitting tail digits behind it. E = the run is
  used up before a 1 is found (blank beyond the MSD); the rebuilt list (~1.5A digits) extends the MSD frontier
  into new territory. So BOTH frontiers move every round.

Consequences:
(a) v-coding is COMPLETE: every binary word parses as a digit list (any 1 = part of a digit, any 0-run = zero
    digits). The walk's only look-ahead is "next cell 0 or 1" and the borrow handler reads only the found digit's
    last cell. So anything parked beyond the MSD, behind any gap ("00" = two zero digits), IS the leading digit:
    the walk borrows from it ([c,0^k;A] -> [c-1, refill, tail], list length FROZEN at k+1 until c = 0, then E
    and growth resume). Literal (parked.py): i [3,0,0,1] -> [2,15,2,2]; d [2,0^4,1] -> [1,14,3,2,2,1]. It never
    halts: the parked counter just multiplies one round.
(b) Anything parked beyond the LSD end is absorbed by the first D steps (lsdpark.py: the block becomes digits /
    accumulator within ~100-800 steps for r, i, d, gaps 2..30).
(c) Hence with the engine intact (gadget entered only from the E-end slot or the halt slot) nothing but the
    accumulator crosses an exhaustion, and the E-end gadget sits at the new MSD frontier (blank) and can read only
    the run's leftover = a residue of A: the bb8_fw1_redirect finite-state argument (<= ~1 certified rebuild).
(d) A gadget on an engine slot fires in normal contexts too. Example r: the borrow is found by C1 = 0RB at the
    digit's last 1 (cell p). Put C1 -> 1LH: H reads p-1 and must come back to p in a
    state doing C1's old action, i.e. H1 = 1RI, H0 = 0RI, I1 = 0RB (p-1 = 1: digit >= 2; p-1 = 0: digit 1; both
    occur every round); I0 is then unreachable (I always reads the kept 1). Looking one cell further
    (H -> I reads p-2, return needs a third state) all four patterns 11, 10, 01, 00 occur in normal borrows (digits >= 3,
    digit 2, digit 1 after a nonzero digit, digit 1 after a zero digit), so again no branch is free. By coding
    completeness the same holds for any slot of the walk/borrow handler: two states cannot see a pattern that a
    normal list does not also show. A counter would need transport of a unary block with the walk (>= 3 extra
    states, as in the G6 lesson) or a different coding.
Verdict: no 2-state counter gadget exists on these bases with the engine's semantics kept; modified engines are a
different machine class (the 8-state census in bb8_fw1_redirect found nothing there).

## 2. W1-LOOPER rows (4, dl3_triage7): tape span ~ sqrt(t) to 1.07e9 steps (width.exe): polynomial, not record class.

## 3. NEW POOL (next): dlscan3 LOOPER rows with an INCOMPLETE coding and an MSD prefix P
dl3_hits/out.tsv 359 LOOPER + dl3_triage7/out.tsv 256 LOOPER; most have u in {110, 01, 10} and P in {1100, 1010,
1, 100, ...}: codings where a separator / marker is locally recognisable (BB(13) champion template
"(110)^n 1 0 [inner] 1^b -> (110)^(n-1) 1 0 [~b digits]"). Requirements for a counter host:
  R1 real (blank-tape) rebuilds whose cleared list grows with the accumulator (judge by CLEARED lengths);
  R2 the MSD end (prefix P) stays put at E, growth on the LSD side (one-sided), so cells beyond P survive rounds;
  R3 a slot read only at E (the walk meeting P), from which a gadget can look past P.
Steps: (i) literal geometry screen of all LOOPER rows (MSD frontier fixed across rebuilds? growth per round?
E-only slots?), (ii) for survivors write the gadget spec (counter = blocks beyond P, decrement at E, halt when the
walk past P meets blank), (iii) enumerate only those gadgets (2 states, entry = the E-only slot), (iv) screen with a
K-level run counting rounds, cleared lengths and counter size.
