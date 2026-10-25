# PLAN: Coq proof for h003 (bb9_h003_coq)

h003 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC (9 states, H1 the halt).

## Architecture: auxiliary 11-state X3, simulation down to h003 (as f3 / C7)

    C04 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF
    X3  = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_1RK1RC

h003's H = X3 J, h003's I = X3 K, h003's G = X3 I, h003's F0 = 1RG = X3's F0, G, H0.  h/Sim.v = port of
bb9_c7_coq/c7/Sim.v (only K's two cases change: K0 = 1RK, K1 = 1RC).

KEY POINT (resync): at a good E0 event (T[e-2] = 1, T[e+1] = 1) C04 runs E0 H0 I1 F1 D0 A1 and X3 runs
E0 J0 K1 C0 D0 A1, six raw steps each, same configuration afterwards.  So Base.v defines [step] = ONE RAW step
(no macro), and every C04 generated script ([do n step], [follow], [execute]) that has only good E0 events replays
on X3 with the same counts.  Only textual edit: C04's halt (E0 writes 1, H reads 1) becomes X3's (E0 writes 0,
J reads 1): targets `<{{J}} (1 >> ...` -> `<{{J}} (0 >> ...` in G_end, K_x; ones counts in CBtail/K31_*/score
shift by one.  Risk: a window where X3 needs the cell e-2 while C04's script has it inside a symbolic power.

## Reused (copied, recompiled against X3's Base.v; Base.v FROZEN 2026-10-22 14:52)

From bb9_f3_coq/x (C04's tree already ported to the 11-state XL instance, Endgame generalised over Pm):
  dev: G_rules G_end G_sub2-5 G_stop G_entry G_p14_0-5 G_p20_0-5 Abs Orbit Lift Cascade Step CBtail Endgame Fin
  k31: K_rf K_x K_e1 K_e2 K31_Abs K31_Mach K31_End;  score: Score.v
From bb9_c7_coq/x: Res.v (every accumulator = rho mod 2^5 3^4 5^14), Ones.v, G_pbab + G_pbc (the E0-free
frame-1 rebuild PB: Kx(1^n ++ [1];1;3R+2;t;e1) -->+ Kt(1^(K'-1) ++ [7];1;2;t), K' = 12R+n+5), C7Score5 ideas
(fSS_le_U, chain lemmas), gen/ (mexp, retargeted to X3).
(C04's dev/G_top.v TOP1 is for D0f run 5J+30: not usable; XTOP1 for 5J+24 generated on X3 from f3's item.)

## The run (all literal-checked with tools/x3sim.py on X3, fake accumulators at the CL jumps)

  c0 -->* Kt(1^11;1;3B+2;0)                                   (Abs.run_to_exhaustion, E0-free)
  T1 (K = 1 mod 5): Kt(1^K;1;3R+2;t) -->+ Top(K'), K' = 12R + (9K+36)/5, t+3   [literal: via "0 3 1*(K'+1)", one R3]
     first use K = 11 -> K0 = 12B+27 (t = 3)
  T4 (K0 = 4 mod 5): -> CL "0 1 (6R+5) 2 z2 (Ka+7) 1*Ka" (t+3) [P4]; CDPx -> R_b;
     -> CL "0 1 (6R+4) (6R_b+10) 1*(Ka-1)" [P4b]; CDPx -> R_c; CDPx (v = 2R+1, j = Ka-1, b = R_c) -> R_d;
     PB (n = Ka) -> Top(12 R_d + (3K-2)/5)
  T3 (K1 = 3 mod 5): -> CL "0 1 (6R+1) (Kb+8) 1*Kb" (t+3) [P3]; CDPx -> R_b; CDPx (v = 2R, j = Kb) -> R_c;
     PB (n = Kb+1) -> Top(12 R_c + (3K+16)/5)
  T1 (K2), T1 (K3) -> Top(K4), K4 = 0 mod 5, t = 15
  exit: clear R_e = iter 2 (U (K4-1)) 0; TXa: Kt(1^K;1;3R+2;t) -->+ D0f (t+1) (3K-1) 2 1 (6R+3) blank
     (contains the bad far-left event; literal K = 15..45, R = 6, 16, t = 0, 3, 6); then XTOP1 (3K-1 = 5J+24; NOT C04's
     TOP1, which is for the run 5J+30: regenerated f3's XTOP1 item on X3, G_xt1.v)
     -> D0f (t+4) (3J+2) (12R+17) 0 (J+6) blank = reachF Pm L1 with L1 = 3J+1 (odd since K4 odd, = 1 mod 3),
     Pm = 12R+17-L1; then f3's halts_from_reach (cascade_from_start + casc_key + K31 end) unchanged.
  Residues (Res.v): K0..K4 mod 5 = 4,3,1,1,0, exact divisions, K4 odd; C7Arith-style generated arithmetic.

## New generated lemmas (mexp on X3, gen/): P1 (=T1, maybe split), P3, P4, P4b, TXa (maybe split), TOP1 (port).

## Score
f3's XScore (casc_keyS): N > f_omega (f_omega a) for every a <= depth of R_e's clear (K4 - 1).  Top chain:
each top's first clear is iter 2 (U (K_i - 1)) 0 and K_(i+1) >= 12 R_a, so f_omega^4 (12B+26) <= K4 - 1 (C7Score5
style: "x + 1 <= depth -> f_omega x < U depth 0").  Goal: h003_lower : f_omega^6 (6 * arrow 13 2 3 + 2) < N
(6 arrow 13 2 3 + 2 = 12B+26), corollary f_omega^7 12 < N (fw12_le_Bx), and > M8's upper bound
f_omega^2 (6 * arrow 13 2 3 + 3).

## Files to write
x/dev: HTop.v (top lemmas restated on Kx/Kgx, T1/T3/T4/TX, the orbit), HArith.v (generated residues), HFinal.v
(x_halts), HScore.v (from XScore); h/: Defs.v, Sim.v, Final.v, Statement.v (h003_table parser, h003_halts,
h003_lower, h003_lower7_12, h003_beats_m8_bound), probe.v.

## Compute budget
Ported machine files: ~8 CPU-h at Idle (C04 record 29,000 s), 3 coqc -> ~3-4 h wall, started 14:53.
New generated lemmas: 5-6 files, each 5-60 min compile + mexp generation 10-60 min.  Hand files small.
Total estimate: 8-12 h wall.
