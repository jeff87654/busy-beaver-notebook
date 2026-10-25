"""B-form level macro simulator for T12a (literal events, CLR jumps with representatives)."""
import sys
TMS = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_0RL---_0RF---'
QS = 'ABCDEFGHIJKL'
def mk(tms):
    T = {}
    for qi, ch in enumerate(tms.split('_')):
        for s in (0, 1):
            e = ch[3*s:3*s+3]
            T[(QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])
    return T
TT = mk(TMS)
def D(m): return '10'*m + '1'
FAR_TAIL = '10110101010101010010000010111100100100100100'
def fare(k): return '10101'*k + FAR_TAIL

def back_tok(t, p):
    """token ending at p (t[p]==1): returns (start, m)"""
    m = 0
    while p >= 2 and t[p-1] == 0 and t[p-2] == 1:
        m += 1; p -= 2
    return p, m

def run_lit(word, head, q, maxsteps=10**8, T=TT, stop_bform=True, skip_first=True):
    """literal run until a B-form (state H, head right of all 1s, word ends D0 D(A)).
    returns ('B', word, steps, reads) or ('HALT', ...)"""
    PAD = 1 << 12
    t = bytearray(PAD) + bytearray(int(c) for c in word) + bytearray(PAD)
    h = head + PAD; steps = 0
    reads = {}
    while steps < maxsteps:
        if h < 2:
            t[0:0] = bytearray(PAD); h += PAD
        if h >= len(t) - 2:
            t.extend(bytearray(PAD))
        s = t[h]
        if stop_bform and q == 'H' and s == 0 and t[h-1] == 1 and (steps > 0 or not skip_first):
            if t.find(1, h) < 0:
                st, A = back_tok(t, h-1)
                if t[st-1] == 1:
                    st2, m2 = back_tok(t, st-1)
                    if m2 == 0:
                        a = t.find(1)
                        return ('B', ''.join(map(str, t[a:h])), steps, reads)
        key = (q, s)
        reads[key] = reads.get(key, 0) + 1
        tr = T[key]
        if tr is None:
            a = t.find(1); b = t.rfind(1)
            return ('HALT', q + str(s), steps, ''.join(map(str, t[a:b+1])), h - a, reads)
        w, d, q = tr
        t[h] = w; h += d; steps += 1
    return ('TIMEOUT', steps)

def parse_tail(word):
    """B-form word -> (prefix_word, X_start, toks nearest-first list of (start,m)) parse all tokens from right until gap"""
    t = word
    toks = []
    p = len(t) - 1
    while p >= 0 and t[p] == '1':
        m = 0
        while p >= 2 and t[p-1] == '0' and t[p-2] == '1':
            m += 1; p -= 2
        toks.append((p, m))
        p -= 1
    return toks   # nearest first: toks[0] = A, toks[1] = D0, toks[2..] = t1, t2, ...

def fmt_word(word, maxtok=10**9):
    """render a word as far-bits | tokens (farthest-first, rle)"""
    toks = parse_tail(word)
    st = toks[-1][0]
    far = word[:st]
    ms = [m for (_, m) in toks][::-1]
    out = []; i = 0
    while i < len(ms):
        j = i
        while j < len(ms) and ms[j] == ms[i]: j += 1
        out.append(f'{ms[i]}^{j-i}' if j-i > 1 else str(ms[i])); i = j
    return far, ' '.join(out)
