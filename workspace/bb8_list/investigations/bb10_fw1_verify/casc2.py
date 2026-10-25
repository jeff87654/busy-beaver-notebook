"""cascade rounds: from [6,6,3,Y,T,0,1^w | A] (T huge) record each round's first absorption (transit t, zeros W, junk)
   and the outcome.   casc2.py Y T w A1,A2,..."""
import sys, re
from fw import *

def run(Y, T, w, A, maxev=200000):
    L = [6, 6, 3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A)
    s = Server(M10, 'Bf,E0', 10 ** 9)
    rounds = []
    prev_t = None
    out = None
    for x in s.job(wd, h, q, 10 ** 11):
        if x['kind'] == 'BF':
            out = 'BF'; break
        if x['kind'] == 'HALT':
            it, idx, off = tokpos(x['word'], x['rel'])
            out = 'HALT@tokens-from-left=%d' % idx; break
        if x['kind'] == 'EV':
            it, idx, off = tokpos(x['word'], x['rel'])
            r = it[idx + 1:]
            # absorption pattern: [[D1]] D0 D(t) z2 D1^W junk
            if it[idx] == 1 and off == 1 and len(r) >= 3 and r[0] == 0 and isinstance(r[1], int) and r[2] == 'z2':
                t = r[1]; W = 0; k = 3
                while k < len(r) and r[k] == 1:
                    W += 1; k += 1
                junk = fmt(r[k:])
                if prev_t is None or t != prev_t - 2:
                    rounds.append((t, W, junk))
                prev_t = t
            maxev -= 1
            if maxev <= 0:
                out = 'MAXEV'; break
        if x['kind'] == 'TIMEOUT':
            out = 'TIMEOUT'; break
    s.close()
    return rounds, out

if __name__ == '__main__':
    Y, T, w = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    for A in [int(a) for a in sys.argv[4].split(',')]:
        TT = int(T) if not T.startswith('x') else int(T[1:]) * A + 401
        TT += (1 - TT) % 8
        rounds, out = run(Y, TT, w, A)
        print('A=%d w=%d T=%d:' % (A, w, TT), ' | '.join('t=%d W=%d %s' % (t, W, ('junk:' + j[:60]) if j else '') for t, W, j in rounds), '=>', out, flush=True)
