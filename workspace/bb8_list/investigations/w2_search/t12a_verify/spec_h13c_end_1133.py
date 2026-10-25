M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1LK0LL_0LM0LA_0LJ---'
# H13c round-2 end = Per (prefix) k2 6 X15 | U14 (tdrive_h13c stage 23 CLR output).  True order:
# k1 << P (U5 = iter 2 (U (w+11)) 4) << k2 (4/21 U4, U4 = huge-d clear) << X15 (round-2 depth) << U16 << U17 << U14
START = "2^(k1-12) 1 7 z4 0 z5 1 z3 0^3 z2 0 z2 0 10 0^3 (U5+1) 2^(4/21*U4-55/21) 5 1^6 0^2 2 1^(X15) 0 (U14)"
ATOMS_SPEC = {'k1': (166054000337, 523069747200, 1000), 'U5': (2382873489400, 4707627724800, 1003),
  'U4': (2382873489400, 4707627724800, 1004), 'X15': (1133, 2520, 1015), 'U14': (2382873489400, 4707627724800, 1030)}
OVERRIDE = [(r'CLR d=3 n=\(X15', 1020), (r'CLR d=2 n=\(X15', 1025)]   # U16 = iter 3 (U X15) 4 < U17 = iter 2 (U X15) 4 < U14
MAXST = 6
