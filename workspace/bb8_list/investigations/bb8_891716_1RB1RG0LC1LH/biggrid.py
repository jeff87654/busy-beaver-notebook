import subprocess, re, sys, itertools
from absys import step
cases = []
for par in 'oe':
    for k in (0, 1, 2, 3, 7, 20, 41):
        for b in (0, 1, 2, 5, 17, 40):
            for y1 in (1, 2, 4):
                for far in ([], [0], [3, 1]):
                    cases.append((par, far + [y1] + [0] * k, 0, b))      # R23, y+1 = y1, k zeros, with prefix 'far'
    for n in (0, 1, 2, 3, 9, 25, 40):
        for b in (0, 1, 2, 6, 19, 40):
            cases.append((par, [0] * n, 0, b))                              # exhausted list: Conv (o) / Final (e)
    for a in (1, 2, 7):
        for b in (0, 3, 30):
            cases.append((par, [2, 0, 1], a, b))                            # R1
lines = ['%s:%s|%d|%d' % (par, ','.join(map(str, ds)), a, b) for par, ds, a, b in cases]
res = subprocess.run(['./ksim.exe', 'step', '3000000000'], input='\n'.join(lines) + '\n', capture_output=True, text=True).stdout.splitlines()
ok = bad = hl = 0
cost = {}
for (par, ds, a, b), line in zip(cases, res):
    nxt = step(par, ds, a, b)
    m = re.match(r'.* => (HALT|T|K([oe])\(([\d,]*); (\d+); (\d+)\)) after (\d+) steps', line)
    if m.group(1) == 'HALT':
        if nxt is None: hl += 1
        else: bad += 1; print('lit HALT, abs', nxt, par, ds, a, b)
        continue
    if m.group(1) == 'T': bad += 1; print('T', par, ds[:5], a, b); continue
    lit = (m.group(2), [int(x) for x in m.group(3).split(',') if x], int(m.group(4)), int(m.group(5)))
    if nxt is None or tuple(nxt[:2]) + tuple(nxt[2:]) != lit: bad += 1; print('MISMATCH', par, ds, a, b, nxt, lit)
    else: ok += 1
    # record cost for R23 shape / exhausted shape
    if a == 0:
        nz = [d for d in ds if d]
        key = ('R23' if nz else ('Conv' if par == 'o' else 'Fin'), par)
        n = len(ds); k = (len(ds) - 1 - max(i for i, d in enumerate(ds) if d)) if nz else n
        cost.setdefault(key, []).append((k, b, int(m.group(6))))
print('cases', len(cases), 'ok', ok, 'both halt', hl, 'bad', bad)

F = {('R23','o'): lambda k,b: (4*k+26)*b + 8*k + 40, ('R23','e'): None,
     ('Conv','o'): lambda n,b: (4*n+24)*b + 4*n + 19, ('Fin','e'): lambda m,b: (4*m+22)*b + 8*m + 32}
for key, v in sorted(cost.items()):
    f = F.get(key)
    if f is None:
        print(key, 'sample', v[:4]); continue
    errs = [(k, b, c, f(k, b)) for k, b, c in v if f(k, b) != c]
    print(key, 'n=%d' % len(v), 'formula mismatches:', len(errs), errs[:3])
