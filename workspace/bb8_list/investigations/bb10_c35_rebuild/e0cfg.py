"""Base machine (E0 undefined) from a token configuration: show the configuration at the E0 read, both sides
tokenised.  python e0cfg.py "toks farthest-first incl. a b 2" """
import sys
from tokrun import start, rle
from tmlit import ST
TM8 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF'

def side_tokens(bits):
    """greedy left-to-right D-token parse (D(m) = (10)^m 1) of a bit string; junk shown raw"""
    out = []; i = 0; junk = ''
    while i < len(bits):
        if bits[i] == '1':
            j = i; m = 0
            while j + 2 < len(bits) + 0 and bits[j + 1:j + 3] == '01':
                j += 2; m += 1
            if junk: out.append('<' + junk + '>'); junk = ''
            out.append(str(m)); i = j + 1
        else:
            junk += '0'; i += 1
    if junk: out.append('<' + junk + '>')
    # compress
    res = []; k = 0
    while k < len(out):
        l = k
        while l < len(out) and out[l] == out[k]: l += 1
        res.append(out[k] + ('*%d' % (l - k) if l - k > 1 else '')); k = l
    return ' '.join(res)

def e0(toks, N=10**7):
    s = start(TM8, toks)
    while s.steps < N:
        if not s.step():
            break
    lo, hi = s.bounds()
    L = ''.join(map(str, s.tape[lo:s.pos])); R = ''.join(map(str, s.tape[s.pos + 1:hi + 1]))
    return s.steps, ST[s.last[0]] + str(s.last[1]), L, s.tape[s.pos], R

if __name__ == '__main__':
    toks = [int(x) for x in sys.argv[1].split()]
    st, sl, L, h, R = e0(toks)
    print(st, sl, '| L:', side_tokens(L), '| head', h, '| R:', side_tokens(R))
    if len(sys.argv) > 2: print(L, h, R)
