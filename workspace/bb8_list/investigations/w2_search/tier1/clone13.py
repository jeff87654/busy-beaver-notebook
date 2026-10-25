"""clone13.py MACHINE [--k 17 --n 41 --stages 220 --xs base]: clone-split halt search.  For each eater slot X (J0 and the
new states' slots; with --xs all also every base slot) redirect X -> fresh state Z (keep X's write/move); Z = copy of
X's target T with one slot undefined (the halt), either a plain copy (T-references kept) or a self-clone (T -> Z).
Each variant is followed from far_k + [0 1^n|1|19]; prints variants that halt after >= 1 restart (round boundary)."""
import sys, threading, argparse
from t1lib import run, start_word, far_of, rsig
QS = 'ABCDEFGHIJKLMNOP'
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--k', type=int, default=17)
ap.add_argument('--n', type=int, default=41); ap.add_argument('--stages', type=int, default=220); ap.add_argument('--xs', default='eater')
ap.add_argument('--all', action='store_true')
a = ap.parse_args()
def follow(M):
    rs = []
    def cb(st, kind, d):
        if kind == 'K':
            s = rsig(d[0][:-2])
            if s and not d[1] and s[1] >= 40: rs.append(f'c={s[1]}(d={s[1]-79},%42={s[1]%42},P={len(s[0])})@{st}')
    kind, st, d, v = run(M, start_word([0] + [1] * a.n + [1, 19], far_of(a.k)), a.stages, cb=cb)
    return kind, st, d, rs
def go():
    parts = a.machine.split('_'); ns = len(parts); Z = QS[ns]
    xs = [(9, 0)] + [(q, s) for q in range(10, ns) for s in (0, 1)]
    if a.xs == 'all': xs = [(q, s) for q in range(ns) for s in (0, 1)]
    for qi, s in xs:
        e = parts[qi][3*s:3*s+3]
        if e == '---': continue
        T = QS.index(e[2]); tp = parts[T]
        for kind_c in ('copy', 'self'):
            zt = tp if kind_c == 'copy' else tp.replace(e[2], Z)
            if kind_c == 'self' and zt == tp: continue
            for hs in (0, 1):
                zz = zt[:3*hs] + '---' + zt[3*hs+3:]
                p = list(parts); p[qi] = p[qi][:3*s] + e[:2] + Z + p[qi][3*s+3:]
                M = '_'.join(p + [zz])
                k, st, d, rs = follow(M)
                tag = 'HIT' if (k == 'H' and rs) else '   '
                if a.all or rs:
                    print(f'{tag} X={QS[qi]}{s} {kind_c} halt={Z}{hs}: {k} st={st} {d[:2] if k == "H" else ""} rounds={len(rs)} {" ".join(rs)} | {M}', flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
