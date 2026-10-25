"""Fit B> moments of a literal C7 run across a parameter.  bfit.py IDX u0 u1 ... (D0f with L = 15u+17, t=9, P=4u+40, s=2, y=30)
Prints for B> moment number IDX the block-RLE per u, then a token-wise linear fit when the token structures agree."""
import idle, sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim
from c7sim import C7
from r2d0 import word
from brle import brle
def moments(t, L, P, s, y, upto, maxs=10**8):
    sm = Sim(C7, word(t, L, P, s, y), state='B'); out = []
    while sm.steps < maxs and len(out) < upto:
        if not sm.step(): out.append(('HALT', sm.q, sm.pos)); break
        if sm.q == 'B' and sm.t[sm.pos] == 0 and sm.t.rfind(1) == sm.pos - 1:
            w, lo, r = sm.word(); out.append(w[lo:r + 1])
    return out
def toks(rl):
    return re.findall(r'\(([01]+)\)\^(\d+)|([01]+)', rl)
if __name__ == '__main__':
    idx = int(sys.argv[1]); us = [int(x) for x in sys.argv[2:]]
    rows = []
    for u in us:
        ms = moments(9, 15 * u + 17, 4 * u + 40, 2, 30, idx + 1)
        rl = brle(ms[idx]) if idx < len(ms) and isinstance(ms[idx], str) else str(ms[-1])
        rows.append(rl); print('u=%d: %s' % (u, rl[:400]))
    T = [toks(r) for r in rows]
    if len(set(len(x) for x in T)) == 1:
        out = []
        for parts in zip(*T):
            blks = set(p[0] or p[2] for p in parts)
            if len(blks) > 1: out.append('?' + '/'.join(sorted(blks))); continue
            b = parts[0][0] or parts[0][2]
            if parts[0][0]:
                ns = [int(p[1]) for p in parts]
                d = (ns[1] - ns[0]) / (us[1] - us[0])
                c = ns[0] - d * us[0]
                ok = all(abs(n - (d * u + c)) < 1e-9 for n, u in zip(ns, us))
                out.append('(%s)^[%g u + %g]%s' % (b, d, c, '' if ok else '!'))
            else: out.append(b)
        print('FIT:', ' '.join(out))
