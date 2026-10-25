"""tmsim.py : small literal TM simulator for C04 with readable tape dumps.
Usage: python tmsim.py "<kt spec>" [--steps N] [--every N] [--kmom] [--E0] [--raw]
  kt spec: "tok,tok,...;m;r;t" like ktr/pkf (x*k = k copies, zN = N zeros), far prefix 11 is NOT added (give 0,0 yourself).
  --kmom : print at K-moments (state B, head on blank right end, "1001" to the left)
  --E0   : print whenever E reads 0 (the exhaustion event)
Prints: step state | tape parsed into tokens: D(x) shown as x, zeros as zN, a token run x*k; head position marked with [q>.
"""
import sys
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
TR = {}
for s, grp in enumerate(M.split('_')):
    for c in range(2):
        x = grp[3 * c:3 * c + 3]
        TR[(s, c)] = None if x[0] == '-' else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)

def build(spec):
    f = spec.split(';')
    w = []
    if f[0]:
        for it in f[0].split(','):
            rep = 1
            if '*' in it: it, rep = it.split('*'); rep = int(rep)
            if it[0] == 'z': w += [0] * (int(it[1:]) * rep)
            else:
                d = int(it)
                for _ in range(rep): w += [1, 0] * d + [1]
    m, r, t = int(f[1]), int(f[2]), int(f[3])
    w += [1, 0] * m + [1] + [1, 0] * r + [1, 1] + [1, 1, 1, 1, 1, 1, 0, 0] * t + [1, 0, 0, 1]
    return w

def parse(tape, lo, hi, head):
    """token view of tape[lo..hi]; returns string with head marker"""
    out = []; i = lo
    while i <= hi:
        if i == head: out.append('^')
        if tape[i] == 0:
            j = i
            while j <= hi and tape[j] == 0 and j != head: j += 1
            if j == i: j = i + 1
            out.append('z%d' % (j - i) if j - i > 1 else 'z'); i = j; continue
        # token (10)^x 1
        j = i; x = 0
        while j + 2 <= hi and tape[j] == 1 and tape[j + 1] == 0 and tape[j + 2] == 1 and head not in (j + 1, j + 2): j += 2; x += 1
        if tape[j] == 1 and j <= hi: out.append(str(x)); i = j + 1
        else: out.append('1'); i = i + 1
    # run-length
    res = []; k = 0
    while k < len(out):
        l = k
        while l < len(out) and out[l] == out[k]: l += 1
        res.append(out[k] + ('*%d' % (l - k) if l - k > 1 else '')); k = l
    return ' '.join(res)

def rle(bits):
    """compress a 0/1 string: repeated substrings of period 1..8 become (pat)^k when k>=3 and k*p>=6"""
    s = ''.join(map(str, bits)); out = []; i = 0; n = len(s)
    while i < n:
        best = None
        for p in range(1, 9):
            if i + p > n: break
            pat = s[i:i + p]; k = 1
            while s[i + k * p:i + (k + 1) * p] == pat: k += 1
            if k >= 3 and k * p >= 6 and (best is None or k * p > best[0] * best[1]): best = (k, p)
        if best:
            k, p = best; out.append('(%s)^%d' % (s[i:i + p], k)); i += k * p
        else: out.append(s[i]); i += 1
    # merge adjacent single bits
    res = []
    for x in out:
        if len(x) == 1 and res and len(res[-1]) and res[-1][0] != '(' : res[-1] += x
        else: res.append(x)
    return ' '.join(res)

def run(spec, steps=10**7, every=0, kmom=False, e0=False, raw=False, q0=1):
    w = build(spec)
    pad = 64
    tape = [0] * pad + w + [0] * pad
    head = pad + len(w); q = q0
    lo = pad; hi = pad + len(w) - 1
    st = 0
    def dump(tag):
        a, b = lo, max(hi, head)
        if raw: s = rle(tape[a:head]) + ' [' + chr(65 + q) + '> ' + rle(tape[head:b + 1])
        else: s = parse(tape, a, b, head) + '  [%s>' % chr(65 + q)
        print('%s step=%d %s' % (tag, st, s), flush=True)
    while st < steps:
        if head < 2 or head > len(tape) - 3:
            ext = len(tape)
            tape = [0] * ext + tape + [0] * ext; head += ext; lo += ext; hi += ext
        c = tape[head]
        if kmom and q == 1 and c == 0 and tape[head - 4:head] == [1, 0, 0, 1] and all(x == 0 for x in tape[head:hi + 1]):
            dump('K')
        if e0 and q == 4 and c == 0: dump('E0')
        tr = TR[(q, c)]
        if tr is None:
            dump('HALT %s%d' % (chr(65 + q), c)); return
        tape[head] = tr[0]; head += tr[1]; q = tr[2]; st += 1
        lo = min(lo, head); hi = max(hi, head)
        if every and st % every == 0: dump('S')
    dump('STOP')

if __name__ == '__main__':
    a = sys.argv[1:]
    spec = a[0]; kw = {}
    i = 1
    while i < len(a):
        if a[i] == '--steps': kw['steps'] = int(float(a[i + 1])); i += 2
        elif a[i] == '--every': kw['every'] = int(a[i + 1]); i += 2
        elif a[i] == '--kmom': kw['kmom'] = True; i += 1
        elif a[i] == '--E0': kw['e0'] = True; i += 1
        elif a[i] == '--raw': kw['raw'] = True; i += 1
        else: raise SystemExit('bad arg ' + a[i])
    run(spec, **kw)
