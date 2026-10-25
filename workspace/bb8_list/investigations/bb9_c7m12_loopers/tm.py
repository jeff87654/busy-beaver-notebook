"""tm.py: small literal TM helpers (python) for the c7m12 looper study."""
def parse(m):
    rows = m.split('_')
    T = {}
    for q, r in enumerate(rows):
        for c in range(2):
            x = r[3 * c:3 * c + 3]
            if x[0] != '-' and x[2] != 'Z':
                T[(q, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T, len(rows)

def kword(ds, a, b):
    """K(ds; a; b) = 11 D(3d+1).. D(3a+1) (10)^(3b+2) 111001, head in B on the blank right of it"""
    D = lambda m: '10' * m + '1'
    return '11' + ''.join(D(3 * d + 1) for d in ds) + D(3 * a + 1) + '10' * (3 * b + 2) + '111001'

def run(m, word='', head=0, state='A', maxs=10**6, stop=None):
    """literal run; stop(tape, pos, q, step) -> True stops. returns (kind, step, tape dict, pos, q)"""
    T, n = parse(m)
    tape = {i: int(ch) for i, ch in enumerate(word) if ch == '1'}
    pos, q = head, ord(state) - 65
    for step in range(maxs):
        if stop and stop(tape, pos, q, step):
            return 'S', step, tape, pos, q
        c = tape.get(pos, 0)
        t = T.get((q, c))
        if t is None:
            return 'H', step, tape, pos, q
        w, d, nq = t
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq
    return 'T', maxs, tape, pos, q

def word_of(tape, lo=None, hi=None):
    if not tape: return ''
    lo = min(tape) if lo is None else lo; hi = max(tape) if hi is None else hi
    return ''.join('1' if tape.get(i) else '0' for i in range(lo, hi + 1))

def dtoks(w):
    """D-token view of a word: D(m) = (10)^m 1 as numbers, other cells raw <...>, equal neighbours x*k"""
    tok = []; raw = ''; i = 0; n = len(w)
    while i < n and w[i] == '0': i += 1
    while i < n:
        j = i; m = 0
        while j + 1 < n and w[j] == '1' and w[j + 1] == '0': j += 2; m += 1
        if j < n and w[j] == '1':
            if raw: tok.append('<' + raw + '>'); raw = ''
            tok.append(str(m)); i = j + 1
        else:
            raw += w[i]; i += 1
    if raw: tok.append('<' + raw + '>')
    out = []; k = 0
    while k < len(tok):
        l = k
        while l < len(tok) and tok[l] == tok[k]: l += 1
        out.append(tok[k] + (f'*{l-k}' if l - k > 1 else '')); k = l
    return ' '.join(out)

def kw(toks, r):
    """E0-twin K word: D-tokens then (10)^r (+0 if r odd); head on the blank right of it in state I"""
    return ''.join('10' * m + '1' for m in toks) + '10' * r + '0' * (r % 2)
