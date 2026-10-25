from parts import *
L = [V('l')]
P = {
 'R1v': (K([L], tok(3, a=1), tok(0, r=1)), K([L], tok(0, a=1), tok(5, r=2)), ()),
 'R2v': (K([tok(3, m=1), L], tok(1), tok(0, r=1)), K([tok(0, m=1), L], tok(5, r=2), tok(1)), ()),
 'R3v': (K([zeros(M=1), tok(1), tok(3, m=1), L], tok(1), tok(0, r=1)), K([zeros(M=1), tok(5, r=2), tok(0, m=1), L], tok(1), tok(1)), ()),
}
for n, (s, t, pos) in P.items():
    try:
        mexp.explore(s, t, positive=frozenset(pos)); print(n, 'OK')
    except Exception as e:
        print(n, 'FAIL', str(e)[:300])
