"""rp.py ROW 'DS' b [nev] : macro probe in row coding (F from table). DS tokens: P (=M0 top), Mv, v, with ^k.
prints successive a=0 states (decoded) / raw runs for undecodable events between them (compressed)."""
import sys, subprocess
from drv import SIM, show
from gk import gruns, gword, vshow
import geng2 as G
ROWS = [l.split()[0] for l in open('rows16.txt') if l.strip()]
FT = {3: dict(Q='A', z=2, A0=0, B0=2, dl=0), 4: dict(Q='A', z=2, A0=0, B0=2, dl=0)}
def parse(s):
    ds = []
    for t in s.split():
        k = 1
        if '^' in t: t, k = t.split('^'); k = int(k)
        if t == 'P': d = (0, 1)
        elif t[0] == 'M': d = (int(t[1:]), 1)
        else: d = (int(t), 0)
        ds += [d] * k
    return ds
def dec34(runs):
    if len(runs) < 2: return None
    A, B = runs[-2], runs[-1] - 2
    if A % 2 or B < 0 or B % 2: return None
    return [(r // 2, r % 2) for r in runs[:-2]], A // 2, B // 2
def vs(ds):
    return show([2 * v + m for v, m in ds])
def probe(row, ds, b, nev=3, N=10**9, raw=False):
    F = dict(FT[row]); F.update(c2=0, c3=0, a3=0, c4=0, droptop=0)
    M = ROWS[row - 1]
    w = gword(G.enc(F, ds, 0, b), F['z'])
    p = subprocess.Popen([SIM, M, '1', F['Q'], w, str(len(w)), str(N), F['Q'], '100000000'], stdout=subprocess.PIPE, text=True)
    out = []; c = 0; lastraw = None
    for l in p.stdout:
        s = l.split(None, 2)
        if s[0] == 'H': out.append('HALT@%s' % s[1]); break
        if s[0] != 'E' or len(s) < 3: out.append(l.strip()[:30]); break
        runs, z = gruns(s[2])
        d = dec34(runs) if z == F['z'] else None
        if d is not None and d[1] == 0:
            out.append('%s: %s ;b=%d' % (s[1], vs(d[0]), d[2])); c += 1
            if c >= nev: p.kill(); break
        elif raw: out.append('[%s z%d %s]' % (s[1], z, vshow(runs)[:60]))
    return out
if __name__ == '__main__':
    row = int(sys.argv[1]); ds = parse(sys.argv[2]); b = int(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    raw = len(sys.argv) > 5
    print(' | '.join(probe(row, ds, b, n, raw=raw)))
