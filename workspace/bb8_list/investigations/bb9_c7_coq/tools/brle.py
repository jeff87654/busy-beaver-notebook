"""Block run-length view of a 0/1 string: greedy, blocks of length 1..10, repeated >= 3 times -> (blk)^n."""
def brle(w, maxb=10, minrep=3):
    out = []; i = 0; n = len(w); lit = ''
    while i < n:
        best = None
        for b in range(1, maxb + 1):
            blk = w[i:i + b]
            if len(blk) < b: break
            k = 1
            while w[i + k * b:i + (k + 1) * b] == blk: k += 1
            if k >= minrep and (best is None or k * b > best[0] * best[1] + 2):
                best = (b, k)
        if best:
            if lit: out.append(lit); lit = ''
            b, k = best
            out.append('(%s)^%d' % (w[i:i + b], k)); i += b * k
        else:
            lit += w[i]; i += 1
    if lit: out.append(lit)
    return ' '.join(out)
