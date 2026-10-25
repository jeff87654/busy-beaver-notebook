import sys, time
from fam import TM, parse, Sim, ST
from grid1 import rule
N = int(sys.argv[1])
s = Sim(TM, size=1<<20)
exp = None; nconf = 0; nr = {'R1':0,'R2':0,'R3':0,'R4':0}
t0 = time.time()
cur = None
while s.steps < N:
    if ST[s.state] == 'A' and s.pos == s.lo and s.tape[s.pos] == 0 and not any(s.tape[s.lo:s.pos]):
        w = ''.join(map(str, s.tape[s.pos+1:s.hi+1])).rstrip('0')
        r = parse(w[::-1])
        if r is not None and len(r) >= 2 and r[-1] % 2 == 1:
            L = r[:-2][::-1]; a = r[-2]; b = (r[-1]-1)//2
            got = (L, a, b)
            if exp is not None:
                if got != exp:
                    print('MISMATCH at step', s.steps, 'expected', exp, 'got', got); break
                nconf += 1
            # predicted successor
            p = rule(L, a, b)
            if p is None: print('no rule'); break
            if p[0] == 'R4':
                n = len(L); bb = p[2]
                p = ([1]*n + [0]*(2*bb+2), 1, 0); nr['R4'] += 1
            else:
                nr['R1' if a > 0 else ('R2' if L[0] > 0 else 'R3')] += 1
            exp = p
    if not s.step(): print('HALT', s.steps); break
print('steps', s.steps, 'family configs matched', nconf, nr, 'last', exp[0][:8] if exp else None, exp[1:] if exp else None, '%.0fs' % (time.time()-t0))
