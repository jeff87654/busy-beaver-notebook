# bb9_m9seed: 9-state machines seeded from Argon's M9 counter engine (started 2026-10-17)

## Engine (verified literally, chk_core.py / m9s.exe runt)
- 13 core slots (M9 labels): A0=1RB A1=1RA B1=1RC C0=0LD C1=1LG D0=0RE D1=1LD E1=1RF F1=0RA G0=1RA G1=0LH H0=1LG H1=1LH.
  Free in M9/M11 alike: B0, E0, F0 + the 9th state I.
- Ch j b z = 0^inf (10)^j [H on last 0] 1^(b+1) 0 z  -->  Ca j (W j b) z = 0^inf (10)^j 1^W [A on 0] z
  (W 0 b = b+3, W 1 b = 3b+5, W 2 b = (3^(b+3)-5)/2, W (j+1) b = iter (b+1) (W j) 2). Uses only the 13 core slots
  (literal check j<=2, b<=3; Coq CH_CA in BB9_M9_halt.v and BB11_M11_halt.v, which differ in B0/E0/F0/I).
- M9 outer loop: Cb p (Z+1) -> Cb (p+2+W(p+1,1)/2) Z, Cb p 0 halts; each Cb step = 2 top-level Ch jumps at j=p.

## Tools
- m9s.cpp / m9s.exe: literal simulator + exact Ch accelerator (used only when the 13 core slots are intact);
  values W > CAP replaced by a representative R >= RBASE with W's residue mod 18 (screening only).
  Modes: enum (tree over free slots from blank, any start state), mut K (Hamming-K mutants of M9), run / runt.
  Validated: M9 from 0 0 (111100)^1 gives sigma 23 with and without the accelerator (979 vs 1710 steps).

## Run log
- 2026-10-17 enum1/: free-slot tree (B0 E0 F0 I0 I1; 13 core slots fixed), blank tape, each start state A..I
  (C, D, E give the same tree: C0=0LD, D0=0RE lead into E0). Budget 1e5 literal steps, RBASE 40, CAP 1e5.
  ~1.2M leaves; 144k halters; holdouts 760k (A-H) + 253k (I).
  Best halters: start B/F machines with one Ch jump at j=3..4 (sigma ~ W(4,0) = W2(W2(119)), an f_4-ish number),
  e.g. 1RB1RA_1LI1RC_0LD1LG_0RE1LD_1RG1RF_1RZ0RA_1RA0LH_1LG1LH_1LH0LD start B. Far below fw2.
  ~89k holdouts made >= 1 jump with W > CAP (REP); the ones inspected are "linear-j" loops
  (Ch j b -> ... -> Ch (j+d) b with constant b), i.e. non-halting under the representative.
- Bug fixes during the run: representative must be >= b+3 (else z shifted left); recursive W replaced by closed
  forms (W3: only W 3 0 = 119 is small; j>=4 always big) - deep recursion crashed at j ~ 3800.
- pass2/: all holdouts re-expanded with enumroot at 1e6 steps (running).
- pass2 (1e6 steps, all ~1.01M holdouts re-expanded): no holdout reached an undefined slot between 1e5 and 1e6
  steps; 1 new halter (sigma 367, no big jump). So the free-slot tree is closed at 1e6.
- grade1/ (m9s grade, RBASE 40, mod-36 representative, 1e6 steps) on the 144,277 holdouts that made >= 1 Ch jump:
  NO halts. Classes: LINJ 14,226 (Ch j b -> Ch j+d b, constant b), NEARLINJ 605, OTHER 127,198 (sampled: j grows
  by 1 per jump while b ~ previous W grows: self-feeding loops that never reach the halt slot), norep 2,248.
- Representative fixed to mod 36 (W_j b mod 4 = 3 if b even else 2 for j >= 2, by the same induction as M11's
  mod 18; together 11 / 2 mod 36).
- grade2/ (RBASE 76, so a different residue mod 8, 5, 7): same classes, again NO halts (an undefined slot would
  show as HALT in grade mode).
- mut2/ (all 1- and 2-slot changes of M9, 37 values per slot incl. halt, start A, 1e6 steps, accelerator on when
  the core is intact): 177,480 machines; best halter sigma 32 (literal); no halter after a big jump. Holdouts:
  6,152 core-intact (all jump loops of the kinds above), 58,203 core-broken (39k translated, 6.7k span < 200,
  12.4k mid-span listed in mut2/broken_mid.txt, not graded: no accelerator for a broken core).

## Best halters found (exact-core space; sigma checked at R = 40/76/400/4000: sigma = R + const)
| machine (M9 labels) | start | top jump | sigma |
|---|---|---|---|
| 1RB1RA_1LI1RC_0LD1LG_0RE1LD_1RH1RF_1RE0RA_1RA0LH_1LG1LH_1RZ0LB | F | Ch 3 3 | W(3,3)+7 = W2^3(119)+7 ~ 3^3^3^122 |
| 1RB1RA_1LI1RC_0LD1LG_0RE1LD_1RG1RF_1RZ0RA_1RA0LH_1LG1LH_1LH0LD | B | Ch 4 0 | W(4,0)+6 = W2(W2(119))+6 ~ 10^10^57.8 |
Both are towers of 3s of height ~4: below f_4(10), nowhere near fw2 (f_w(f_w(465009))).

## Conclusion (2026-10-17)
In the space "M9's 13 engine slots + any values for B0, E0, F0, I0, I1, any start state" (complete tree from blank,
1e6-step screening, representative grading at two bases) no machine makes two big jumps and then halts. Every
machine that makes a big jump either halts right after it (one top-level Ackermann call, sigma ~ W(3..4, small))
or enters a self-feeding loop (j grows forever, the halt slot is never reached). The engine cannot be shrunk:
the half-states B, E, F all use only their 1-slot, so no two can merge. => Argon's engine needs > 9 states for a
working bootstrap (M11 uses 11).
