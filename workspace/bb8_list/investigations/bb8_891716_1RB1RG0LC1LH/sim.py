"""Literal simulator for the 891716 machine. python sim.py N  -> prints tape at first-C-on-blank-right-of-K events."""
import sys
TM = "1RB1RG_0LC1LH_1LD1RC_---0LE_0RF0LA_0RA1LH_1RA0RC_1RA1LF"
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
T = parse(TM)

class Sim:
    def __init__(self, size=1 << 12):
        self.tape = bytearray(size); self.pos = size // 2; self.state = 0; self.steps = 0
    def grow(self):
        n = len(self.tape)
        self.tape = bytearray(n) + self.tape + bytearray(n); self.pos += n
    def run(self, N):
        tape, pos, st, steps = self.tape, self.pos, self.state, self.steps
        Tt = T
        while steps < N:
            if pos <= 1 or pos >= len(tape) - 2:
                self.tape, self.pos = tape, pos; self.grow(); tape, pos = self.tape, self.pos
            e = Tt[st][tape[pos]]
            if e is None:
                self.pos, self.state, self.steps = pos, st, steps
                return False
            tape[pos], d, st = e[0], e[1], e[2]
            pos += d; steps += 1
        self.pos, self.state, self.steps = pos, st, steps
        return True
    def word(self):
        t = self.tape
        lo = next(i for i, v in enumerate(t) if v); hi = len(t) - 1 - next(i for i, v in enumerate(reversed(t)) if v)
        return lo, hi
    def show(self):
        lo, hi = self.word()
        lo = min(lo, self.pos); hi = max(hi, self.pos)
        s = ''.join(map(str, self.tape[lo:hi+1]))
        return s, self.pos - lo, ST[self.state]

if __name__ == '__main__':
    N = int(sys.argv[1])
    s = Sim()
    ok = s.run(N)
    w, p, q = s.show()
    print(ok, s.steps, q, p, len(w))
    print(w[:p] + '[' + q + ']' + w[p:])
