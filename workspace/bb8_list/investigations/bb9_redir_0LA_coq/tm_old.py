"""Shared helpers: machine, literal simulator, RLE view.  Machine #11 of bb9 c7m12 section 10.1."""
import re
M11 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
M12 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RH0RE_0LH---'
TAIL = '111111110011111100111111001111110011111100111111001001'

def parse(m):
    tr = {}
    for i, g in enumerate(m.split('_')):
        for c in (0, 1):
            x = g[3 * c:3 * c + 3]
            tr[(chr(65 + i), c)] = None if x[0] == '-' else (int(x[0]), 1 if x[1] == 'R' else -1, x[2])
    return tr

def D(m):
    return '10' * m + '1'

def K(ds, a, b, tail='111001'):
    """ds farthest first"""
    return '11' + ''.join(D(3 * d + 1) for d in ds) + D(3 * a + 1) + '10' * (3 * b + 2) + tail

def lam(b):
    return '11' + D(4) + D(21) + D(4) + D(17) + D(4) * (12 * b - 12) + D(1) + D(34) + '10' * 44 + TAIL

class Sim:
    def __init__(self, m, word, head=None, state='B'):
        self.tr = parse(m)
        self.t = bytearray(word.encode()) if False else bytearray(int(c) for c in word)
        self.off = 0
        self.pos = len(word) if head is None else head
        self.q = state
        self.steps = 0
        self.halted = False
        self._grow()
    def _grow(self):
        if self.pos < 0:
            n = max(1024, -self.pos)
            self.t[0:0] = bytearray(n); self.pos += n; self.off += n
        if self.pos >= len(self.t):
            self.t.extend(bytearray(max(1024, self.pos - len(self.t) + 1)))
    def step(self):
        c = self.t[self.pos]
        x = self.tr[(self.q, c)]
        if x is None:
            self.halted = True
            return False
        w, d, nq = x
        self.t[self.pos] = w
        self.pos += d
        self.q = nq
        self.steps += 1
        if self.pos < 0 or self.pos >= len(self.t):
            self._grow()
        return True
    def run(self, n):
        for _ in range(n):
            if not self.step():
                return False
        return True
    def word(self):
        s = ''.join(map(str, self.t))
        l = s.find('1'); r = s.rfind('1')
        return s, l, r
    def view(self, tok=True):
        s, l, r = self.word()
        lo = min(l, self.pos) if l >= 0 else self.pos
        hi = max(r, self.pos)
        w = s[lo:hi + 1]
        hp = self.pos - lo
        return rle(w, hp, self.q) if tok else w[:hp] + '[' + self.q + ']' + w[hp:]

def tokz(w):
    out = []
    i, n = 0, len(w)
    while i < n:
        m = 0
        while i + 2 * m + 1 < n and w[i + 2 * m] == '1' and w[i + 2 * m + 1] == '0':
            m += 1
        if m >= 1 and i + 2 * m < n and w[i + 2 * m] == '1':
            out.append('D%d' % m); i += 2 * m + 1
        elif m >= 2:
            out.append('(10)^%d' % m); i += 2 * m
        else:
            out.append(w[i]); i += 1
    # merge literal runs
    res = []
    for t in out:
        if len(t) == 1 and res and set(res[-1]) <= set('01'):
            res[-1] += t
        else:
            res.append(t)
    # compress repeats
    comp = []
    for t in res:
        if comp and comp[-1][0] == t:
            comp[-1][1] += 1
        else:
            comp.append([t, 1])
    return ' '.join(t if k == 1 else '%s^%d' % (t, k) for t, k in comp)

def rle(w, hp=None, q=None):
    if hp is None:
        return tokz(w)
    return tokz(w[:hp]) + ' <%s> ' % q + tokz(w[hp:])

def kparse(w, tail='111001'):
    """'11' D(m1) ... D(mk) (10)^r tail -> ([m1..mk], r) or None"""
    if not w.endswith(tail):
        return None
    m = re.fullmatch(r'11((?:(?:10)*1)*)((?:10)*)', w[:len(w) - len(tail)])
    if not m:
        return None
    ms = [len(t) // 2 for t in re.findall(r'((?:10)*)1', m.group(1))]
    return ms, len(m.group(2)) // 2

def at_family(s, tail='111001'):
    """head in B on the blank right of everything and the word parses"""
    if s.q != 'B' or s.t[s.pos] != 0 or s.t.rfind(1) > s.pos:
        return None
    w, l, r = s.word()
    if s.pos != r + 1:
        return None
    return kparse(w[l:r + 1], tail)

def kparse_any(w):
    """'11' D(m1) ... D(mk) (10)^r '11' (11111100)^j '1001' -> (ms, r, j) or None"""
    m = re.fullmatch(r'11((?:(?:10)*1)*?)((?:10)*)11((?:11111100)*)1001', w)
    if not m:
        return None
    ms = [len(t) // 2 for t in re.findall(r'((?:10)*)1', m.group(1))]
    return ms, len(m.group(2)) // 2, len(m.group(3)) // 8

def at_family_any(s):
    if s.q != 'B' or s.t[s.pos] != 0 or s.t.rfind(1) > s.pos:
        return None
    w, l, r = s.word()
    if s.pos != r + 1:
        return None
    return kparse_any(w[l:r + 1])
