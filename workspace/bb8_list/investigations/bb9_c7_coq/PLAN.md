# PLAN: Coq proof for C7 (bb9_c7_coq)

C7 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA (9 states, H1 the halt).

## Architecture (as for f3): auxiliary 11-state X', then a simulation down to C7

    C04 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF
    X'  = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_1LC0RA

X' = f3's X with K's row replaced by C7's I (K0 = 1LC, K1 = 0RA). X' agrees with C04 until the first E0. C7's H is
X' J, C7's I is X' K, C7's G is X' I, C7's F0 = 1RG is X' F0,G,H0 (X' H is only entered from G and always reads 0).
Sim.v: port of f3/Sim.v (only K's two cases change; they now go to ordinary states C and A).

## What is reused unchanged (recompiled against the new Base.v; Idle, 2 coqc)

Base.v (new table), G_rules (champion rules R1, R2, R3 and the 00-gap variants R2z, R3z: E0-free), Abs (token family,
U, CDP, arrows, Bx, init_reach = 2369 C04 steps: literal check shows C7 has NO E0 before J1), KStep.v (= the generic
first part of f3's Step.v: Kx/Kgx with any far end, CDPx), Lift (D0f, maybe).
NOT reusable: every C04 cascade lemma (G_sub*, G_stop, G_entry, G_p14/20, K31, Endgame). Literal check: C04/M8 cascade
sub-steps DO contain E0 events (left cell 1), which C7 resolves differently (H0 = 0LI, I1 = 0RA). So the post-J11
cascade of C7 is C7's own and needs its own sub-step lemmas (only the 9 steps actually taken, at fixed residues).

## The run (literal checks so far, tools/c7sim.py, pkf8 --kt with an explicit far frame "0,0,")

  c0 -->* Kg(0^10++[2]) (Abs.init_reach), CDP -> Kt(1^11; 1; 3B+2; 0)                              [reused]
  Phase A (n = 1 mod 5): Kt(1^n;1;3R+2;t) (frame 11) -->+ CL [frame 1 | 1, K+5, 1^(K-1)] t+2, K = (27R+3n+10)/5
     CHECKED for J1 (B = 6..366, 10 values) and n = 16,21,26 (R = 16, 41).  Contains a far-left transfer loop
     (H0 with blank left, I0 = 1LC, about R rounds) and two H0 events with left cell 1 (I1 = 0RA).
  clear (CDPx, depth K-2, digit (K+4)/3) -> Kx(1^(K-1) ++ [1]; 1; 3R'+2; t+2; e1)
  Phase B (E0-free, f3's XREB2 generalised): Kx(1^n ++ [1];1;3R+2;t;e1) -->+ CL Kt(1^(K'-1) ++ [7];1;2;t) frame 11,
     K' = 12R + n + 5.  CHECKED (n = 40, 94; R = 6, 16, 21, 41), no H0 event.
  clear digit 2 -> Kt(1^K'; 1; 3R''+2; t)
  J1, J3 use phase A (n = 11, n3 = 1 mod 5 for the real residue), J5 uses
  Phase C (n = 3 mod 5): Kt(1^n;1;3R+2;t) -->+ CL [frame 11 | 1, 7, gap 00, K-12, 1^K] t+2, K = (27R+3n+44)/5
     CHECKED (n = 13; R = 16, 41).
  clear (digit (K-13)/3 at depth K-1, far end = gap 00) -> Kx(1^K; 1; 3R5+2; t; 00 7 1 11)
  Phase D (E0-free): -> CL [0*3 | 6R5+12, 7, 1^(K-2)]   CHECKED (R = 16, K = 103).
  Counter loop (E0-free, by induction): token C = 6R5+12 drops by 3 per round, each round deposits 6R+7 (a digit)
     and clears it at depth K-2 (CDPx): about 2 R5 rounds.  CHECKED qualitatively (8 rounds).  One lemma by
     induction on the round count (like C04's K31 COUNT).
  End of counter (C = 3 -> 0 -> frame consumed, literal check from C = 6): the far frame is eaten, then
     CL [X | 1^(L0)] with NO frame (far end blank) -> clear -> Kx(1^L0; 1; 3R10+2; t; blank).
  Post-J11 exhaustion with blank far end: a C7-specific cascade (deposits of tokens ~ 3/5 of the previous at the
     far left, one H0 event with left cell 1 per sub-step).  TO BE CHARACTERISED NEXT (moment shape, sub-step map
     per residue class); then 8 sub-step lemmas + the stop/halt lemma at the residues of the real orbit.

## New Coq lemmas (generated with mexp retargeted to X', gen/ = copy of f3's gen with TM = X')

1. PA (phase A, parametric in R = 5q+1, n = 5k+1, t), PB (phase B), PC (phase C), PD (phase D), PCNT (one counter
   round) + COUNT (induction), PEND (counter end / frame consumption), PE (post-J11 entry), PS1..PS8 (cascade
   sub-steps at the orbit's residues), PH (stop branch and halt).
2. Residues: every accumulator R satisfies 2R+4 = 2^^(tall); need R mod 5^10 (or 5^11) and mod 2^a 3^b. Coq lemma:
   2^(4*5^(k-1)) = 1 mod 5^k (lifting the exponent by induction on k), hence towers of height >= k+3 are constant
   mod 5^k; generalises f3's U_mod50.  The checker (bb9_c7check) has flagged a discrepancy in L0's residue
   (8136900 vs the claimed 23806525 mod 5^10): to be settled by the exact phase formulas derived here.
3. Score: halt after the 9th sub-step, ones >= 24 R10-ish; chain R10 > U_{K6}(R5) > ... > f_w^5(5B) in the f/f_omega
   notation of Defs.v; vs M8's upper bound f_omega(f_omega(6*arrow 13 2 3 + 3)).
4. Sim.v (C7 <-> X'), Statement.v, probe.v (table eq_refl vs string, Print Assumptions closed).

Compute: the reused files are small (Base, G_rules, Abs ~ 5 min); the new generated lemmas dominate (each 5-60 min).
Risk: the cascade (unknown shape yet), the residue discrepancy, and phases with many H0 events (mexp transfer loops).

## Update 2026-10-22 03:00 (the plan as executed)

Run decomposition (each arrow one generated mexp lemma unless marked; x/dev files):
  c0 ->* Kx(1^11;1;3B+2;0;e11) (Abs) -> pa1 -> M1n (9B-9) -> pa2 -> clear R1 -> pbab, pbc -> clear R2 -> pa1 -> pa2 ->
  clear R3 -> pb -> clear R4 -> pa1 -> pc2 -> clear R5 -> pd -> counter [count_loop, by induction: KR3 + CDPx] ->
  count_end [r30, e2, e3 + clears] -> Kx(1^N;1;3R10+2;6;blank), N = 3j3+19 = 5m -> entry1 -> sub3, sub0, sub3, sub4,
  sub0, sub0, sub3 -> D0f 23 (15u+17) (12R10-32) 2 (J8+13) l -> r2a1 -> pre -> rounds [u x rnd, by induction] -> VH (halt).
  C7Arith (generated): with every accumulator = rho mod 2^5 3^4 5^14 (Res.v), all divisions exact and u = 5jj+2.
  C7Score: f_omega^2 (12B+27) < R3, f_omega^4 (12B+27) < R5 <= R10 <= ones at the halt.
Statement (c7/Statement.v): c7_table, c7_halts, c7_lower (f_omega^4 (6*arrow 13 2 3 + 3) < N), c7_beats_m8_bound.
Lessons: mexp needs single-variable loops (split phases where a loop runs over a sum of two runs), concrete s/t/p
where small values behave differently, and targets in the syntactic form the run reaches (Coq's finish_norm).
