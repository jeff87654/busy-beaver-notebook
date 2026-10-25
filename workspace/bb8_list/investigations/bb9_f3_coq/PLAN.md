# PLAN: Coq proof for f3_0RC (bb9_f3_coq)

f3 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_0RC1RF (9 states, H1 the halt).

## Architecture: an auxiliary 11-state machine X, then a simulation down to f3

    C04 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF
    X   = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_0RC1RH   (states A..K)

X is C04 with E0 = 1LH replaced by an inspection of the cell left of H: E0 = 1LJ; J1 = halt (C04's H1 halt);
J0 = 0LK; K1 = 1RH (back in H at x with C04's tape: 3 X steps = C04's one E0 step); K0 = 0RC (f3's I0, the new
behaviour). So X agrees with C04 step for step, and configuration for configuration, except that each E0 with
H reading 0 takes 3 steps, and at a "bad" E0 (left cell 0: the top-level exhaustions) X does f3's I0 = 0RC.

* f3 is simulated by X with the same tape (f3 F0 = 1RG <-> X F0,G,H0; f3 H0,I1 <-> X J0,K1; f3 G <-> X I,
  f3 H <-> X J, f3 I <-> X K; f3's F reading 0 after I1 <-> X's H reading 0). A Sim.v like M8's gives
  f3_halts from X's halting and transfers every ones count both ways (determinism + halted_unique).
* The C04 development is reused against X: the busycoq instance becomes 11 states (lib/BB112.v, Individual112.v)
  and Base.v redefines the tactic `step` as ONE C04 step (3 raw X steps at E0+J0+K1). The generated proof scripts
  (`do n step`, `execute`, `follow`) then compile UNCHANGED; the only textual edit is the halting state H -> J.
  Already checked (compiled, exit 0): G_rules, G_end, K_rf, K_x, Abs (incl. init_reach = 2369 C04 steps).

## Reused from C04 (copied; machine files ported mechanically, abstract files lightly edited)

G_rules, G_sub2..5, G_stop, G_entry, G_p14_*, G_p20_*, G_end, K_rf, K_x, K_e1, K_e2 (machine);
Abs, Lift, Orbit, Cascade, Step (minus its C04 top: ATE/AT1/reach_top), CBtail, Fin, Endgame, K31_Abs/Mach/End,
Score, FArith-type arithmetic (abstract). NOT reused: G_reb1, G_top, Chain (C04's top-level exhaustions: these are
exactly X's bad events). Endgame/Fin/ScoreEnd are generalized from C04's constant Pm/L1 to parameters.

## New lemmas (machine lemmas generated with C04's mexp generator, retargeted to X)

1. P1 = XREB1: Kt(1^11;1;3B+2;0) -->+ [frame "0 1", 6B-2, 13 | 1*5 ; r=2], t=3 (parametric in B, like C04's
   REBUILD1; one bad E0 = K0 at the far left). Then CDP clears 13 and 6B-2 at depth 5..7 -> R''.
   Est: generation 1-2 h, compile ~15 min.
2. P2 = XREB2: the frame-"0 1" exhaustion [0 1 1*8 ; 3R''+2] ->* [0,0,7 | 1*(12R''+11) ; 2] (no E0; a rebuild like
   REBUILD1, parametric in R''), then CDP of the digit 7 -> R2' (2R2'+4 = 2^^(12R''+12) 4). Est: 1-2 h.
3. P3 = XTE + XT1: top entry through K0 from Kt(1^n;1;3R2'+2;3), n = 12R''+12, to a D0 moment at sketch
   L00 = 3n+1, then the first sub-step with r = 3 at small parked count (C04's TOP1 analogue for residue 3),
   producing the parked list; then C04's AbsSTOP (L1 = 0 mod 5), CDPx, AbsENTRY -> D0f at L0' = (324R''-359)/25.
   Est: 2-3 h.
4. Residues: arrow_mod25 (2R+4 = 2^(2^g), 4 | g => = 11 mod 25), so R'' = 16 mod 25, even, 0 mod 3; hence
   r(L00) = 3, L1 = 0 mod 5, L0' integer, odd, = 1 mod 3. Est: 1 h.
5. Hookup: reach_top' : reachP Pm' L1' (and reachF for the score), then casc_stepP + cascade_from_start +
   casc_key (keys 31/37/43/49/55, K31 end) unchanged => X halts => f3_halts. Est: 2-3 h.
6. Score: ScoreEnd/ScoreK chain with K >= 11 R2' (instead of 11 R2(Bx)) =>
   N > f_omega (f_omega (12 R'' + c)) and R'' >= 2^^9(2B) => N > f_omega (f_omega (6 * arrow 13 2 3 + 3))
   (M8's Statement.v upper bound); plus the direct comparison with M8's ones count (importing M8's compiled
   Statement from a byte-identical compiled tree, if its busycoq .vo match). Est: 3-4 h.
7. Sim.v (f3 <-> X), probe.v (table vs the literal string, Print Assumptions Closed). Est: 1-2 h.

Compute: the reused machine files are ~8 CPU-h at Idle (C04's record: 29,000 s); with 3 parallel coqc about
3-4 h wall, started early and frozen (no Base.v change after that). Risk: a reused lemma whose X run needs the
cell left of a non-bad E0 when C04's lemma left it symbolic (none so far in 5 files); fixed per lemma.
