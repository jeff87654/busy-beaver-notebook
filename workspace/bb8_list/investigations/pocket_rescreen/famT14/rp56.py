"""rp56.py ROW 'DS' b [nev] [raw]: macro probe for rows 15/16. Coding (mirrored, event state B, z=1):
digit (v, mark): run 2v+1 if unmarked, 2v if marked; then A-run = 2a, B-run = 2b+2. a=0 events decoded."""
import sys, subprocess
from drv import SIM, show
from gk import gruns, gword, vshow
ROWS = [l.split()[0] for l in open('rows16.txt') if l.strip()]
def parse(s):
    ds = []
    for t in s.split():
        k = 1
        if '^' in t: t, k = t.split('^'); k = int(k)
        d = (int(t[1:]), 1) if t[0] == 'M' else (int(t), 0)
        ds += [d] * k
    return ds
def vs(ds):
    s = []; i = 0
    while i < len(ds):
        j = i
        while j < len(ds) and ds[j] == ds[i]: j += 1
        v, m = ds[i]; t = ('M%d' % v) if m else str(v)
        s.append(t if j - i == 1 else '%s^%d' % (t, j - i)); i = j
    return ' '.join(s)
def enc(ds, a, b):
    return [2 * v + (0 if m else 1) for v, m in ds] + [2 * a, 2 * b + 2]
def dec(runs):
    if len(runs) < 2: return None
    A, B = runs[-2], runs[-1] - 2
    if A % 2 or B < 0 or B % 2: return None
    return [(r // 2, 0 if r % 2 else 1) for r in runs[:-2]], A // 2, B // 2
def probe(row, ds, b, nev=3, N=10**9, raw=False, a=0):
    M = ROWS[row - 1]
    w = gword(enc(ds, a, b), 1)
    p = subprocess.Popen([SIM, M, '1', 'B', w, str(len(w)), str(N), 'B', '100000000'], stdout=subprocess.PIPE, text=True)
    out = []; c = 0
    for l in p.stdout:
        s = l.split(None, 2)
        if s[0] == 'H': out.append('HALT@%s' % s[1]); break
        if s[0] != 'E' or len(s) < 3: out.append(l.strip()[:30]); break
        runs, z = gruns(s[2])
        d = dec(runs) if z == 1 else None
        if d is not None and d[1] == 0:
            out.append('%s: %s ;b=%d' % (s[1], vs(d[0]), d[2])); c += 1
            if c >= nev: p.kill(); break
        elif raw: out.append('[%s z%d %s]' % (s[1], z, vshow(runs)[:60]))
    return out
if __name__ == '__main__':
    row = int(sys.argv[1]); ds = parse(sys.argv[2]); b = int(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    print(' | '.join(probe(row, ds, b, n, raw=len(sys.argv) > 5)))
