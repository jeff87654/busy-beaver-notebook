"""Independent literal simulator for H14 / n1 / D1 (h14verify). Plain bytearray tape, no acceleration."""
import re
H14 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LN1LL_0LK1LM_1RJ1RM_1RD---'
D1  = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK1LM_1RJ1RM'
assert len(H14.split('_')) == 14 and len(D1.split('_')) == 13
N1  = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
QS = 'ABCDEFGHIJKLMN'
TR = bytes([48, 49] + [63]*254)
def parse(tm):
    T = {}
    for qi, ch in enumerate(tm.split('_')):
        for s in (0, 1):
            e = ch[3*s:3*s+3]
            T[(QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])
    return T
def D(m): return '10'*m + '1'
# FarE tail as listed in the Coq file (nearest-first, i.e. reading leftwards from the list)
FARE_NEAR = [0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,1,0,0,0,0,0,1,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,1]
def fare(k):
    """FarE k as a left-to-right string: D2^k then the tail (reversed nearest-first list)"""
    return '10101'*k + ''.join(map(str, reversed(FARE_NEAR)))
def bword(ts, A):
    """B-form word: tokens t1..tn left-to-right (ints -> D(t); strings literal), then D0 D(A)"""
    return ''.join(D(t) if isinstance(t, int) else t for t in ts) + D(0) + D(A)
class TM:
    def __init__(self, tm, word, head=None, q='H', pad=64):
        self.T = parse(tm)
        self.t = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
        self.base = pad   # tape index of word[0]
        self.h = pad + (len(word) if head is None else head)
        self.q = q; self.steps = 0
    def step(self):
        if self.h < 0:
            n = max(256, len(self.t)//2); self.t[0:0] = bytearray(n); self.h += n; self.base += n
        elif self.h >= len(self.t):
            self.t.extend(bytearray(max(256, len(self.t)//2)))
        tr = self.T[(self.q, self.t[self.h])]
        if tr is None: return False
        w, d, q = tr
        self.t[self.h] = w; self.h += d; self.q = q; self.steps += 1
        return True
    def word(self):
        s = self.t.translate(TR).decode()
        a = s.find('1'); b = s.rfind('1')
        if a < 0: return '', 0, 0
        return s[a:b+1], self.h - a, a - self.base
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
    for x in list(items) + [None]:
        if x == prev: c += 1; continue
        if prev is not None:
            s = str(prev)
            out.append(s if c == 1 else '%s^%d' % (s, c))
        prev = x; c = 1
    return ' '.join(out)
def bform(m):
    """if m is in state H with head on the blank right of the word and the word ends D0 D(A): token list"""
    if m.q != 'H': return None
    w, rel, _ = m.word()
    if rel != len(w): return None
    it = tokens(w)
    if len(it) < 2 or it[-2] != 0 or not isinstance(it[-1], int): return None
    return it
