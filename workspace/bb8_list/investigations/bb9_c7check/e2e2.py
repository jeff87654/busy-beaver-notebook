# e2e2.py: continuation of the end-to-end world (runs/e2e_bad_ctxgap.txt J1..J5 are valid: J5 = "0*2 1 7 z2 457355641
# 1*457355653", K6 = 457355653, n = K6-3 = real n mod 6*5^10) from the CL of J5 with R5 = 6, using the fixed c7m90f.
import idle
from chain import chain
def pol(i, r):
    if r['view'].startswith('0 2 z2 ') or r['ctx'] == '': return 2124366
    return 366
print('# e2e continuation from J5 (R5=6): counter R=366, exit/R10 = 2124366', flush=True)
chain('0*2,1,7,z2,1*457355653;1;20;6', [], pol, 400, log=lambda s: print(s[:900], flush=True))
