# farcount (route 1: far run as outer counter d) -- running notes (Opus investigator, 2026-10-10)

## Geometry facts (measured, j0site.py / dumpj0.py)
- far_of(k) = (10101)^k + 44-bit tail, LEFT of the word.  Each round builds its OWN D2 run (Per 2^k token run,
  ~4 per period = 2c/7) at the left end of its word, i.e. RIGHT of any older far region.
- Round start with an old far region on the left (far_20 + [2 5 1^c 0^3 9 1^41|1|19], n1, J0 undefined), J0 read site:
  - class 9: new round's own tail idx 22 (new far = new D2 run + new tail, right of the old far);
  - class 4, 6, 11: right end of the NEW D2 run (site moves +20 cells per period);
  - **class 12: OLD far tail idx 22 (abs 122 for K=20), independent of c**: the class-12 end walks left over its own
    D2 run and presents the old far region exactly as at round 1's end (D2^K + tail[0:22] | J0), with a different
    right side ('0001111001001..' vs '0010111100100..' at round 1);
  - classes 1, 2, 5, 7: far right (thousands of cells): those ends spread junk.
  => class 12 is the only round-end class whose J0 event sits on the OLD far region.  A class-12 in-place restarter
     would re-meet the same far run each round (the route-1 shape).
- Restarters keep or eat D2s at restart: T12a eats 7 (k -> k-7, 22-bit tail), H13c 12, Q12a 6 once and then never
  (class-9 rounds, far tail +79 bits per round, kD2 constant).

## Survey (survey.py -> survey.tsv): all RS leaves of inplace ie2_1RK/ie2_0RK + t12scan trees (2373 machines),
   start far_29 + [0 1^29|1|19] std, kD2 at each restart.
