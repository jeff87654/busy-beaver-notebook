"""sim.py: tiny literal TM simulator for n1-based gadget machines (any number of states, '---' = undefined).
Tape words use the follower convention: word = far + D(t)... + D(a) + D(r) + SUF('1010'), head right of the word in G."""
import re
QS = 'ABCDEFGHIJKLMNOP'
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
FAR_TAIL = '10110101010101010010000010111100100100100100'

def parse(tm):
    T = {}
    for qi, ch in enumerate(tm.split('_')):
        for s in (0, 1):
            e = ch[3*s:3*s+3]
            T[(QS[qi], s)] = None if (e[0] == '-' or e[2] == 'Z') else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])
    return T

def D(m): return '10' * m + '1'
def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v
def word_of(toks): return ''.join(D(m) for m in toks)
def far_of(k): return '10101' * k + FAR_TAIL

class Sim:
    def __init__(self, tm, word, head=None, q='G', pad=1 << 14):
        self.T = parse(tm) if isinstance(tm, str) else tm
        self.pad = pad
        self.t = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
        self.h = pad + (len(word) if head is None else head); self.q = q; self.steps = 0
        self.used = set()
    def run(self, maxs, stop=None):
        t = self.t; T = self.T
        while self.steps < maxs:
            if self.h < 2 or self.h >= len(t) - 2:
                n = len(t); self.t = t = bytearray(n) + t + bytearray(n); self.h += n; self.pad += n
            s = t[self.h]
            self.used.add((self.q, s))
            tr = T[(self.q, s)]
            if tr is None: return 'HALT'
            if stop and stop(self): return 'STOP'
            w, d, q = tr
            t[self.h] = w; self.h += d; self.q = q; self.steps += 1
        return 'TIMEOUT'
    def word(self):
        s = ''.join(map(str, self.t)); a = s.find('1'); b = s.rfind('1')
        if a < 0: return '', 0, 0
        return s[a:b+1], self.h - a, a
    def show(self, win=60):
        s = ''.join(map(str, self.t)); a = s.find('1'); b = s.rfind('1')
        lo = min(a, self.h) ; hi = max(b, self.h)
        out = s[lo:self.h] + '[' + self.q + ']' + s[self.h:hi+1]
        return out
