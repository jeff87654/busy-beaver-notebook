"""ucode.py: universal coding detection + literal macro probe for the 1RB1LG family.
coding C = dict(M, Q, z, A0, B0, dl): digit (v,mark): run 2v+dl if unmarked else 2v+1-dl; then runs A=A0 (a=0), B=2b+B0; trailing zeros z, head in Q."""
import subprocess
from collections import Counter
from drv import SIM
from gk import gruns, gword
def events(M, Q, N, maxev=200000, start='A', word='-', hp=0):
    p = subprocess.run([SIM, M, '1', start, word, str(hp), str(N), Q, str(maxev)], capture_output=True, text=True).stdout.splitlines()
    ev = []; tail = ''
    for l in p:
        s = l.split(None, 2)
        if s[0] == 'E' and len(s) == 3: ev.append((int(s[1]),) + gruns(s[2]))
        else: tail = l
    return ev, tail
def detect(M, Q, N=30000000):
    ev, tail = events(M, Q, N)
    if len(ev) < 50: return None, 'few events (%d)' % len(ev)
    z = Counter(e[2] for e in ev).most_common(1)[0][0]
    E = [e for e in ev if e[2] == z]
    Amin = Counter(); Bstart = Counter(); par = Counter(); chain = 0
    for (s1, r1, _), (s2, r2, _) in zip(E, E[1:]):
        if len(r1) >= 3 and len(r2) == len(r1) and r1[:-2] == r2[:-2] and r2[-2] == r1[-2] - 1 and r2[-1] == r1[-1] + 2:
            chain += 1
        elif len(r1) >= 3 and r1[:-2] != r2[:-2]:
            Amin[r1[-2]] += 1          # A value at the moment the digits change = a=0 value
            if len(r2) >= 2: Bstart[r2[-1]] += 1
        for r in r1[1:-2]: par[r % 2] += 1
    if chain < 20: return None, 'no a-phase chains (%d)' % chain
    A0 = Amin.most_common(1)[0][0] if Amin else 0
    B0 = min(Bstart) if Bstart else 0
    dl = 1 if par[1] > par[0] else 0
    return dict(M=M, Q=Q, z=z, A0=A0, B0=B0 % 2 if False else B0, dl=dl), 'ok chains=%d A0hist=%s Bstart=%s' % (chain, dict(Amin.most_common(3)), dict(Bstart.most_common(3)))
def enc(C, ds, b):
    r = [2 * v + (C['dl'] if m == 0 else 1 - C['dl']) for v, m in ds]
    if r and C.get('lo'): r[-1] += C['lo']
    return r + [C['A0'], 2 * b + C['B0']]
def dec(C, runs):
    if len(runs) < 2 or runs[-2] != C['A0']: return None
    B = runs[-1] - C['B0']
    if B < 0 or B % 2: return None
    ds = []
    rs = list(runs[:-2])
    if rs and C.get('lo'):
        rs[-1] -= C['lo']
        if rs[-1] < 0: return None
    for r in rs:
        par = r % 2; m = 0 if par == C['dl'] else 1
        v = (r - (C['dl'] if m == 0 else 1 - C['dl'])) // 2
        if v < 0: return None
        ds.append((v, m))
    return ds, B // 2
def chain_end(C, pv, r):
    """a=0 event reached at the end of an a-phase: previous event has same digit runs, A = A0+1, B = B-2"""
    if pv is None or pv[1] != C['z'] or len(r) < 2: return False
    q = pv[0]
    return len(q) == len(r) and q[:-2] == r[:-2] and q[-2] == C['A0'] + 1 and q[-1] == r[-1] - 2 and r[-2] == C['A0']
def lead_invisible(C):
    """a leading digit whose run is 0 is invisible on the tape"""
    return [(0, 0)] if C['dl'] == 0 else [(0, 1)]
def norm(C, ds):
    inv = (0, 0) if C['dl'] == 0 else (0, 1)
    i = 0
    while i < len(ds) and ds[i] == inv: i += 1
    return ds[i:]
def probe(C, ds, b, N=3 * 10**8, nev=1, maxev=4000, tmo=30):
    runs = enc(C, ds, b)
    w = gword(runs, C['z'])
    try:
        r = subprocess.run([SIM, C['M'], '1', C['Q'], w, str(len(w)), str(N), C['Q'], str(maxev)], capture_output=True, text=True, timeout=tmo).stdout.splitlines()
    except subprocess.TimeoutExpired:
        return [('T', 0)]
    out = []; prev = None
    for l in r:
        s = l.split(None, 2)
        if s[0] == 'H': out.append(('H', int(s[1]))); break
        if s[0] in ('END', 'TAPE'): out.append(('T', 0)); break
        if s[0] != 'E' or len(s) < 3: continue
        rr, z = gruns(s[2])
        pv = prev; prev = (rr, z)
        if z != C['z']: continue
        if not chain_end(C, pv, rr): continue
        d = dec(C, rr)
        if d is None: continue
        out.append((norm(C, d[0]), d[1]))
        if len(out) >= nev: break
    if not out: out.append(('T', 0))
    return out
