"""trace1.py K R t [lim]: B-at-right moments of X3 from Kt(1^K;1;3R+2;t), tapes block-compressed far-first."""
import idle, sys
from x3sim import *
def comp(bits):
    s = ''.join(map(str, bits))
    out = []; i = 0
    while i < len(s):
        best = None
        for L in range(1, 13):
            blk = s[i:i + L]
            if len(blk) < L: break
            n = 1
            while s[i + n * L:i + (n + 1) * L] == blk: n += 1
            if n >= 3 and (best is None or n * L > best[0] * best[1]): best = (n, L, blk)
        if best: out.append('(%s)^%d' % (best[2], best[0])); i += best[0] * best[1]
        else: out.append(s[i]); i += 1
    return ' '.join(out)
if __name__ == '__main__':
    K, R, t = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    s = Sim(X3, kx_left([1] * K, 1, 3 * R + 2, t, STD))
    lim = int(sys.argv[4]) if len(sys.argv) > 4 else 200000
    while s.steps < lim:
        if not s.step(): break
        if s.at_right():
            print(s.steps, comp(s.left_stream()[::-1]))
