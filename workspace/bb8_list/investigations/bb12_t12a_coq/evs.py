"""Event specs (start, target) for n1, plus literal validation of a spec."""
from shapes import *
O1 = lambda: tok(1)
def ones(c): return [x for _ in range(c) for x in tok(1)]
EV = {
 'H':  (W(ONES(n=1), O1(), Z(), tok(0, a=1)), W(tok(2), ONES(a=2), ones(4), Z(), ONES(n=1), Z(), tok(6))),
 'S0': (W(tok(2), ONES(M=1), ones(5), Z(), ONES(n=1), ones(2), Z(), tok(0, a=1)),
        W(tok(2), tok(5), ONES(M=1), Z(), Z(), Z(), tok(3, a=1), ONES(n=1), Z(), tok(4))),
}
GAP = [0, 0]
EV.update({
 'P1': (W(TWOS(k=1), tok(5), ONES(m=1), ones(6), Z(), Z(), tok(2), ONES(n=1), Z(), tok(0, a=1)),
        W(TWOS(k=1), tok(2), tok(2), tok(5), ONES(m=1), Z(), Z(), Z(), tok(1), tok(3, a=1), ONES(n=1), Z(), tok(6))),
 'P2': (W(TWOS(k=1), tok(5), ONES(m=1), ones(6), Z(), Z(), Z(), tok(1), T3(1, p=1), Z(), ONES(w=1), Z(), tok(0, r=1)),
        W(TWOS(k=1), tok(2), tok(2), tok(5), ONES(m=1), Z(), Z(), Z(), GAP, tok(2), tok(1, r=1), ONES(w=1), ONES(p=2), O1(), Z(), tok(4))),
 'P3': (W(TWOS(k=1), tok(5), ONES(m=1), Z(), Z(), Z(), GAP, tok(2), tok(2), ONES(w=1), Z(), tok(0, a=1)),
        W(TWOS(k=1), tok(5), ONES(m=1), Z(), Z(), tok(5, a=1), ONES(w=1), Z(), tok(6))),
 'P4': (W(TWOS(k=1), tok(5), ONES(m=1), ones(2), Z(), Z(), T3(0, q=1), Z(), ONES(w=1), Z(), tok(0, r=1)),
        W(TWOS(k=1), tok(5), ONES(m=1), Z(), Z(), tok(1, r=1), ONES(w=1), ONES(q=2), O1(), Z(), tok(4))),
})

for _k in ('P2', 'P4'):
    EV[_k] = EV[_k] + ({'r', 'w'},)
EV.update({
 'P2': (W(TWOS(k=1), tok(5), ONES(m=1), ones(6), Z(), Z(), Z(), tok(1), T3(1, p=1), Z(), ONES(w=1), Z(), tok(1, r=1)),
        W(TWOS(k=1), tok(2), tok(2), tok(5), ONES(m=1), Z(), Z(), Z(), GAP, tok(2), tok(2, r=1), ONES(w=1), ONES(p=2), O1(), Z(), tok(4))),
 'P4': (W(TWOS(k=1), tok(5), ONES(m=1), ones(2), Z(), Z(), T3(0, q=1), Z(), ONES(w=1), Z(), tok(1, r=1)),
        W(TWOS(k=1), tok(5), ONES(m=1), Z(), Z(), tok(2, r=1), ONES(w=1), ONES(q=2), O1(), Z(), tok(4))),
})
EV.update({
 'P2': (W(TWOS(k=1), tok(5), ONES(m=1), ones(6), Z(), Z(), Z(), tok(1), T3(1, p=1), Z(), ONES(w=1), O1(), Z(), tok(1, r=1)),
        W(TWOS(k=1), tok(2), tok(2), tok(5), ONES(m=1), Z(), Z(), Z(), GAP, tok(2), tok(2, r=1), ONES(w=1), ONES(p=2), ones(2), Z(), tok(4))),
 'P4': (W(TWOS(k=1), tok(5), ONES(m=1), ones(2), Z(), Z(), T3(0, q=1), Z(), ONES(w=1), O1(), Z(), tok(1, r=1)),
        W(TWOS(k=1), tok(5), ONES(m=1), Z(), Z(), tok(2, r=1), ONES(w=1), ONES(q=2), ones(2), Z(), tok(4))),
})
def FARE(**k):
    out = [TWOS(**k), tok(1), tok(6), GAP, Z(), [0]*5, tok(1), Z(), Z(), Z()]
    for _ in range(4): out += [GAP, Z()]
    return out + [GAP]
EV.update({
 'E': (W(TWOS(k=1), ones(0), tok(2), tok(2), tok(2), tok(2), tok(2), tok(2), tok(5), O1(), Z(), Z(), Z(), tok(1), T3(1, p=1), Z(), ONES(w=1), O1(), Z(), tok(1, r=1)),
       W(*FARE(k=1), tok(3, r=1), ONES(w=1), ONES(p=2), ones(2), Z(), tok(4))),
 'HALT': (W(*FARE(k=1), Z(), ONES(w=1), Z(), tok(0, f=1)), None),
})
# targets in the explorer's own run shapes: (101101)^p for 1^(2p), placed left of the w run
def PP(**v): return [run((1, 0, 1, 1, 0, 1), **v)]
EV['H'] = (EV['H'][0], W(tok(2), PP(a=1), ones(4), Z(), ONES(n=1), Z(), tok(6)))
EV['P2'] = (EV['P2'][0], W(TWOS(k=1), tok(2), tok(2), tok(5), ONES(m=1), Z(), Z(), Z(), GAP, tok(2), tok(2, r=1), PP(p=1), ONES(w=1), ones(2), Z(), tok(4)))
EV['P4'] = (EV['P4'][0], W(TWOS(k=1), tok(5), ONES(m=1), Z(), Z(), tok(2, r=1), PP(q=1), ONES(w=1), ones(2), Z(), tok(4)))
EV['E'] = (EV['E'][0], W(*FARE(k=1), tok(3, r=1), PP(p=1), ONES(w=1), ones(2), Z(), tok(4)))
