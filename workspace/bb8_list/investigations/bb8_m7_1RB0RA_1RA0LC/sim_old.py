"""Literal simulator for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF with snapshots."""
import sys
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF'
T = {}
for i, part in enumerate(TM.split('_')):
    for s in range(2):
        tr = part[3*s:3*s+3]
        if tr != '---':
            T[(chr(65+i), s)] = (int(tr[0]), 1 if tr[1] == 'R' else -1, tr[2])

class Cfg:
    def __init__(self, word, state='B', head=None, size=1 << 16):
        self.tape = bytearray(size)
        self.off = size // 2
        for i, ch in enumerate(word):
            self.tape[self.off + i] = int(ch)
        self.h = self.off + (len(word) if head is None else head)
        self.st = state
        self.lo = min(self.off, self.h)
        self.hi = max(self.off + len(word) - 1, self.h)
        self.steps = 0

    def step(self, n=1):
        tape, h, st = self.tape, self.h, self.st
        lo, hi = self.lo, self.hi
        for _ in range(n):
            key = (st, tape[h])
            if key not in T:
                self.h, self.st, self.lo, self.hi = h, st, lo, hi
                return 'HALT'
            w, d, st = T[key]
            tape[h] = w
            h += d
            if h < lo: lo = h
            if h > hi: hi = h
            self.steps += 1
        self.h, self.st, self.lo, self.hi = h, st, lo, hi
        return None

    def word(self):
        """nonblank word with the head marker, trimmed of outer zeros (head kept)."""
        s = []
        for i in range(self.lo, self.hi + 1):
            if i == self.h:
                s.append('[' + self.st + ']')
            s.append('1' if self.tape[i] else '0')
        return ''.join(s)

    def trimmed(self):
        w = self.word()
        a = w.split('[')[0].lstrip('0')
        b = w.split(']')[1].rstrip('0')
        return a + '[' + self.st + ']' + b

    def contents(self):
        """bits left of head, head symbol, bits right."""
        L = self.tape[self.lo:self.h].decode('latin1') if False else ''.join('1' if x else '0' for x in self.tape[self.lo:self.h])
        R = ''.join('1' if x else '0' for x in self.tape[self.h:self.hi + 1])
        return L.lstrip('0'), R.rstrip('0')

def used(j, b):
    """K1 used-up: j+1 tokens D(1) (incl. a-token), r = 3b+2."""
    return '101' * j + '101' + '10' * (3*b+2) + '111001'
