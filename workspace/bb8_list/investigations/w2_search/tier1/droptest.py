"""droptest.py MACHINE [--k 17 --n 41 --stages 220]: for the machine and each variant with one of its J0/new-state slots
made undefined, follow from far_k + [0 1^n|1|19] and report restarts (c, delta) and where it halts."""
import sys, threading, argparse
from t1lib import run, start_word, far_of, rsig
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--k', type=int, default=17)
ap.add_argument('--n', type=int, default=41); ap.add_argument('--stages', type=int, default=220); ap.add_argument('--R', type=int, default=19)
ap.add_argument('--nodrop', action='store_true'); ap.add_argument('--policy', default='std')
a = ap.parse_args()
def follow(M):
    rs = []
    def cb(st, kind, d):
        if kind == 'K':
            s = rsig(d[0][:-2])
            if s and not d[1] and s[1] >= 40: rs.append(f'c={s[1]}(d={s[1]-79},%14={s[1]%14},%42={s[1]%42},P={len(s[0])})@{st}')
    kind, st, d, v = run(M, start_word([0] + [1] * a.n + [1, a.R], far_of(a.k)), a.stages, cb=cb, policy=a.policy)
    return f'{kind} st={st} {d[:2] if kind == "H" else ""} rounds={len(rs)} ' + ' '.join(rs)
def go():
    print('BASE', follow(a.machine), flush=True)
    if a.nodrop: return
    parts = a.machine.split('_')
    for qi in [9] + list(range(10, len(parts))):
        for s in (0, 1):
            if qi == 9 and s == 1: continue
            p = list(parts); e = p[qi]
            if e[3*s:3*s+3] == '---': continue
            p[qi] = e[:3*s] + '---' + e[3*s+3:]
            print(f'drop {"ABCDEFGHIJKLMNOP"[qi]}{s}:', follow('_'.join(p)), flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
