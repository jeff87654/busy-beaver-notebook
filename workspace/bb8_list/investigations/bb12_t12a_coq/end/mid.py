"""tape of the EAT event at the moment the head is leftmost (and some later snapshots)"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ana')
from evs_end import *
from probe import word_of, MK
from bsim import TT
from view import view
r, j = int(sys.argv[1]), int(sys.argv[2])
S = EVE['EAT%d' % r][0]
w = word_of(S, dict(j=j, x=3, A=40, K=7))
def sim(stop=None):
    PAD = 4096
    t = bytearray(PAD) + bytearray(int(c) for c in w) + bytearray(PAD)
    h = len(w) + PAD; q = 'H'; n = 0; lo = (h, 0)
    while True:
        if stop is not None and n == stop: return t, h, q
        tr = TT[(q, t[h])]
        w_, d, q = tr; t[h] = w_; h += d; n += 1
        if h < lo[0]: lo = (h, n)
        if q == 'H' and t[h] == 0 and t.find(1, h) < 0 and n > 1000:
            return lo, n
lo, total = sim()
print('leftmost at step', lo[1], 'of', total)
for st in [lo[1]] + [int(x) for x in sys.argv[3:]]:
    t, h, q = sim(st)
    s = ''.join(map(str, t))
    a = s.find(MK) + len(MK); b = s.rfind('1')
    print(st, q, 'head', h - a)
    print('   L:', view(s[a:h].lstrip('0')))
    print('   R:', s[h:b + 1])
