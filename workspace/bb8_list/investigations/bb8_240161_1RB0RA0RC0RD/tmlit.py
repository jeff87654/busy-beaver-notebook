"""Generic exact literal Turing-machine simulator (no acceleration) plus tape display helpers.

Used by the K-family tools (kfam.py, ...) for the neighbors of
1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---.

  from tmlit import Sim, parse_tm
  s = Sim(tm)                       # blank tape, state A
  s = Sim.from_word(tm, '1101', off, 'B')   # word written at offset 0.., head at index `off` of the word
  s.step() -> False on an undefined transition (halt); s.steps, s.state (0..7), s.pos, s.tape
"""
ST = "ABCDEFGH"


def parse_tm(tm):
    t = []
    for ch in tm.split('_'):
        row = []
        for i in (0, 3):
            e = ch[i:i + 3]
            row.append(None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, ST.index(e[2])))
        t.append(row)
    return t


class Sim:
    def __init__(self, tm, size=1 << 16):
        self.tm = tm
        self.T = parse_tm(tm)
        self.tape = bytearray(size)
        self.pos = size // 2
        self.lo = self.hi = self.pos
        self.state = 0
        self.steps = 0
        self.last = None      # (state, symbol) of the last transition taken or attempted
        self.usage = None     # optional dict (state, sym) -> count

    @classmethod
    def from_word(cls, tm, word, off, state, size=1 << 16):
        s = cls(tm, size)
        base = s.pos - off
        for i, c in enumerate(word):
            s.tape[base + i] = int(c)
        s.lo = min(base, s.pos)
        s.hi = max(base + len(word) - 1, s.pos)
        s.state = ST.index(state) if isinstance(state, str) else state
        return s

    def grow(self):
        n = len(self.tape)
        self.tape = bytearray(n) + self.tape + bytearray(n)
        self.pos += n
        self.lo += n
        self.hi += n

    def step(self):
        s = self.tape[self.pos]
        self.last = (self.state, s)
        e = self.T[self.state][s]
        if e is None:
            return False
        if self.usage is not None:
            self.usage[(self.state, s)] = self.usage.get((self.state, s), 0) + 1
        w, d, q = e
        self.tape[self.pos] = w
        self.pos += d
        self.state = q
        self.steps += 1
        if self.pos < self.lo:
            self.lo = self.pos
            if self.pos <= 0:
                self.grow()
        elif self.pos > self.hi:
            self.hi = self.pos
            if self.pos >= len(self.tape) - 1:
                self.grow()
        return True

    def ones(self):
        return sum(self.tape[self.lo:self.hi + 1])

    def bounds(self):
        t = self.tape
        lo, hi = self.lo, self.hi
        while lo < self.pos and t[lo] == 0:
            lo += 1
        while hi > self.pos and t[hi] == 0:
            hi -= 1
        return lo, hi

    def runs(self):
        """Run-length description of the non-blank part: '3 . 5 .. 1' (numbers = runs of 1s, dots = zeros),
        plus the head's offset from the left end."""
        t = self.tape
        lo, hi = self.bounds()
        out = []
        i = lo
        while i <= hi:
            j = i
            while j <= hi and t[j] == t[i]:
                j += 1
            n = j - i
            if t[i] == 1:
                out.append(str(n))
            else:
                out.append('.' * n if n <= 3 else '0^%d' % n)
            i = j
        return ' '.join(out), self.pos - lo

    def show(self):
        t = self.tape
        lo, hi = self.bounds()
        L = ''.join(map(str, t[lo:self.pos]))
        R = ''.join(map(str, t[self.pos + 1:hi + 1]))
        return '%s [%s%d] %s' % (rle(L), ST[self.state], t[self.pos], rle(R))


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
