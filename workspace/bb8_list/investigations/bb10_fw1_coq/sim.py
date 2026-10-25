"""Concrete simulator on token words.  word = far-to-near tokens; head in G right of the word."""
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
T = {}
for qi, ch in enumerate(TM.split('_')):
    for s in (0, 1):
        e = ch[3 * s:3 * s + 3]
        T[('ABCDEFGHIJ'[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, 'ABCDEFGHIJ'.index(e[2]))

def word(toks):
    return ''.join('10' * m + '1' for m in toks)

def tokens_of(cells):
    """parse a 0/1 string into tokens if possible: sequence of (10)^m 1; returns list or None"""
    s = cells.strip('0')
    out = []; i = 0
    while i < len(s):
        if s[i] != '1':
            return None
        j = i; m = 0
        while s[j + 1:j + 3] == '01':
            j += 2; m += 1
        out.append(m); i = j + 1
        if i < len(s) and s[i] == '0':
            # 00 gap
            return None
    return out

class Tape:
    def __init__(self, w, head, state):
        self.off = 1000
        self.t = bytearray(2 * len(w) + 2000)
        for i, ch in enumerate(w):
            self.t[self.off + i] = int(ch)
        self.h = self.off + head
        self.q = 'ABCDEFGHIJ'.index(state)
        self.steps = 0
    def grow(self):
        n = len(self.t)
        self.t = bytearray(n) + self.t + bytearray(n)
        self.off += n; self.h += n
    def step(self):
        s = self.t[self.h]
        tr = T[('ABCDEFGHIJ'[self.q], s)]
        if tr is None:
            return False
        w, d, q = tr
        self.t[self.h] = w; self.h += d; self.q = q; self.steps += 1
        if self.h <= 0 or self.h >= len(self.t) - 1:
            self.grow()
        return True
    def show(self, lo=None, hi=None):
        nz = [i for i, c in enumerate(self.t) if c]
        lo = min(nz + [self.h]) if lo is None else lo
        hi = max(nz + [self.h]) if hi is None else hi
        s = ''.join(str(c) for c in self.t[lo:hi + 1])
        p = self.h - lo
        return s[:p] + '[' + 'ABCDEFGHIJ'[self.q] + ']' + s[p:]
