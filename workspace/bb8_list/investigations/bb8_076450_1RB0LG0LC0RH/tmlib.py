"""Literal TM simulation helpers for the gap-word representation.
Tape words: x="1", a="10", b="100", c="1000"; configurations are
  0^inf [A reading 0] <word> 0^inf   (head on the 0 cell immediately left of the word).
"""
import re
MAIN = "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF0RH"
VAR1 = "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF1RA"
VAR2 = "1RB0LG_0RC1RG_1LD1RF_1RE---_0LH1LC_1RA1LA_1RH0RE_0LF0LC"
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

LET = {'x': '1', 'a': '10', 'b': '100', 'c': '1000'}

def expand(word):
    """word: sequence like 'abb*3 bab*2 x' with tokens separated by spaces; u*n repeats."""
    out = []
    for tok in word.split():
        if '*' in tok:
            u, n = tok.split('*'); n = int(n)
        else:
            u, n = tok, 1
        s = ''.join(LET.get(ch, ch) for ch in u)
        out.append(s * n)
    return ''.join(out)

TOK = "xabcdefghij"
def tokenize(bits):
    out = []; i = 0
    while i < len(bits) and bits[i] == '0':
        out.append('0'); i += 1
    while i < len(bits):
        i += 1; z = 0
        while i < len(bits) and bits[i] == '0':
            z += 1; i += 1
        out.append(TOK[z] if z < len(TOK) else '<%d>' % z)
    return ''.join(out)

def compress(s, maxL=10):
    out = []; i = 0
    while i < len(s):
        best = None
        for L in range(1, maxL + 1):
            u = s[i:i+L]
            if len(u) < L: break
            k = 1
            while s[i+k*L:i+(k+1)*L] == u: k += 1
            if k >= 2 and k*L >= max(3, 2*L) and (best is None or k*L > best[1]*len(best[0])):
                best = (u, k)
        if best:
            out.append('(%s)%d' % best); i += len(best[0]) * best[1]
        else:
            out.append(s[i]); i += 1
    return ' '.join(out)

class Sim:
    def __init__(self, tm, bits, state=0, pad=None):
        self.T = parse(tm)
        n = len(bits)
        pad = pad or (4 * n + 1000)
        self.tape = bytearray(pad) + bytearray(int(c) for c in bits) + bytearray(pad)
        self.pos = pad - 1           # head on the 0 just left of the word
        self.state = state
        self.steps = 0
        self.lo = self.pos; self.hi = pad + n
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
    def at_left_A0(self):
        return self.state == 0 and self.tape[self.pos] == 0 and not any(self.tape[self.lo:self.pos + 1])
    def word(self):
        """bits from head+1 to last 1 (only meaningful at left edge)."""
        t = self.tape
        hi = self.hi
        while hi > self.pos and t[hi] == 0: hi -= 1
        return ''.join(map(str, t[self.pos+1:hi+1]))
    def ones(self):
        return sum(self.tape)
    def show(self):
        t = self.tape
        lo, hi = self.lo, self.hi
        while lo < self.pos and t[lo] == 0: lo += 1
        while hi > self.pos and t[hi] == 0: hi -= 1
        L = ''.join(map(str, t[lo:self.pos])); R = ''.join(map(str, t[self.pos+1:hi+1]))
        return '%s [%s%d] %s' % (L, ST[self.state], t[self.pos], R)

def run_until_left(sim, maxsteps, first=True):
    """Run until the next state-A left-edge config (after at least one step). Returns 'left', 'halt', 'limit'."""
    start = sim.steps
    while sim.steps - start < maxsteps:
        if not sim.step():
            return 'halt'
        if sim.state == 0 and sim.pos <= sim.lo + 0 and sim.tape[sim.pos] == 0 and sim.at_left_A0():
            return 'left'
    return 'limit'
