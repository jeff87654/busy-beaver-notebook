"""Literal n1 simulator on B-forms (pure Python; small sizes)."""
import re
TMS = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---'
QS = 'ABCDEFGHIJKLMNOP'
T = {}
for qi, ch in enumerate(TMS.split('_')):
    for s in (0, 1):
        e = ch[3*s:3*s+3]
        T[(QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])

def D(m): return '10'*m + '1'

def bword(ts, A, far=''):
    return far + ''.join(D(t) if isinstance(t, int) else t for t in ts) + D(0) + D(A)

class Tape:
    def __init__(self, word, head, q):
        self.t = bytearray(int(c) for c in word)
        self.off = 0; self.h = head; self.q = q; self.steps = 0
    def cell(self):
        return self.t[self.h]
    def step(self):
        if self.h < 0:
            self.t[0:0] = bytearray(256); self.h += 256; self.off += 256
        if self.h >= len(self.t):
            self.t.extend(bytearray(256))
        tr = T[(self.q, self.t[self.h])]
        if tr is None:
            return False
        w, d, q = tr
        self.t[self.h] = w; self.h += d; self.q = q; self.steps += 1
        return True
    def word(self):
        s = bytes(self.t).decode('latin1') if False else ''.join(map(str, self.t))
        a = s.find('1'); b = s.rfind('1')
        if a < 0: return '', 0
        return s[a:b+1], self.h - a

TOK = re.compile(r'(?:10)*1')
def tokens(word):
    out = []; i = 0; n = len(word)
    while i < n:
        if word[i] == '0':
            j = i
            while j < n and word[j] == '0': j += 1
            out.append('z%d' % (j-i)); i = j; continue
        j = i; m = 0
        while j + 2 < n and word[j+1] == '0' and word[j+2] == '1':
            j += 2; m += 1
        out.append(m); i = j + 1
    return out

def fmt(items):
    out = []; prev = None; c = 0
    for x in items + [None]:
        if x == prev: c += 1; continue
        if prev is not None:
            s = ('D%d' % prev) if isinstance(prev, int) else prev
            out.append(s if c == 1 else '%s^%d' % (s, c))
        prev = x; c = 1
    return ' '.join(out)

def is_bform(tp):
    """state H, head on the blank right of the word, word = ... D0 D(A)"""
    if tp.q != 'H': return None
    w, rel = tp.word()
    if rel != len(w): return None
    it = tokens(w)
    if len(it) < 2 or it[-2] != 0 or not isinstance(it[-1], int): return None
    return it[:-2], it[-1]

def run_to_b(word, head=None, q='H', maxsteps=10**7, first_step=True):
    tp = Tape(word, len(word) if head is None else head, q)
    n0 = 0
    while tp.steps < maxsteps:
        if not tp.step():
            w, rel = tp.word()
            return ('HALT', tp.q, w, rel, tp.steps, w.count('1'))
        b = is_bform(tp)
        if b is not None:
            return ('B', b[0], b[1], tp.steps)
    return ('TIMEOUT', tp.steps)

def nextb(ts, A, far=''):
    return run_to_b(bword(ts, A, far))
