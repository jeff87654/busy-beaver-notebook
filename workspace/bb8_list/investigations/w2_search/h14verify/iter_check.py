"""One chain iteration from the exact real D_i (generic prefix, fresh atoms): run to the next decisive form
P 1 2^10 1^V 0 | U and compare V's exact residue with the class-map prediction D_(i+1).  python iter_check.py i"""
import sys, os, json
from absim import *
import absim, drive
i = int(sys.argv[1])
DL = json.load(open('dlist.json'))
D = new_atom('D', DL[i - 1], MB, rank=1010, note='D_%d' % i)
A = new_atom('A', stable_phi(MB), MB, rank=1020, note='acc')
pre = [('t', Val(2), Val(3)), ('t', Val(1), Val(1)), ('t', Val(7), Val(1)), ('t', Val(0), Val(1)), ('t', Val(5), Val(1)), ('t', Val(1), Val(1))]
runs = norm(pre + [('t', Val(2), Val(10)), ('t', Val(1), D), ('t', Val(0), Val(1)), ('t', A, Val(1))])
print('iteration', i, 'class', DL[i - 1] % 5, flush=True)
def stop(rs):
    if len(rs) < 4 or len(rs) <= len(pre) + 4: return False
    t = rs[-4:]
    if t[0][0] == 't' and t[0][1] == 2 and t[0][2] == 10 and t[1][0] == 't' and t[1][1] == 1 and Val.of(t[1][2]).huge() and t[3][0] == 't' and Val.of(t[3][1]).huge():
        V = Val.of(t[1][2])
        return D.co.keys() & V.co.keys() or any(ATOMS[a]['name'].startswith('X') for a in V.co)
    return False
r = drive.drive(runs, 60, lambda s: print(s[:300], flush=True), stop=stop)
print('END', r[0])
if r[0] == 'STOP':
    V = Val.of(r[1][-3][2])
    m = 5 ** 10
    print('D_next =', V, ' residue mod 5^10 =', V.res(m), ' predicted =', DL[i] % m if i < len(DL) else None, ' class', V.res(5))
