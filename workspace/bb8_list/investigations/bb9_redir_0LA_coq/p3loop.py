import pickle
from common import *
from inst import word, sim
UNIT = (1, 1, 0, 0, 1)
P3 = pickle.load(open('st2_p3U.pkl', 'rb'))
q, L, R, mode = P3
FAR = L[1:]
def X(v, i, c=2):
    """[far] unit^v D(c+i) C> 0 D1^(c+i) 100 [P3 right]"""
    Lx = [1] + [0, 1] * c + [run((0, 1), i=1)] + [run(UNIT, v=1)] + FAR
    Rx = [0] + list(Z) * c + [run(Z, i=1)] + [1, 0, 0] + R
    return ('C', Lx, Rx, '>')
if __name__ == '__main__':
    for c in (0, 1, 2):
        # literal: from P3 with U units, do we pass X(U-k, k-c) for k = c..?
        U = 9
        s = sim(P3, {'U': U, 'r': 3})
        targets = {}
        for k in range(c, U + 1):
            w, hp, qq = word(X(U - (k - c), k - c, c) if False else X(U - (k - c), k - c, c), {'v': U - (k - c), 'i': k - c, 'r': 3})
            targets[(w.strip('0'), qq)] = k
        hits = []
        for _ in range(200000):
            st, l, r = s.word()
            key = (st[l:r + 1], s.q)
            if key in targets and s.t[s.pos] == 0:
                hits.append((targets[key], s.steps))
            if not s.step(): break
        print('c=%d hits' % c, hits[:20])
