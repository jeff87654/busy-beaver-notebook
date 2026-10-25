# e2e.py: END-TO-END world from the CL moment J1 (Kt([1]^11 ++ [0;0]; 1; 3B+2; 0), reached from blank at step 2117) to the
# halt, with exact simulation (c7m90f) between CLs.  B = R1 = R2 = R3 = 366 (real mod 18000: all branch conditions as in
# the real run), R4 = 84694356 chosen so that n = K6-3 = real n mod 6*5^10, R5 = 6 (counter C = 48), counter CLs 366,
# the CL feeding EXIT and R10 = 2124366 (real mod 3150000, parked list >> consumption).
import idle
from chain import chain
B = 366
fixed = [366, 366, 366, 84694356, 6]
def pol(i, r):
    if i < len(fixed): return fixed[i]
    if r['view'].startswith('0 2 z2 ') or r['ctx'] == '': return 2124366
    return 366
print('# e2e world: B=366, R1..R3=366, R4=84694356, R5=6, counter R=366, exit/R10 = 2124366', flush=True)
chain(f'0,0,1*11;1;{3*B+2};0', [], pol, 400, log=lambda s: print(s[:900], flush=True))
