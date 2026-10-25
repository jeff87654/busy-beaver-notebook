# exitR.py: the counter-exit exhaustion Kt(0,2,z2,1^(K-2);1;3R+2;6) for K in the real class (mod 6*5^9) and R in
# various residue classes: which first stop does it take?
import idle
from gm import run
from towmod import Rres
K = 324403
out = []
for k in (2, 3, 4, 5, 6):
    rr = Rres(5**k)
    for m in (0, 1, 2):
        R = rr + m * 5**k
        if R < 50: R += 5**k * 3
        r = run(f'0,2,z2,1*{K-2};1;{3*R+2};6')
        print(f'R={R} (= real mod 5^{k}, R mod 5^{k+1} = {R % 5**(k+1)} vs real {Rres(5**(k+1))}) ->', r['kind'], r.get('view', r.get('tape', ''))[:200], flush=True)
