# cal_s55_1RB1RC: 1RB1RC_0RC0LB_0RD1RF_1LE1LD_1RC1LG_1LD1RA_1LA0LH_---1LG

Calibration run (Sonnet 5.5, blind). Halting transition: H0.

## Verdict
Never halts. Confidence: proved (Coq PASS): `bb8_list/proofs/CAL_S55_1RB1RC.v`, `python check.py CAL_S55_1RB1RC.v` -> PASS (~20 s).

## Mechanism
Tape (head D at the left end, blank to the left): 1^6 0^b (10)^m 1^5. A round (D0 1LE, E0 1RC, C/F/A sweep over the 1s, F0 1LD, D sweep back)
turns 1^a 0^b into 1^(a+3) 0^(b-1) provided a = 0 mod 3. After b rounds the zero run is used up and a = 3b+7 = 1 mod 3, so the next sweep ends in
A0 1RB; B then erases everything (B1 0LB) and the builder restarts, giving
  R1: F(b, m+2) -->+ F(3b+8, m)         (F(b,m) = 1^6 0^b (10)^m 1^5)
When m = 0 the ones are all consumed (b = 4c+2 always) and a G/H sweep (G1 0LH, H1 1LG) converts 1^(2j+1) into (10)^j:
  R2: F(4c+2, 0) -->+ F(2, 6c+10)
With D(n,c) = F(4c+2, 2n): D(n+1,c) -->+ D(n,3c+3) and D(0,c) -->+ D(3c+5,0); b = 2 mod 4 and m even are preserved, so no halting ending
occurs. Blank tape reaches D(2,0) in 111 steps. Growth is tetration-rate (b -> 3b+8 per two units of m, m resets to ~1.5 b).

## Verification
All rules are Coq lemmas (round, special, endA, stage2, stage3, R1, R2, Dn_step, init_reach), no axioms. Numeric cross-check with `cal_s55_1RB1RC/sim.py`, `snap3.py`
(events (6,2,4)->(6,14,2)->(6,50,0)->(6,2,82) matched b->3b+8, m->(3b+14)/2).
Not a record candidate (never halts). Scratch: `cal_s55_1RB1RC/` (T1_scratch.v is the development file).
