# hs68.py: small-config halting search in the F68 grammar: A in 0..9, list length 1..4, digits 0..3 (c=-1).
# For each config: literal kl2 run (2e6 steps): HALT? ; engine run with D-acceleration: does it ever apply a rule
# below its exact validity threshold (B_j/T_j need A >= j-1)?  Claim tested: literal halt => engine path unsafe.
import itertools, json
from lit68 import KL, M, content
import subprocess
def eng_unsafe(A, L, maxev=60, cap=10**7):
    L = list(L)
    for _ in range(maxev):
        A += 2 * L[0]; L[0] = 0
        if A > cap: return None
        j = 1
        while j < len(L) and L[j] == 0: j += 1
        if j < len(L):
            if A < j - 1: return ('B%d' % j, A)
            L[:j] = [1] * (j - 1) + [A + 3 - j]; L[j] -= 1; A = 1
        elif len(L) == 1:
            if A + 4 > 10**5: return None
            L = [1] * (A + 4); A = 1
        else:
            j = len(L) - 1
            if A < j - 1: return ('T%d' % j, A)
            L = [1] * (j - 1) + [A + 2 - j]; A = 1
        if max(L) > cap: return None
    return None
res = {'n': 0, 'halt': 0, 'halt_safe': [], 'unsafe_nohalt': 0, 'halts': []}
for A in range(10):
    for n in range(1, 5):
        for L in itertools.product(range(4), repeat=n):
            st = (A, L, -1); res['n'] += 1
            p = subprocess.run([KL, M, '2000000', 'D', 'L', 'a', 'D00' + content(st)], capture_output=True, text=True)
            h = p.stdout.strip().splitlines()[-1].startswith('HALT')
            u = eng_unsafe(A, L)
            if h:
                res['halt'] += 1; res['halts'].append((A, L, u))
                if u is None: res['halt_safe'].append((A, L))
            elif u is not None: res['unsafe_nohalt'] += 1
print('configs', res['n'], 'literal halts', res['halt'], 'halts with SAFE engine path', len(res['halt_safe']), res['halt_safe'][:10],
      'unsafe-but-no-halt-in-2e6', res['unsafe_nohalt'])
print('sample halts', res['halts'][:8])
json.dump(res, open('hs68.json', 'w'))
