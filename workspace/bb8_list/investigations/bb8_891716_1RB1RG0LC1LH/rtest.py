import random, subprocess, re, sys
from absys import step
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
cases = []
for par in 'oe':
    for n in range(0, 6):
        for _ in range(60):
            ds = [random.choice([0, 0, 1, 2, 3, 4]) for _ in range(n)]
            a = random.choice([0, 0, 0, 1, 2, 3]); b = random.choice([0, 1, 2, 3, 5, 8])
            cases.append((par, ds, a, b))
# exhaustive small
import itertools
for par in 'oe':
    for n in range(0, 4):
        for ds in itertools.product(range(0, 3), repeat=n):
            for a in (0, 1):
                for b in (0, 1, 2, 3):
                    cases.append((par, list(ds), a, b))
lines = []
for par, ds, a, b in cases:
    lines.append('%s:%s|%d|%d' % (par, ','.join(map(str, ds)), a, b))
res = subprocess.run(['./ksim.exe', 'step', '200000000'], input='\n'.join(lines) + '\n', capture_output=True, text=True).stdout.splitlines()
bad = 0; halts = 0; tmo = 0; ok = 0
for (par, ds, a, b), line in zip(cases, res):
    nxt = step(par, ds, a, b)
    m = re.match(r'.* => (HALT|T|K([oe])\(([\d,]*); (\d+); (\d+)\)).*', line)
    if m.group(1) == 'HALT':
        if nxt is None: halts += 1
        else: bad += 1; print('lit HALT, abs', nxt, 'for', par, ds, a, b)
        continue
    if m.group(1) == 'T':
        tmo += 1; print('T', par, ds, a, b); continue
    lit = (m.group(2), [int(x) for x in m.group(3).split(',') if x], int(m.group(4)), int(m.group(5)))
    if nxt is None or (nxt[0], nxt[1], nxt[2], nxt[3]) != lit:
        bad += 1; print('MISMATCH', par, ds, a, b, 'abs', nxt, 'lit', lit)
    else: ok += 1
print('cases', len(cases), 'ok', ok, 'both halt', halts, 'timeouts', tmo, 'mismatches', bad)
