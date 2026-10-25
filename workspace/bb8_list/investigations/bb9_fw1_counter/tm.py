"""tm.py: tiny literal TM tools. parse(machine) -> table; run(); rl() run-length tape view."""
import idle
def parse(m):
    T = {}
    for q, part in enumerate(m.split('_')):
        for c in range(2):
            x = part[3*c:3*c+3]
            if x[0] == '-' or x[2] in 'Z-': T[(q, c)] = None
            else: T[(q, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T
class TM:
    def __init__(s, m, tape=None, pos=0, q=0):
        s.T = parse(m); s.t = dict(tape or {}); s.pos = pos; s.q = q; s.steps = 0; s.halted = None
    def step(s):
        c = s.t.get(s.pos, 0); tr = s.T.get((s.q, c))
        if tr is None: s.halted = (s.q, c); return False
        w, d, n = tr
        if w: s.t[s.pos] = 1
        elif s.pos in s.t: del s.t[s.pos]
        s.pos += d; s.q = n; s.steps += 1; return True
    def word(s, lo=None, hi=None):
        ks = list(s.t) + [s.pos]
        lo = min(ks) if lo is None else lo; hi = max(ks) if hi is None else hi
        return lo, ''.join('1' if s.t.get(i) else '0' for i in range(lo, hi + 1))
    def view(s, maxlen=400):
        lo, w = s.word()
        hp = s.pos - lo
        return rl(w[:hp]) + ' [' + chr(65 + s.q) + ']' + w[hp] + ' ' + rl(w[hp+1:])
def rl(w, maxch=400):
    o = []; i = 0
    while i < len(w):
        j = i
        while j < len(w) and w[j] == w[i]: j += 1
        n = j - i
        o.append(w[i] + ('^%d' % n if n >= 4 else w[i] * (n - 1)) if n >= 4 else w[i:j])
        i = j
    s = ' '.join(o)
    return s if len(s) <= maxch else s[:maxch//2] + ' ... ' + s[-maxch//2:]
