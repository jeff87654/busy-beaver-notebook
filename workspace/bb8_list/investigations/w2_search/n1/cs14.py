"""cs14.py MACHINE13 [--stages 300]: clone-split every defined transition X->T of the machine (adds state N = copy of T
with one symbol undefined) and follow each variant from the stage-37 input of n1 (far_17 + [0 1^329|1|19]);
report variants that HALT after >= 2 restarted rounds (period chains)."""
import sys, threading, argparse
from fstep import stage
from sim import far_of, word_of
from sigs import sig, chains
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--stages', type=int, default=300)
ap.add_argument('--n', type=int, default=329); ap.add_argument('--k', type=int, default=17); ap.add_argument('--only', default='')
a = ap.parse_args()
Q = 'ABCDEFGHIJKLMNOP'
parts = a.machine.split('_'); NQ = Q[len(parts)]
def follow(M):
    word = far_of(a.k) + word_of([0] + [1] * a.n + [1, 19]) + '1010'
    sigs = []
    for st in range(a.stages):
        kind, d = stage(M, word, 2 * 10**8)
        if kind != 'K':
            return f'{kind} {d} at {st}', sigs
        toks, far, newword, ev, nz, new = d
        sg = sig(toks)
        if sg and sg[2] >= 6: sigs.append((st,) + sg)
        word = newword
    return 'MAX', sigs
def go():
    for qi, p in enumerate(parts):
        for s in (0, 1):
            nm = f'{Q[qi]}{s}'
            if a.only and nm not in a.only.split(','): continue
            tr = p[3*s:3*s+3]
            if tr == '---': continue
            T = Q.index(tr[2]); tp = parts[T]
            for u in (0, 1):
                if tp[3*u:3*u+3] == '---': continue
                nt = tp[:3*u] + '---' + tp[3*u+3:]
                new = list(parts); newp = p[:3*s] + tr[:2] + NQ + p[3*s+3:]
                new[qi] = newp; new.append(nt)
                M = '_'.join(new)
                res, sigs = follow(M)
                ch = [c for c in chains(sigs) if c[4] >= 2]
                cs = ' '.join(f'{c[0]}-{c[1]}:m{c[2]}>{c[3]}:L{c[4]}:P{len(c[7])}' for c in ch)
                print(f'{nm}->{NQ} undef{u}: {res[:60]} | rounds={len(ch)} {cs} | {M}', flush=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
