def compress(s, maxp=8, minrep=3):
    """Greedy block compression of a 0/1 string: (u)^n for n>=minrep."""
    out = []
    i = 0
    n = len(s)
    lit = []
    while i < n:
        best = None
        for p in range(1, maxp + 1):
            if i + p > n: break
            u = s[i:i+p]
            k = 1
            while s[i+k*p:i+(k+1)*p] == u:
                k += 1
            if k >= minrep and (best is None or k*p > best[0]*best[1] ):
                best = (k, p, u)
        if best:
            if lit: out.append(''.join(lit)); lit = []
            k, p, u = best
            out.append('(%s)^%d' % (u, k))
            i += k*p
        else:
            lit.append(s[i]); i += 1
    if lit: out.append(''.join(lit))
    return ' '.join(out)
