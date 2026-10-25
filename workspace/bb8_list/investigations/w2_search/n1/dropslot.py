"""dropslot.py MACHINE [--stages 200]: for each new-state slot (J0, K*, L*, M*), make it undefined and follow from
the real start's stage-37 input (far_17 + [0 1^329 | 1 | 19]); report halts with the period chains before them."""
import sys, threading, argparse
from fstep import stage
from sim import far_of, word_of
from sigs import sig, chains
ap2 = argparse.ArgumentParser(); ap2.add_argument('machine'); ap2.add_argument('--stages', type=int, default=200)
ap2.add_argument('--k', type=int, default=17); ap2.add_argument('--n', type=int, default=329); ap2.add_argument('--slots', default='')
b = ap2.parse_args()
Q = 'ABCDEFGHIJKLMNOP'
parts = b.machine.split('_')
def go():
    slots = [f'{Q[i]}{s}' for i in range(9, len(parts)) for s in (0, 1)]
    if b.slots: slots = b.slots.split(',')
    for sl in [None] + slots:
        p = list(parts)
        if sl:
            qi = Q.index(sl[0]); s = int(sl[1])
            if p[qi][3*s:3*s+3] == '---': continue
            p[qi] = p[qi][:3*s] + '---' + p[qi][3*s+3:]
        M = '_'.join(p)
        word = far_of(b.k) + word_of([0] + [1] * b.n + [1, 19]) + '1010'
        sigs = []; res = 'MAX'
        for st in range(b.stages):
            kind, d = stage(M, word, 2 * 10**8)
            if kind != 'K':
                res = f'{kind} {d} at {st}'; break
            toks, far, newword, ev, nz, new = d
            sg = sig(toks)
            if sg and sg[2] >= 6: sigs.append((st,) + sg)
            word = newword
        ch = [c for c in chains(sigs) if c[4] >= 2]
        cs = ' '.join(f'{c[0]}-{c[1]}:m{c[2]}>{c[3]}:L{c[4]}:z{c[5]}>{c[6]}:P{len(c[7])}' for c in ch)
        print(f'drop {sl}: {res} | chains: {cs}', flush=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
