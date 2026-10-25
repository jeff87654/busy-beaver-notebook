# Coq proof of the three-cycle sibling 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA (resume here)

Family Kf ds a r = 0^inf D(d_n)..D(d_1) D(a) D(r) (10)^4 F> 0^inf. Start-up: c0 -> Kf(1^34 7 | 1 | 0) in 6524 steps
(= Kg (0^34 2) [] 0 0, same champion values as 0LA: bf = U 34 (U 34 0)).

Machine pieces (gen_machine_fh.py; all explored by mexp, closing symbolically):
- FR1-FR3: champion rules on raw tokens (as 0LA).
- P0 (st0a.py): Kf(1^J|1|r) -> S1;  P0B: S1 (J+1) -> XH(J,1);  HOP_loop3 (hop.py XH, hand loop): zeros hop right one per round;
  P0C: XH(0,i) -> E0 (19 steps, E reading 0 = the BB(8) record halt).
- glue r = 3 + 5w; P0D (st0b.py): E0 -> MR(w) (first macro-round point, D9^4 made);
- MR1 (mr.py): MR(w+1, i, l) -> MR(w, i+8, D9^4 l): four rounds of stage 0 as ONE rule (the multi-round loop cannot be
  generalized by mexp because each round contains hop loops over its own runs); iterated in Coq (MR_iter).
- P0E: MR(0, i, l) -> Kf(1^(7+i) 7 6 8 l | 1 | 0).  => stage 0 ends at Kf(1^(2n+34) 7 6 8 9^n | 1 | 0) as in 0LA.
- champion: CDP, CLRS (6->3->0): b3 = U K (U K (U K 0)), K = 2n+35.
- ST2 (st2c.py): Kf(1^m 0 8 9 9 l | 1 | 11+r) -> Kf(1^(m+41) 3 (4+2r) 8 l | 1 | 0). The FINDING target with D4^(m+40)
  is a later champion snapshot; the third clearing is CLRS at depth K+41: B4 = U (K+41) 0.
- ST3E (st3e.py): Kf(1^M 0 (3+T) 8 9 l | 1 | r) -> Yc(T, 2r+5, M+2);  Y1 (st3y.py): Yc(T+1, a+2, z) -> Yc(T, a, z+2)
  (a >= 1), iterated in Coq (Y_iter);  ST3X (st3x.py c=3): Yc(0, 21+a, 3+5u) -> halt in I reading 0.
  Real: z = K + 12 b3 + 1 = 3 mod 5 (b3 = 16 mod 25), a = 6 B4 - 12 b3 + 26 >= 0 (B4 >= 2 b3 + 2).
- ones at the halt = 86 + 9u + a + 10 (n - 3)  (literal check: 129, 187 exact).

Coq assembly: gen_final_fh.py (abstract_fh_base.v.in + run_fh.v.in + arith_fh.v.in + main_fh.v.in);
gen_bound_fh.py (bound_fh.v.in built by mk_bound_tmpl.py from bound_fh_head/score + 0LA bound pieces).
Dev: dev/M.v (machine part, 955 KB), dev/A.v (abstract, imports Dev.M), dev/B.v (bound).
