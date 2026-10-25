"""Literal B-form macro run from the round-2-end Per form:
  far: D2^k D1 D8 0 0 D3 D(p), then D2^K D5 D1^3 D0 D0 D2 D1^n D0 D(a)
python r2end.py k p K n a"""
import sys
sys.path.insert(0, '../ana')
from macro2 import *
def per_word(k, p, K, n, a):
    far = D(2) * k + D(1) + D(8) + '00' + D(3) + D(p)
    return far + D(2) * K + D(5) + D(1) * 3 + D(0) + D(0) + D(2) + D(1) * n + D(0) + D(a)
if __name__ == '__main__':
    k, p, K, n, a = map(int, sys.argv[1:6])
    R = Run({}, verbose=True)
    wd = per_word(k, p, K, n, a)
    R.go(wd, len(wd), 'H')
