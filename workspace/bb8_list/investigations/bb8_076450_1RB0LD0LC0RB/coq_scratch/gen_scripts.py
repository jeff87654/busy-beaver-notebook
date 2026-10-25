"""Generate busycoq proof scripts for the rules R1, R2, R3 with the planner (full tapes)."""
from explore import *

Dd = {'d': 1}
print('#### R1: P a (S (S b)) c d t -->+ P (S a) (S b) c d t')
drive('R1', P(A1, B1, A2, Dd, TT, c={'b1': 2}), P(A1, B1, A2, Dd, TT, c={'a1': 1, 'b1': 1}))
print('#### R2: P (S a) 1 c (S (S d)) t -->+ P 1 (S (S (a + a))) (S c) (S d) t')
drive('R2', P(A1, Z, A2, Dd, TT, c={'a1': 1, 'b1': 1, 'b2': 2}), P(Z, {'a': 2}, A2, Dd, TT, c={'a1': 1, 'b1': 2, 'a2': 1, 'b2': 1}))
print('#### R3: P (S a) 1 c 1 t -->+ P 1 2 a (S (S (S (c + c)))) (S t)')
drive('R3', P(A1, Z, A2, Z, TT, c={'a1': 1, 'b1': 1, 'b2': 1}), P(Z, Z, A1, {'c': 2}, TT, c={'a1': 1, 'b1': 2, 'b2': 3, 't': 1}))
for nm, lm in sorted(LEMMAS.items()):
    print(nm, lm)
