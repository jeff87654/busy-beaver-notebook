"""clonesplit.py: clone-split variants of a 12-state machine (adds state M): redirect one transition X->T to X->M,
M = copy of T with one symbol undefined.  Test: clean restart for k in GOOD, halt (on M) for k in BAD."""
import sys, threading
from fstep import stage
from sim import far_of, word_of
BASE = sys.argv[1]
GOOD = [int(x) for x in sys.argv[2].split(',')]; BAD = [int(x) for x in sys.argv[3].split(',')]
slots = sys.argv[4].split(',') if len(sys.argv) > 4 else None
Q = 'ABCDEFGHIJKLMNOP'
parts = BASE.split('_')
def outcome(M, k, S=60, n=30):
    word = far_of(k) + word_of([0] + [1] * n + [1, 19]) + '1010'
    for st in range(S):
        kind, d = stage(M, word, 10**8)
        if kind != 'K':
            return f'{kind}{d[0]}{d[1]}' if kind == 'H' else kind
        toks, far, newword, ev, nz, new = d
        dd = toks[:-2]
        if not far and len(dd) > 2 and dd[0] == 2 and dd[1] == 5:
            return 'CLEAN'
        word = newword
    return 'MAX'
def go():
    cand = []
    for qi, p in enumerate(parts):
        for s in (0, 1):
            nm = f'{Q[qi]}{s}'
            if slots and nm not in slots: continue
            tr = p[3*s:3*s+3]
            if tr == '---': continue
            T = Q.index(tr[2]); tp = parts[T]
            for u in (0, 1):
                mt = tp[:3*u] + '---' + tp[3*u+3:]
                new = list(parts); newp = list(p); newp[3*s:3*s+3] = list(tr[:2] + 'M')
                new[qi] = ''.join(newp)
                if len(new) == 12: new.append(mt)
                else: new[12] = mt
                cand.append((nm, u, '_'.join(new)))
    for nm, u, M in cand:
        g = [outcome(M, k) for k in GOOD]
        if any(x != 'CLEAN' for x in g):
            print(f'{nm} M-undef{u}: GOOD fails {g}', flush=True); continue
        b = [outcome(M, k) for k in BAD]
        print(f'{nm} M-undef{u}: GOOD ok, BAD {b}  {M}', flush=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
