import idle
"""Literal TM utilities for champ_231 extensions. Tape: dict-free list with offset."""
C231 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
C232 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"
def parse(s):
    rows = s.split('_'); T = {}
    for q, r in enumerate(rows):
        for b in (0, 1):
            t = r[3*b:3*b+3]
            if t[0] in '-' or t[2] in 'HZ' and len(rows) <= 7 and False:
                T[(q, b)] = None
            elif t[2] == '-' or t[0] == '-':
                T[(q, b)] = None
            else:
                T[(q, b)] = (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)
    return T, len(rows)
def kword(a, ds):
    """K(a; ds): head (state E=4) on the leading 0. returns string starting at head."""
    w = "0100" + "11"*a + "00"
    for d in ds: w += "11"*d + "00"
    return w + "1"
class Run:
    def __init__(self, T, word, head_idx, state, pad=1 << 16):
        self.T = T
        self.tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
        self.p = pad + head_idx; self.q = state; self.steps = 0
    def grow(self):
        pad = len(self.tape)
        self.tape = bytearray(pad) + self.tape + bytearray(pad); self.p += pad
    def step(self):
        c = self.tape[self.p]; t = self.T[(self.q, c)]
        if t is None: return False
        self.tape[self.p] = t[0]; self.p += t[1]; self.q = t[2]; self.steps += 1
        if self.p <= 0 or self.p >= len(self.tape) - 1: self.grow()
        return True
    def run(self, maxsteps):
        T = self.T; tape = self.tape; p = self.p; q = self.q; s = 0
        while s < maxsteps:
            t = T[(q, tape[p])]
            if t is None: break
            tape[p] = t[0]; p += t[1]; q = t[2]; s += 1
            if p <= 0 or p >= len(tape) - 1:
                self.p = p; self.q = q; self.steps += s; maxsteps -= s; s = 0
                self.grow(); tape = self.tape; p = self.p
        self.p = p; self.q = q; self.steps += s
        return self.T[(q, tape[p])] is None
    def view(self):
        nz = [i for i, v in enumerate(self.tape) if v]
        lo = min(nz + [self.p]); hi = max(nz + [self.p])
        return lo, hi, ''.join(str(v) for v in self.tape[lo:self.p]), self.tape[self.p], ''.join(str(v) for v in self.tape[self.p+1:hi+1])
def rle(s):
    if not s: return ''
    out = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        out.append(s[i] + ('^%d' % (j - i) if j - i > 1 else '')); i = j
    return ' '.join(out)
