"""ktparse.py: parse a word (far->near, ending before the head) as Kt: far D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001,
pkf4-style (greedy from the right). Returns (far_raw_prefix, tokens far->near, m, r, t) or None."""
def parse(w):
    if not w.endswith('1001'): return None
    p = len(w) - 4; t = 0
    while w[p - 8:p] == '11111100': p -= 8; t += 1
    if w[p - 2:p] != '11': return None
    p -= 2; r = 0
    while p >= 2 and w[p - 2:p] == '10': r += 1; p -= 2
    toks = []
    while p >= 1 and w[p - 1] == '1':
        q = p - 1; x = 0
        while q >= 2 and w[q - 2:q] == '10': x += 1; q -= 2
        toks.append(x); p = q
    toks.reverse()
    return w[:p], toks[:-1], toks[-1] if toks else None, r, t
