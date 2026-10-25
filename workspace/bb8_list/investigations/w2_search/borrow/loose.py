"""loose.py: loose token view of a bit string: maximal blocks '1(01)^m' -> D(m) written as m; '0' runs between blocks
written as '_k' (k zeros beyond the single separator); used to see where digits sit inside far-region debris."""
import idle  # noqa: F401  (Idle priority)

import re, sys
def view(bits):
    out = []; i = 0; n = len(bits)
    while i < n:
        if bits[i] == '1':
            j = i + 1; m = 0
            while j + 1 < n and bits[j] == '0' and bits[j + 1] == '1':
                m += 1; j += 2
            out.append(str(m)); i = j
        else:
            j = i
            while j < n and bits[j] == '0': j += 1
            if j - i > 1: out.append('_%d' % (j - i))
            i = j
    # rle
    res = []; k = 0
    while k < len(out):
        l = k
        while l < len(out) and out[l] == out[k]: l += 1
        res.append(out[k] + ('^%d' % (l - k) if l - k > 1 else '')); k = l
    return ' '.join(res)
if __name__ == '__main__':
    print(view(sys.stdin.read().strip()))
