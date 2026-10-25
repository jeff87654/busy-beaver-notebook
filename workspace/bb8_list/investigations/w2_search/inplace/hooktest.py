"""hooktest.py M GRAM [--ks ..]: build the clone-split chain that halts exactly when the slot-read k-gram GRAM
(e.g. 'L1,K1' or 'L0,J1,C1') occurs, then follow it: std at k = 17,29,41 (RSIGs + outcome), and big at k = 17 with
the counter trimmed (ctrim) to reach the round-2 end.  usage: python hooktest.py M L1,K1 [--S 160] [--big]"""
import sys, threading, argparse
from ilib import stage, rsig, far_of, word_of, SUF
QS = 'ABCDEFGHIJKLMNOP'
def parse(M): return [[M.split('_')[q][3*s:3*s+3] for s in (0, 1)] for q in range(len(M.split('_')))]
def unparse(T): return '_'.join(a + b for a, b in T)
def build(M, gram):
    T = parse(M); g = [(QS.index(x[0]), int(x[1])) for x in gram.split(',')]
    prev = g[0]
    for i in range(1, len(g)):
        q, s = g[i]
        new = len(T); T.append(list(T[q]))            # clone of q
        e = T[prev[0]][prev[1]]
        assert e[2] == QS[q], f'gram break: {QS[prev[0]]}{prev[1]} -> {e} not {QS[q]}'
        T[prev[0]][prev[1]] = e[:2] + QS[new]
        if i == len(g) - 1: T[new][s] = '---'
        prev = (new, s)
    return unparse(T)
def run(M, k, pol, S, ctrim=0, maxs=10**9, n=329, real=False):
    head, state = None, 'G'
    if real:
        from ilib import real_start
        word, head, state = real_start(6)
    else:
        word = far_of(k) + word_of([0] + [1] * n + [1, 19]) + SUF
    rs = []
    for st in range(S):
        kind, d = stage(M, word, maxs, pol, ctrim=ctrim, head=head, state=state); head, state = None, 'G'
        if kind != 'K': return f'{kind}{d.get("slot","")}@{st}', rs
        r = rsig(d['toks'])
        if r and st > 0 and (not rs or st - rs[-1][0] > 3): rs.append((st, len(r[0]), r[1], r[2]))
        word = d['newword']
    return 'MAX', rs
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('gram'); ap.add_argument('--S', type=int, default=160)
    ap.add_argument('--ks', default='17,29,41'); ap.add_argument('--big', action='store_true'); ap.add_argument('--bigks', default='17'); ap.add_argument('--n', type=int, default=329); ap.add_argument('--real', action='store_true'); ap.add_argument('--bign', type=int, default=329); ap.add_argument('--ctrim', type=int, default=126); ap.add_argument('--nostd', action='store_true')
    a = ap.parse_args()
    def go():
        H = build(a.M, a.gram); print(H, flush=True)
        if a.real:
            for pol in (('big',) if a.nostd else ('std', 'big')):
                out, rs = run(H, 0, pol, a.S + 40, ctrim=a.ctrim if pol == 'big' else 0, maxs=3 * 10**9, real=True)
                print(f'  REAL b0=6 {pol}: {out} RS=' + ' '.join(f'{s}:P{p}:c{c}:z{z}' for s, p, c, z in rs), flush=True)
        for k in ([] if a.nostd else map(int, a.ks.split(','))):
            out, rs = run(H, k, 'std', a.S, n=a.n)
            print(f'  std k={k}: {out} RS=' + ' '.join(f'{s}:P{p}:c{c}:z{z}' for s, p, c, z in rs), flush=True)
        if a.big:
            for k in map(int, a.bigks.split(',')):
                out, rs = run(H, k, 'big', a.S, ctrim=a.ctrim, maxs=3 * 10**9, n=a.bign)
                print(f'  big+ctrim k={k}: {out} RS=' + ' '.join(f'{s}:P{p}:c{c}:z{z}' for s, p, c, z in rs), flush=True)
    threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
    t = threading.Thread(target=go); t.start(); t.join()
