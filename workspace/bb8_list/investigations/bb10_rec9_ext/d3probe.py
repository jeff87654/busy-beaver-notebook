"""D3 / D0 events next to a small token X in A/B-type machines (follower convention, state A):
word = D(0)^2 LEFT D(X) D(Z) D(1)^k D(1) D(r) D(0)^6 (100 D(0)^5)^t 100 100   (bb8-ab's d2map.word layout)"""
import sys
import follow3 as F
def D(m): return '10' * m + '1'
def word(left, X, k, r, t, Z):
    w = D(0) * 2 + ''.join(D(x) for x in left) + D(X) + D(Z) + D(1) * k + D(1) + D(r) + D(0) * 6
    return w + ('100' + D(0) * 5) * t + '100' + '100'
ms = sys.argv[1].split(',')
left = [int(x) for x in sys.argv[2].split(',')]
X, Z = int(sys.argv[3]), int(sys.argv[4])
ks = [int(x) for x in sys.argv[5].split(',')]
rs = [int(x) for x in sys.argv[6].split(',')]
budget = int(sys.argv[7]) if len(sys.argv) > 7 else 300000000
for m in ms:
    for k in ks:
        for r in rs:
            w = word(left, X, k, r, 7, Z)
            o = F.run_hyb(m, w, budget, start='A', canon='A')
            print(m.split('_')[-1], k, r, o['raw'][:150], flush=True)
