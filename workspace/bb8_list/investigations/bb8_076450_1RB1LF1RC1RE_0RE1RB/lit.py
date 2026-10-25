"""Literal simulator helpers for 1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC."""
import sys
MAIN = "1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC"
ST = "ABCDEFGH"

def parse(tm):
    t = []
    for ch in tm.split('_'):
        row = []
        for i in (0, 3):
            e = ch[i:i+3]
            row.append(None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, ST.index(e[2])))
        t.append(row)
    return t

def rle(s):
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        n = j - i
        out.append(s[i] if n == 1 else '%s^%d' % (s[i], n))
        i = j
    return ' '.join(out)

def compress(s, maxL=12):
    out = []; i = 0
    while i < len(s):
        best = None
        for L in range(1, maxL + 1):
            u = s[i:i+L]
            if len(u) < L: break
            k = 1
            while s[i+k*L:i+(k+1)*L] == u: k += 1
            if k >= 2 and k*L >= max(4, 2*L) and (best is None or k*L > best[1]*len(best[0])):
                best = (u, k)
        if best:
            out.append('(%s)^%d' % best); i += len(best[0]) * best[1]
        else:
            out.append(s[i]); i += 1
    # merge single chars
    res = []
    for t in out:
        if len(t) == 1 and res and not res[-1].startswith('('):
            res[-1] += t
        else:
            res.append(t)
    return ' '.join(res)

class Sim:
    def __init__(self, tm=MAIN, size=1 << 16):
        self.T = parse(tm)
        self.tape = bytearray(size)
        self.pos = size // 2
        self.lo = self.hi = self.pos
        self.state = 0
        self.steps = 0
    def grow(self):
        n = len(self.tape)
        self.tape = bytearray(n) + self.tape + bytearray(n)
        self.pos += n; self.lo += n; self.hi += n
    def step(self):
        s = self.tape[self.pos]
        e = self.T[self.state][s]
        if e is None:
            return False
        w, d, q = e
        self.tape[self.pos] = w; self.pos += d; self.state = q; self.steps += 1
        if self.pos < self.lo:
            self.lo = self.pos
            if self.pos <= 0: self.grow()
        if self.pos > self.hi:
            self.hi = self.pos
            if self.pos >= len(self.tape) - 1: self.grow()
        return True
    def show(self, comp=True):
        t = self.tape
        lo, hi = self.lo, self.hi
        while lo < self.pos and t[lo] == 0: lo += 1
        while hi > self.pos and t[hi] == 0: hi -= 1
        L = ''.join(map(str, t[lo:self.pos])); R = ''.join(map(str, t[self.pos+1:hi+1]))
        if comp:
            L = compress(L); R = compress(R)
        return '%s [%s%d] %s' % (L, ST[self.state], t[self.pos], R)
    def ones(self):
        return sum(self.tape[self.lo:self.hi+1])
