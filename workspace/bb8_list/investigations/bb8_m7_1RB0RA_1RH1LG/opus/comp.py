def compress(s, minrep=3, maxp=6):
    """greedy: at each position find the (period, reps) maximizing covered length with reps >= minrep."""
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == '[':
            j = s.index(']', i)
            out.append(s[i:j+1]); i = j + 1; continue
        best = None
        for p in range(1, maxp + 1):
            blk = s[i:i+p]
            if len(blk) < p or '[' in blk: break
            k = 1
            while s[i+k*p:i+(k+1)*p] == blk:
                k += 1
            if k >= minrep and (best is None or k*p > best[0]*best[1] + (p - 1 if best else 0)):
                best = (k, p, blk)
        if best:
            k, p, blk = best
            out.append('(%s)^%d' % (blk, k)); i += k * p
        else:
            out.append(s[i]); i += 1
    # merge single chars
    res = []
    for t in out:
        if len(t) == 1 and res and not res[-1].startswith('(') and not res[-1].startswith('['):
            res[-1] += t
        else:
            res.append(t)
    return ' '.join(res)
