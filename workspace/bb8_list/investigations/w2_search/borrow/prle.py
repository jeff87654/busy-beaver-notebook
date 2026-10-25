"""prle.py: periodic RLE of a whitespace token list (period up to 10): '(a b c)^n'."""
import idle  # noqa: F401  (Idle priority)

import sys
def prle(t, maxp=10):
    out = []; i = 0; n = len(t)
    while i < n:
        best = (1, 1)
        for p in range(1, maxp + 1):
            r = 1
            while i + (r + 1) * p <= n and t[i + r * p:i + (r + 1) * p] == t[i:i + p]: r += 1
            if r > 1 and r * p > best[0] * best[1] and (r * p >= 2 * p): best = (p, r) if r * p > best[0] * best[1] else best
        p, r = best
        if r > 1:
            out.append(('(' + ' '.join(t[i:i + p]) + ')' if p > 1 else t[i]) + '^%d' % r); i += p * r
        else:
            out.append(t[i]); i += 1
    return ' '.join(out)
if __name__ == '__main__':
    for line in sys.stdin:
        print(prle(line.split()))
