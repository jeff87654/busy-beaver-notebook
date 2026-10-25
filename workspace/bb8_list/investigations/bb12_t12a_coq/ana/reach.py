"""leftmost head position of a literal event, expressed in view tokens of the input word."""
from bsim import *
from view import tokens, rle
def tok_spans(word):
    out = []; i = 0; n = len(word)
    while i < n:
        if word[i] == '0':
            j = i
            while j < n and word[j] == '0': j += 1
            out.append(('z%d' % (j-i), i, j)); i = j; continue
        j = i; m = 0
        while j + 2 < n and word[j+1] == '0' and word[j+2] == '1':
            j += 2; m += 1
        out.append((m, i, j + 1)); i = j + 1
    return out
def leftmost(word, head, q, T=TT, maxsteps=10**9):
    PAD = 1 << 14
    t = bytearray(PAD) + bytearray(int(c) for c in word) + bytearray(PAD)
    h = head + PAD; steps = 0; lo = h; first = True
    while steps < maxsteps:
        s = t[h]
        if q == 'H' and s == 0 and t[h-1] == 1 and steps > 0 and t.find(1, h) < 0:
            st, A = back_tok(t, h-1)
            if t[st-1] == 1:
                st2, m2 = back_tok(t, st-1)
                if m2 == 0: break
        tr = T[(q, s)]
        if tr is None: break
        w, d, q = tr
        t[h] = w; h += d; steps += 1
        lo = min(lo, h)
    return lo - PAD
def touched(word, head=None, q='H'):
    lo = leftmost(word, len(word) if head is None else head, q)
    sp = tok_spans(word)
    for idx, (m, a, b) in enumerate(sp):
        if a <= lo < b or lo < a:
            return lo, idx, sp
    return lo, len(sp), sp
def report(word, head=None, q='H'):
    lo, idx, sp = touched(word, head, q)
    left = rle([m for m, a, b in sp[:idx]])
    right = rle([m for m, a, b in sp[idx:]])
    return '%s  ||  %s' % (left[-60:], right[:200])