- Class-12 J0 site robust: abs 5K+22 for K = 5/20/37 and c = 26/40/82/124 (std); prefixes P = 1, 2, 3, 9 keep it
  (P = 7 or '3 1' -> old tail idx 42); P = '2 1 6 6 36 2 0 7' (a real restarter's prefix) moves it into the new word
  (abs 358): prefixes/deposits can hide the old far.
- Survey (partial ~1000/2373): kD2 drops ONCE at the first restart (T12a 7, H13c/F12 12, Q12a 6, class-12 c=26
  restarters 10) and is then CONSTANT through 6 restarts in every machine; 'DEC' cases = one more one-time drop.
- Non-in-place eaters (k = 29/71 std; true order from h14verify): L12/D1/H14 erase the far run in round 1 (k -> 0,
  then ~8R leftward unpack); C13a (true order) leaves it as inert debris.  None eats per round.
- Tools: fgstage.cpp/.exe (= igstage + ' | G n q@pos..' gadget-read list), fl.py (ilib copy using it), farfol.py
  (kD2 per restart), gread.py (per-stage trace with absolute gadget reads), j0site.py/j0big.py/dumpj0.py (J0 site).

## enum12 (class-12 end at the old far, J0 free, ns=2, K=29 c=40 z=29, std): STOPPED partial at 17k nodes
   (J0 = 0LA..0LJ leaves + J0 = 0LK subtree up to K0 = 0RC..): 3 EAT (one-time eats 29->0/18/24, then classes 7/6),
   6 NOEND (eat 2 -> class-12 round with prefix '0 2 0 7' -> its end borrows 7->4 -> n1 junk cycle), 0 repeated eats.

## PREFIX-DIGIT BORROW at class-12 ends (new lever, prefscan.py / dctx.py / ttrace.py)
- n1 from [D 2 5 1^c 0^3 9 1^z|1|19] (no far): the class-12 round end BORROWS 3 from the prefix digit D (D -> D-3,
  any D = 30..400 tested), then reads J0.  Also class 2 borrows 3, class 11 borrows 9; classes 4/6 leave D intact.
- J0 context after the borrow depends on c mod 42: c = 40 mod 42 (40, 82, 124): J0 at the LEFT END (blank) with D-3's
  cells walk-marked ('0 11111' per 3 units; D mod 3 changes the first cells); c = 26 mod 42 (26, 68, 110): J0 inside
  the word ('97 22/46/70 41 0 43 ..'); c = 12 mod 42 (54, 96): not finished (slow).
- Without the digit the class-12 end is n1's own left event: restart counter 4R+3 = 79 (class 9).
- Route: gadget restarts class 12 in place keeping D-3 as prefix digit => rounds ~ D/3; D ~ R (accumulator) if the
  round-1 restart leaves R as the prefix digit (P11 does this) => f_(omega+2).  enumD.py (= enum12 + --pre) screens it.
- enumD c=40 (J0 at the left end after the borrow), D=100, K=0, ns=2, J0 free: COMPLETE, 91,820 nodes:
  DGONE 53,599 (digit absorbed, mostly by the left-event restart c=4R+3 with empty prefix), RS 17,880, W 15,170,
  HALT 1,912, T 3,232, 1 DDEC1 (..._1RK0LC_1RK1RL_1RI0LI: prefix ..95, c=92 class 8, writes left).  0 class-12 cycles.
- J0 context at c = 26 mod 42 (26, 68; D = 100/101/102) is identical in a 220-cell window: D-3 walk-marked
  ('100000' blocks) LEFT of the head, the round's converted D2 run (token 22+24j) and '41 0 43 1^w' to the right.
- enumD c=26 (J0 inside the word after the borrow), D=100, ns=2, J0 free: COMPLETE, 253,100 nodes: DGONE 215,196,
  RS 8,569 (no D-d in the prefix), W 17,823, T 6,238, HALT 5,272: 0 DDEC.  => no 12-state class-12 borrow cycle.
- Sanity: enumD on P11's round-2 end (pre 19, c 35, J0=1RK, K0=1RC) reports DDEC1 (prefix ..18, class 13) as expected.
- Borrow table (btable.py, D = 100, z = 29, std): the digit survives as D-d at the J0 stage for c mod 42 =
  25 (class 11, d = 9), 26 and 40 (class 12, d = 3), 30 and 44 (class 2, d = 3), 38 (class 10, d = 3, messy).
  Not: c mod 42 = 39/53 (class 11), 12 (class 12: junk K), 35 (class 7, digit absorbed; P11's class-7 borrow had D=19
  and a far region).  Classes 4, 6 and c = 49 (class 7) leave D UNTOUCHED (J0 at the right end of the new D2 run).
- queueD.sh: enumD ns=2 at c = 30, 44, 25, 38 (sequential, 1 process; continue-following if the restart class
  equals the start class mod 14).

## Overlap notice (2026-10-10)
- Found w2_search/borrow/ (inv-w2-borrow, "Route 2: prefix digit as outer counter d"): it already covers the
  prefix-digit borrow cycle (class 7 / class 12 tapes, ns = 2 complete for class 12: 366k nodes, no d-keeping cycle;
  class-12 J0 read at the right end of the old far with d-3 unrolled into marks = same as my dctx finding).
  I stopped my digit-route queue (enumD c=30 partial 109k nodes: 452 DDEC1 = restarts keeping 97 somewhere in the
  prefix, never adjacent; survey2/continuation not run) and returned to the far-run route only.
- queue5.sh: enum12 per J0 subtree (0RK, 1RK, 1LK, then 0LK in full), cross-class following of eaten rounds,
  maxs 1.5e7.
- enum12 speed: NORS leaves were all n1's growing-far junk cycle (tokens start '1 3 1^2 0 1^2 ..', base slots only, no
  restart ever; 30/30 sampled).  Added a JUNK leaf on that signature: ~45 nodes/s.
- 2026-10-10 lead: all farcount scripts now set their own priority to Idle at import (child fgstage inherits).
  Launch from an Idle parent and check with Get-Process. At report time nothing of mine is running.
